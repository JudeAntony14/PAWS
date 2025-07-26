import os
import shutil
import re
import requests
from pathlib import Path
import logging
from datetime import datetime
from db_utils import DatabaseManager
import sqlite3

class QuotationProcessor:
    def __init__(self):
        # API Configuration
        self.API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        self.headers = {
            "Authorization": "Bearer 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"
        }

        # Directory paths
        self.source_dir = Path("C:/SupplierEmail")
        self.processed_rfqs_dir = Path("C:/Users/judea/OneDrive/Desktop/ProcessedRFQs")
        self.unidentified_quotes_dir = Path("C:/Users/judea/OneDrive/Desktop/ProcessedQuotations/UnidentifiedQuotes")
        self.db = DatabaseManager()
        
        # Ensure directories exist
        self.unidentified_quotes_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename='quotation_processor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def extract_body(self, email_text):
        """Extracts only the email body from the full email content."""
        parts = email_text.split("\n\nBody:\n", 1)
        return parts[1] if len(parts) > 1 else email_text

    def query_huggingface(self, text):
        """Query the Hugging Face API to classify the text."""
        email_body = self.extract_body(text)
        
        payload = {
            "inputs": email_body,
            "parameters": {
                "candidate_labels": [
                    "quotation",
                    "price proposal",
                    "supplier quote",
                    "other communication"
                ]
            }
        }

        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"API Response for text: {email_body[:100]}... -> {result}")

            max_score_index = result['scores'].index(max(result['scores']))
            label = result['labels'][max_score_index]
            score = result['scores'][max_score_index]

            is_quotation = label != "other communication" and score > 0.35
            
            return is_quotation

        except Exception as e:
            self.logger.error(f"API query failed: {str(e)}")
            return False

    def get_next_sq_number(self):
        """Generate the next sequential SQ number."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT MAX(supplier_quote) FROM rfq_cases WHERE supplier_quote LIKE "SQ%"')
                result = cursor.fetchone()[0]
                
                if result:
                    last_number = int(result[2:])  # Extract number from 'SQ0001'
                    next_number = last_number + 1
                else:
                    next_number = 1
                    
                return f"SQ{str(next_number).zfill(4)}"
        except Exception as e:
            self.logger.error(f"Error generating SQ number: {str(e)}")
            return None

    def get_related_attachments(self, email_number):
        """Find all attachment files related to an email number."""
        pattern = f"SupplierEmailAttachment\\(\\d+\\){email_number}"
        return [file for file in self.source_dir.glob(f"*{email_number}*") 
                if re.match(pattern, file.name)]

    def process_emails(self):
        """Process all email files in the source directory."""
        try:
            email_files = [f for f in self.source_dir.glob("SupplierEmail[0-9]*") if not "Attachment" in f.name]
            self.logger.info(f"Found {len(email_files)} email files to process")

            for email_file in email_files:
                try:
                    with open(email_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract subject line from email content
                    subject_match = re.search(r"^Subject:\s*(.+)", content, re.MULTILINE)
                    subject_line = subject_match.group(1) if subject_match else ""
                    
                    if self.query_huggingface(content):
                        self.process_supplier_email(email_file, subject_line)
                    else:
                        self.logger.info(f"Not a Supplier Quotation: {email_file.name}")
                
                except Exception as e:
                    self.logger.error(f"Error processing {email_file.name}: {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error in process_emails: {str(e)}")

    def extract_reference_numbers(self, subject):
        """
        Extract up to 3 reference numbers from subject line.
        Pattern: Letters + (space/period/both) + minimum 4 digits
        """
        pattern = r"[A-Za-z]+[\s\.]{0,2}\d{4,}"
        matches = re.finditer(pattern, subject, re.IGNORECASE)
        return [match.group(0) for match in matches][:3]  # Take first 3 matches only

    def is_our_rfq(self, ref_num):
        """Check if number matches our RFQ format."""
        return bool(re.match(r"R\d{4,}", ref_num))

    def process_supplier_email(self, email_file, subject_line):
        try:
            ref_numbers = self.extract_reference_numbers(subject_line)
            self.logger.info(f"Found reference numbers: {ref_numbers}")
            
            our_rfq = None
            client_rfq = None
            supplier_quote = None

            # Check each reference number against database
            for ref in ref_numbers:
                clean_ref = re.sub(r'[\s\.]', '', ref)
                
                if self.is_our_rfq(clean_ref):
                    case = self.db.get_case_by_our_rfq(clean_ref)
                    if case:
                        our_rfq = clean_ref
                        client_rfq = case[0]
                        continue
                
                case = self.db.get_case_by_client_rfq(clean_ref)
                if case:
                    client_rfq = clean_ref
                    our_rfq = case[0]
                    continue
                
                if not supplier_quote:
                    supplier_quote = clean_ref

            # If no supplier quote found, generate one
            if not supplier_quote:
                supplier_quote = self.get_next_sq_number()

            # Get attachments before moving files
            email_number = re.search(r'\d+$', email_file.stem).group()
            attachments = self.get_related_attachments(email_number)

            # Always save to ProcessedQuotations
            self.save_to_quotations_folder(email_file, attachments, supplier_quote)

            if client_rfq:
                # Also save to RFQ folder and update database
                self.save_to_rfq_folder(email_file, attachments, client_rfq, supplier_quote)
                self.db.update_supplier_quote(client_rfq, supplier_quote)
                
                # Update progress file in ProcessedRFQs folder
                rfq_folder = self.processed_rfqs_dir / client_rfq
                progress_file = rfq_folder / f"{client_rfq}_progress.txt"
                if progress_file.exists():
                    with open(progress_file, 'a', encoding='utf-8') as f:
                        f.write(f"\nSupplier quoted - {supplier_quote} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                self.logger.info(f"Processed quote {supplier_quote} for RFQ {client_rfq}")
            else:
                self.logger.info(f"Saved unidentified quote: {supplier_quote}")

            # Move original files from source directory
            self.move_from_source(email_file, attachments)

        except Exception as e:
            self.logger.error(f"Error processing supplier email {email_file}: {str(e)}")

    def save_to_quotations_folder(self, email_file, attachments, supplier_quote):
        """Save supplier quote to ProcessedQuotations folder."""
        try:
            quote_folder = Path("C:/Users/judea/OneDrive/Desktop/ProcessedQuotations") / supplier_quote
            quote_folder.mkdir(exist_ok=True)
            attachments_folder = quote_folder / "attachments"
            attachments_folder.mkdir(exist_ok=True)

            # Copy email
            shutil.copy2(email_file, quote_folder / f"{supplier_quote}.txt")

            # Copy attachments
            for idx, attachment in enumerate(attachments, 1):
                new_name = f"{supplier_quote}_Attachment({idx}){attachment.suffix}"
                shutil.copy2(attachment, attachments_folder / new_name)

            return True

        except Exception as e:
            self.logger.error(f"Error saving to quotations folder: {str(e)}")
            return False

    def save_to_rfq_folder(self, email_file, attachments, client_rfq, supplier_quote):
        """Save supplier quote to the correct RFQ folder."""
        try:
            rfq_folder = self.processed_rfqs_dir / client_rfq
            if not rfq_folder.exists():
                self.logger.error(f"RFQ folder not found: {client_rfq}")
                return False

            supplier_folder = rfq_folder / "SupplierAttachments"
            supplier_folder.mkdir(exist_ok=True)

            # Copy email with supplier quote number
            shutil.copy2(email_file, rfq_folder / f"{supplier_quote}.txt")

            # Copy attachments
            for idx, attachment in enumerate(attachments, 1):
                new_name = f"{supplier_quote}_Attachment({idx}){attachment.suffix}"
                shutil.copy2(attachment, supplier_folder / new_name)

            return True

        except Exception as e:
            self.logger.error(f"Error saving to RFQ folder: {str(e)}")
            return False

    def move_from_source(self, email_file, attachments):
        """Move original files from source directory."""
        try:
            # Move email file
            email_file.unlink()
            
            # Move attachments
            for attachment in attachments:
                attachment.unlink()
            
            self.logger.info(f"Removed original files from source directory")
            return True
        
        except Exception as e:
            self.logger.error(f"Error moving files from source: {str(e)}")
            return False

def main():
    processor = QuotationProcessor()
    processor.process_emails()

if __name__ == "__main__":
    main()
