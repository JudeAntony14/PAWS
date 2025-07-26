import os
import shutil
import re
import requests
from pathlib import Path
import logging
from datetime import datetime
from db_utils import DatabaseManager
#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

class RFQsProcessor:
    def __init__(self):
        # API Configuration
        self.API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        self.headers = {"Authorization": "Bearer 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"}

        # Directory paths
        self.source_dir = Path("C:/ClientEmail")
        self.target_dir = Path("C:/Users/judea/OneDrive/Desktop/ProcessedRFQs")
        self.cases_dir = Path("C:/Users/judea/OneDrive/Desktop/Cases")
        
        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.cases_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger('RFQsProcessor')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('rfq_processor.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handler if it doesn't exist
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # Database Manager
        self.db = DatabaseManager()

    def sanitize_folder_name(self, name):
        """Sanitize folder names by removing invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def extract_rfq_number(self, subject_line):
        """
        Extracts an RFQ number from the subject line.
        The RFQ number is defined as a sequence of letters followed by up to 2 optional characters 
        (spaces, periods, or hyphens) and then a minimum of 4 digits.
        For example, 'DOSQU18291', 'Req.18210', or 'Req 18210' will be matched.
        Returns the matched string (with spaces removed) if found, otherwise None.
        """
        pattern = r"\b[A-Za-z]+[\s\.\-]{0,2}\d{4,}\b"
        match = re.search(pattern, subject_line)
        if match:
            return match.group(0).replace(" ", "")
        return None

    def extract_email_metadata(self, email_text):
        """Extracts the subject line from the email text for naming purposes."""
        match = re.search(r"^Subject:\s*(.+)", email_text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Unknown_Subject"

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
                "candidate_labels": ["request for quotation", "price inquiry", "quote request", "other communication"]
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

            is_rfq = label != "other communication" and score > 0.35
            return is_rfq

        except Exception as e:
            self.logger.error(f"API query failed: {str(e)}")
            return False

    def get_related_attachments(self, email_number):
        """Find all attachment files related to an email number."""
        pattern = f"ClientEmailAttachment\\(\\d+\\){email_number}"
        return [file for file in self.source_dir.glob(f"*{email_number}*") if re.match(pattern, file.name)]

    def create_case_file(self, client_rfq, subject_line):
        """Create a new case file with the current date and increment counter."""
        try:
            today = datetime.now().strftime("%d-%m-%Y")
            
            # Get existing case files for today
            existing_files = list(self.cases_dir.glob(f"{today}--*"))
                                                                
            # Determine next counter number
            if existing_files:
                latest_counter = max(int(f.stem.split('--')[1]) for f in existing_files)
                counter = str(latest_counter + 1).zfill(3)
            else:
                counter = "001"
            
            case_filename = f"{today}--{counter}.txt"
            case_file = self.cases_dir / case_filename
            
            # Write initial case information
            with open(case_file, 'w', encoding='utf-8') as f:
                if client_rfq:
                    f.write(f"Client RFQ Number - {client_rfq}\n")
                else:
                    f.write(f"Client RFQ Number - {subject_line}\n")
                f.write("Our RFQ Number - \n")
                f.write("Supplier Quote Number - \n")
                f.write("Our Quote Number - \n")
                f.write("PO Number - \n")
                f.write("Delivery Tracking Number - \n")
            
            self.logger.info(f"Created case file: {case_filename}")
            return case_file
        
        except Exception as e:
            self.logger.error(f"Error creating case file: {str(e)}")
            return None

    def move_files(self, email_file, attachments, subject_line):
        """Move email and its attachments to the processed directory."""
        try:
            rfq_number = self.extract_rfq_number(subject_line)
            if rfq_number:
                # Store the original RFQ number for database insertion
                original_rfq = rfq_number
                # Use sanitized version only for folder names
                folder_name = self.sanitize_folder_name(rfq_number)
            else:
                original_rfq = folder_name = self.sanitize_folder_name(subject_line.strip().replace(" ", "_")[:50])

            # Create target folders
            target_folder = self.target_dir / folder_name
            attachments_folder = target_folder / "attachments"
            progress_file = target_folder / f"{folder_name}_progress.txt"

            target_folder.mkdir(exist_ok=True)
            attachments_folder.mkdir(exist_ok=True)

            # First move the files
            shutil.move(str(email_file), str(target_folder / f"{folder_name}.txt"))
            self.logger.info(f"Moved email file: {folder_name}.txt -> {target_folder}")

            # Move attachments and rename them accordingly
            for index, attachment in enumerate(attachments, start=1):
                new_attachment_name = f"{folder_name}_Attachment({index}){attachment.suffix}"
                shutil.move(str(attachment), str(attachments_folder / new_attachment_name))
                self.logger.info(f"Moved attachment: {new_attachment_name} -> {attachments_folder}")

            # Create case file
            with open(progress_file, 'w', encoding='utf-8') as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"Classified as an RFQ at {now}\n")
                f.write(f"Email subject: {subject_line}\n")

            # After moving files, try to insert into database using original RFQ number
            try:
                self.db.insert_rfq_case(client_rfq=original_rfq)
            except Exception as db_error:
                self.logger.error(f"Database error (non-critical): {str(db_error)}")
            
            return True

        except Exception as e:
            self.logger.error(f"Error moving files: {str(e)}")
            return False

    def process_emails(self):
        """Process all email files in the source directory."""
        try:
            email_files = [f for f in self.source_dir.glob("ClientEmail[0-9]*") if "Attachment" not in f.name]
            self.logger.info(f"Found {len(email_files)} email files to process")

            for email_file in email_files:
                try:
                    email_number = re.search(r'\d+$', email_file.stem).group()

                    with open(email_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    subject_line = self.extract_email_metadata(content)
                    if self.query_huggingface(content):
                        attachments = self.get_related_attachments(email_number)

                        if self.move_files(email_file, attachments, subject_line):
                            self.logger.info(f"Successfully processed RFQ: {email_file.name}")
                        else:
                            self.logger.error(f"Failed to process RFQ: {email_file.name}")
                    else:
                        self.logger.info(f"Not an RFQ: {email_file.name}")

                except Exception as e:
                    self.logger.error(f"Error processing {email_file.name}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in process_emails: {str(e)}")

def main():
    processor = RFQsProcessor()
    processor.process_emails()

if __name__ == "__main__":
    main()
