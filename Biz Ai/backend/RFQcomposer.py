import os
from pathlib import Path
import re
import shutil
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from imapclient import IMAPClient
from db_utils import DatabaseManager
import sqlite3

class RFQComposer:
    def __init__(self):
        # Directory paths
        self.source_dir = Path("C:/Users/judea/OneDrive/Desktop/ProcessedRFQs")
        self.drafts_dir = Path("C:/Users/judea/OneDrive/Desktop/RFQDrafts")
        self.cases_dir = Path("C:/Users/judea/OneDrive/Desktop/Cases")
        
        # Setup logging first, before any operations
        self.logger = logging.getLogger('RFQComposer')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('rfq_composer.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handler if it doesn't exist
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        
        # Load the current RFQ number from a file
        self.current_rfq_number = self.load_current_rfq_number() or 8790
        
        # Email configuration
        self.recipient = "artisticgems.nfts@gmail.com"
        self.sender = "cooliekid000@gmail.com"
        self.password = "uifi lusy ovgp srpv"
        
        # Ensure drafts directory exists
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Path to processed RFQs tracking file
        self.processed_rfqs_file = Path('clientRFQnumbers.txt')
        # Create the tracking file if it doesn't exist
        if not self.processed_rfqs_file.exists():
            with open(self.processed_rfqs_file, 'w'):
                pass

    def load_current_rfq_number(self):
        """Load the current RFQ number from a file."""
        try:
            # Use Path for proper path handling
            file_path = Path('current_rfq_number.txt')
            if not file_path.exists():
                return None
            with open(file_path, 'r') as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"Error loading current RFQ number: {str(e)}")
            return None

    def save_current_rfq_number(self):
        """Save the current RFQ number to a file."""
        try:
            # Use Path for proper path handling
            file_path = Path('current_rfq_number.txt')
            with open(file_path, 'w') as f:
                f.write(str(self.current_rfq_number))
        except Exception as e:
            self.logger.error(f"Error saving current RFQ number: {str(e)}")

    def connect_to_gmail(self):
        """Connect to Gmail using SMTP and IMAP."""
        try:
            # SMTP connection for sending drafts
            self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
            self.smtp.starttls()
            self.smtp.login(self.sender, self.password)

            # IMAP connection for saving to drafts folder
            self.imap = IMAPClient('imap.gmail.com', ssl=True)
            self.imap.login(self.sender, self.password)
            
            self.logger.info("Successfully connected to Gmail")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail: {str(e)}")
            return False

    def create_email_draft(self, subject, body, attachments=None):
        """Create and save email draft in Gmail."""
        try:
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = self.recipient
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    with open(attachment, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=attachment.name)
                    part['Content-Disposition'] = f'attachment; filename="{attachment.name}"'
                    msg.attach(part)

            # Convert to string
            email_str = msg.as_string()

            # Save to Gmail drafts
            self.imap.append('[Gmail]/Drafts', email_str, flags=['\\Draft'])
            
            self.logger.info(f"Created draft email with subject: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create draft: {str(e)}")
            return False

    def extract_client_rfq_number(self, folder_name):
        """Extract RFQ number if it matches the expected pattern."""
        # Pattern to match letter sequence followed by numbers
        pattern = r"[A-Za-z]+\d{3,}"
        match = re.match(pattern, folder_name)
        return match.group(0) if match else None

    def get_email_body(self, folder_path):
        """Extract email body from the email file."""
        try:
            # Find the email file in the folder
            email_file = next(folder_path.glob("*.txt"))
            
            with open(email_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract everything after "Body:"
            if "Body:" in content:
                body = content.split("Body:", 1)[1].strip()
                return body
            else:
                self.logger.error(f"No 'Body:' marker found in {email_file}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error extracting email body: {str(e)}")
            return ""

    def get_attachments(self, folder_path):
        """Get list of attachments from the attachments subfolder."""
        attachments_dir = folder_path / "attachments"
        if attachments_dir.exists():
            return list(attachments_dir.glob("*.*"))
        return []

    def update_case_file(self, folder_path, our_rfq):
        """Update the case file with our RFQ number."""
        try:
            # Find the case file reference in the progress file
            progress_file = next(folder_path.glob("*_progress.txt"))
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
                case_file_match = re.search(r"Case file: (.+\.txt)", content)
            
            if case_file_match:
                case_filename = case_file_match.group(1)
                case_file = self.cases_dir / case_filename
                
                if case_file.exists():
                    # Read existing content
                    with open(case_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Update Our RFQ Number line
                    for i, line in enumerate(lines):
                        if line.startswith("Our RFQ Number"):
                            lines[i] = f"Our RFQ Number - {our_rfq}\n"
                            break
                    
                    # Write updated content
                    with open(case_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                        
                    self.logger.info(f"Updated case file {case_filename} with RFQ number {our_rfq}")
                    
        except Exception as e:
            self.logger.error(f"Error updating case file: {str(e)}")

    def is_rfq_already_processed(self, client_rfq):
        """Check if this RFQ has already been processed by looking at the tracking file or database."""
        try:
            # First check if it's in our tracking file
            if self.processed_rfqs_file.exists():
                with open(self.processed_rfqs_file, 'r') as f:
                    processed_rfqs = f.read().splitlines()
                    if client_rfq in processed_rfqs:
                        return True
            
            # Also check if it already has our_rfq assigned in the database
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT our_rfq FROM rfq_cases WHERE client_rfq = ?', (client_rfq,))
                result = cursor.fetchone()
                if result and result[0]:  # If it has our_rfq assigned
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if RFQ is already processed: {str(e)}")
            # If there's an error, assume not processed to be safe
            return False
            
    def mark_rfq_as_processed(self, client_rfq):
        """Mark an RFQ as processed by adding it to the tracking file."""
        try:
            with open(self.processed_rfqs_file, 'a') as f:
                f.write(f"{client_rfq}\n")
            return True
        except Exception as e:
            self.logger.error(f"Error marking RFQ as processed: {str(e)}")
            return False

    def compose_draft(self, folder_path):
        """Compose a draft email for a single RFQ folder and save both locally and in Gmail."""
        try:
            folder_name = folder_path.name
            
            # Check if this RFQ has already been processed
            if self.is_rfq_already_processed(folder_name):
                self.logger.info(f"RFQ {folder_name} has already been processed. Skipping.")
                return True
                
            # If this is a new RFQ, generate our RFQ number
            our_rfq = self.generate_rfq_number()
            
            # Get the original client RFQ from the database
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT client_rfq FROM rfq_cases WHERE client_rfq LIKE ?', 
                             (folder_name.replace('_', '%'),))
                result = cursor.fetchone()
                client_rfq = result[0] if result else folder_name

            # Update database with our RFQ number
            if client_rfq:
                self.db.update_our_rfq(client_rfq, our_rfq)
            
            # Update progress file with RFQ number assignment
            progress_file = folder_path / f"{folder_name}_progress.txt"
            if progress_file.exists():
                with open(progress_file, 'a', encoding='utf-8') as f:
                    f.write(f"\nRFQ number {our_rfq} assigned at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Compose subject line using original client RFQ
            subject = f"{our_rfq}----Inquiry"
            if client_rfq:
                subject = f"{our_rfq}----Inquiry----{client_rfq}"
            
            # Get email body and attachments
            body = self.get_email_body(folder_path)
            attachments = self.get_attachments(folder_path)
            
            # Create local draft folder and save
            draft_folder = self.drafts_dir / our_rfq
            draft_folder.mkdir(exist_ok=True)
            
            # Save locally
            draft_file = draft_folder / f"{our_rfq}_draft.txt"
            with open(draft_file, 'w', encoding='utf-8') as f:
                f.write(f"To: {self.recipient}\n")
                f.write(f"Subject: {subject}\n")
                f.write("\nBody:\n")
                f.write(body)
                
                if attachments:
                    f.write("\n\nAttachments:\n")
                    for att in attachments:
                        f.write(f"- {att.name}\n")
            
            # Copy attachments to local draft folder
            if attachments:
                draft_attachments = draft_folder / "attachments"
                draft_attachments.mkdir(exist_ok=True)
                for attachment in attachments:
                    shutil.copy2(attachment, draft_attachments / attachment.name)

            # Create Gmail draft
            if self.create_email_draft(subject, body, attachments):
                self.logger.info(f"Created draft in Gmail for {our_rfq}")
            
            # Update case file with our RFQ number
            self.update_case_file(folder_path, our_rfq)
            
            # Mark this RFQ as processed to avoid duplicate processing
            self.mark_rfq_as_processed(folder_name)
            
            self.save_current_rfq_number()  # Save the current RFQ number after processing
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error composing draft for {folder_path}: {str(e)}")
            return False

    def process_all_rfqs(self):
        """Process all RFQ folders in the source directory."""
        try:
            if not self.connect_to_gmail():
                self.logger.error("Failed to connect to Gmail. Aborting process.")
                return

            # Get all subfolders in ProcessedRFQs
            rfq_folders = [f for f in self.source_dir.iterdir() if f.is_dir()]
            self.logger.info(f"Found {len(rfq_folders)} RFQ folders to process")
            
            for folder in rfq_folders:
                if self.compose_draft(folder):
                    self.logger.info(f"Successfully processed RFQ folder: {folder.name}")
                else:
                    self.logger.error(f"Failed to process RFQ folder: {folder.name}")
                    
            # Clean up connections
            self.smtp.quit()
            self.imap.logout()
                    
        except Exception as e:
            self.logger.error(f"Error in process_all_rfqs: {str(e)}")

    def generate_rfq_number(self):
        """Generate a new RFQ number and save it."""
        try:
            self.current_rfq_number += 1
            # Save the new number
            with open('current_rfq_number.txt', 'w') as f:
                f.write(str(self.current_rfq_number))
            # Return formatted number with L prefix
            return f"L{self.current_rfq_number}"
        except Exception as e:
            self.logger.error(f"Error generating RFQ number: {str(e)}")
            return None

def main():
    composer = RFQComposer()
    composer.process_all_rfqs()

if __name__ == "__main__":
    main() 

