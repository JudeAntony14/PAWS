'''
This script defines a class, EmailExtractor, which automates the extraction and organization of emails from a Gmail 
account using the IMAP protocol. The main functionalities include:

Login and Initialization:

Logs into the Gmail account using credentials.
Initializes directories for saving email content (general) and attachments (attachments).

Email Parsing:

Retrieves the last 10 emails from the inbox, extracts metadata (sender, subject), text content, and attachments.
Emails and attachments are saved locally with sequential naming conventions (e.g., RFQ_0001.txt).
Attachment Handling:

Saves attachments with distinct filenames and extensions in the designated folder.
Continuous Monitoring:

The script runs indefinitely, checking for new emails every 5 seconds. It avoids reprocessing emails by storing previously 
parsed email IDs.
Structured Email Storage:

Email data is organized in .txt files, separating headers and body content for easy reference.
'''


import os
import email
from imapclient import IMAPClient
import time
import shutil
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import threading

#bchw lemr nybb mvpf
# for the tester judealiju@gmail.com

# ICP logging helper (minimal, non-blocking)
def icp_log_message(message):
    try:
        from ic.client import Client
        from ic.identity import Identity
        from ic.agent import Agent
        from ic.candid import Types, encode
        import asyncio

        async def send_log():
            # Update these with your canister/principal info
            canister_id = "<YOUR_CANISTER_ID>"  # Replace after deploy
            url = "http://127.0.0.1:4943"  # Local replica
            agent = Agent(
                identity=Identity.anonymous(),
                url=url
            )
            await agent.fetch_root_key()
            arg = encode([Types.Text], [message])
            await agent.update_raw(canister_id, "record", arg)

        # Run in background thread to not block email processing
        threading.Thread(target=lambda: asyncio.run(send_log()), daemon=True).start()
    except Exception as e:
        print(f"[ICP LOGGING ERROR] {e}")


class GMAIL_EXTRACTOR():
    def __init__(self):
        self.initializeVariables()

    def initializeVariables(self):
        self.usr = "cooliekid000@gmail.com"
        self.pwd = "uifi lusy ovgp srpv"
        self.mail = None
        self.mailbox = ""
        self.parsed_message_ids = set()  # To track processed emails
        
        # Counters for each category for sequential file naming.
        self.client_counter = 1
        self.supplier_counter = 1
        self.bank_counter = 1
        self.unknown_counter = 1

    def helloWorld(self):
        print("\nWelcome to Gmail extractor,\ndeveloped by Jude.")

    def attemptLogin(self):
        try:
            self.mail = IMAPClient("imap.gmail.com", ssl=True)
            self.mail.login(self.usr, self.pwd)
            print("\nLogon SUCCESSFUL")
            return True
        except Exception as e:
            print(f"\nLogon FAILED: {e}")
            return False

    def selectMailbox(self):
        try:
            self.mailbox = "INBOX"
            self.mail.select_folder(self.mailbox)
            print(f"Mailbox '{self.mailbox}' selected.")
            return True
        except Exception as e:
            print(f"Failed to select mailbox '{self.mailbox}': {e}")
            return False

    def getCategory(self, sender_email):
        sender_email = sender_email.lower() if sender_email else ""
        if sender_email in (email.lower() for email in self.CLIENT_EMAILS):
            return 'client'
        elif sender_email in (email.lower() for email in self.SUPPLIER_EMAILS):
            return 'supplier'
        elif sender_email in (email.lower() for email in self.BANK_EMAILS):
            return 'bank'
        else:
            return 'unknown'

    def getCategoryCounterAndIncrement(self, category):
        if category == 'client':
            count = self.client_counter
            self.client_counter += 1
        elif category == 'supplier':
            count = self.supplier_counter
            self.supplier_counter += 1
        elif category == 'bank':
            count = self.bank_counter
            self.bank_counter += 1
        else:
            count = self.unknown_counter
            self.unknown_counter += 1
        return count

    def getFolderForCategory(self, category):
        return self.EMAIL_FOLDERS.get(category, r'C:\NewEmail')

    def processEmail(self, uid):
        try:
            raw_message = self.mail.fetch([uid], ['RFC822', 'BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)]'])
            msg = email.message_from_bytes(raw_message[uid][b'RFC822'])
            message_id = raw_message[uid][b'BODY[HEADER.FIELDS (MESSAGE-ID)]'].decode('utf-8').strip()

            if message_id in self.parsed_message_ids:
                print(f"Email with Message-Id '{message_id}' already parsed. Skipping.")
                return

            sender_full = msg.get("From")
            subject = msg.get("Subject")
            date = msg.get("Date")
            body = None

            sender_name = ""
            sender_email = sender_full
            if sender_full and "<" in sender_full and ">" in sender_full:
                parts = sender_full.split("<")
                sender_name = parts[0].strip()
                sender_email = parts[1].strip(">").strip()

            attachments = []
            for part in msg.walk():
                content_type = part.get_content_type()
                filename = part.get_filename()
                if filename:
                    attachments.append((filename, part.get_payload(decode=True)))
                elif content_type == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")

            category = self.getCategory(sender_email)
            dest_folder = self.getFolderForCategory(category)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            seq = self.getCategoryCounterAndIncrement(category)
            seq_str = f"{seq:04d}"

            if category == 'client':
                txt_filename = f"ClientEmail{seq_str}.txt"
            elif category == 'supplier':
                txt_filename = f"SupplierEmail{seq_str}.txt"
            elif category == 'bank':
                txt_filename = f"BankEmail{seq_str}.txt"
            else:
                txt_filename = f"NewEmail{seq_str}.txt"

            txt_filepath = os.path.join(dest_folder, txt_filename)
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(f"From: <{sender_email}>\n")
                f.write(f"Name: {sender_name}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Date: {date}\n\n")
                f.write("Body:\n")
                f.write(body if body else "No body content available.\n")

            print(f"Email saved as {txt_filename} in {dest_folder}")

            # Log to ICP canister (non-blocking, minimal)
            icp_log_message(f"Processed Email ID: {message_id}")

            attachment_index = 1
            for orig_filename, file_data in attachments:
                ext = os.path.splitext(orig_filename)[-1]
                attachment_filename = f"{category.capitalize()}EmailAttachment({attachment_index}){seq_str}{ext}"
                attachment_path = os.path.join(dest_folder, attachment_filename)
                with open(attachment_path, 'wb') as f:
                    f.write(file_data)
                print(f"Attachment saved as {attachment_filename} in {dest_folder}")
                attachment_index += 1

            self.parsed_message_ids.add(message_id)

        except Exception as e:
            print(f"Error processing email: {e}")

    def parseLast10Emails(self):
        try:
            self.mail.select_folder(self.mailbox)
            messages = self.mail.search(['ALL'])
            last_10_uids = messages[-10:]
            for uid in last_10_uids:
                self.processEmail(uid)
        except Exception as e:
            print(f"Error fetching or processing last 10 emails: {e}")

    def checkNewEmails(self):
        try:
            self.mail.select_folder(self.mailbox)
            messages = self.mail.search(['ALL'])
            last_10_uids = messages[-10:]
            found_new_email = False
            for uid in last_10_uids:
                raw_message = self.mail.fetch([uid], ['BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)]'])
                message_id = raw_message[uid][b'BODY[HEADER.FIELDS (MESSAGE-ID)]'].decode('utf-8').strip()
                if message_id not in self.parsed_message_ids:
                    self.processEmail(uid)
                    found_new_email = True
            if not found_new_email:
                pass
        except Exception as e:
            print(f"Error checking for new emails: {e}")

    def run(self):
        self.helloWorld()
        if self.attemptLogin() and self.selectMailbox():
            try:
                self.parseLast10Emails()
                print("Parsed the last 10 emails.")
                while True:
                    self.checkNewEmails()
                    time.sleep(5)
            except KeyboardInterrupt:
                print("\nProgram stopped.")

if __name__ == "__main__":
    CLIENT_EMAILS = [
        'judealiju@gmail.com',
        'jude.chirayathu@gmail.com'
    ]
    SUPPLIER_EMAILS = [
        'artisticgems.nfts@gmail.com',
        'ejcorporations@gmail.com'
    ]
    BANK_EMAILS = [
        'spamvp3785@gmail.com',
        'eldjubsnss1122@gmail.com'
    ]
    EMAIL_FOLDERS = {
        'client': r'C:\ClientEmail',
        'supplier': r'C:\SupplierEmail',
        'bank': r'C:\BankEmail',
        'unknown': r'C:\NewEmail'
    }

    extractor = GMAIL_EXTRACTOR()
    extractor.CLIENT_EMAILS = CLIENT_EMAILS
    extractor.SUPPLIER_EMAILS = SUPPLIER_EMAILS
    extractor.BANK_EMAILS = BANK_EMAILS
    extractor.EMAIL_FOLDERS = EMAIL_FOLDERS

    extractor.run()


#"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"