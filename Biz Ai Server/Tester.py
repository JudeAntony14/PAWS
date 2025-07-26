import smtplib
import os
import random
import time
from email.message import EmailMessage

# Email Credentials
EMAIL_ADDRESS = "example@gmail.com"
EMAIL_PASSWORD = ""

# Path to RFQ attachments
ATTACHMENTS_FOLDER = r"C:\Users\judea\OneDrive\Desktop\GpayIcons"

# Email Content Options
subjects = [
    "RFQ {} {}", "{} {}", "Requisition {}", "Need items {}"
]
salutations = ["Dear Team,", "Dear Roy,", "Roy,", "V2,", "Dear V2,"]
products = [
    "Seawater Pump", "Saltwater Pump", "Alweiser Pump", "LED TV",
    "Chairs", "Tables", "Laptops", "Sneakers", "Steel", "Bolts", "Aux Engine"
]
quantities = ["1pc", "5pc", "10pc", "8pc"]

# Single and Double Placeholder Templates
body_templates_single = [
    "Please quote {}.",
    "See below for quote.",
    "Quote attached.",
    "See attached for quote.",
    "See attached requisition for quote.",
    "See requisition and provide quote.",
    "Give best price."
]
body_templates_double = [
    "Please quote {} off {}.",
    "We need {} and {}. Kindly quote.",
    "Check stock for {} and {}."
]
endings = ["Regards,", "TD", "Regards, Nine", "Thanks & Regards"]

# Generate unique RFQ number
rfq_counter = 2025

def generate_email():
    global rfq_counter
    rfq_number = rfq_counter
    rfq_counter += 1

    subject = random.choice(subjects).format(rfq_number, random.choice(products))

    salutation = random.choice(salutations)
    num_products = random.randint(1, 5)
    selected_products = random.sample(products, num_products)
    product_list = [f"{random.choice(quantities)} of {p}" for p in selected_products]

    # Randomly decide whether to include product list or refer to attachment
    if random.random() < 0.25:  # 25% chance of using "See attached"
        body = random.choice(["See attached for quote.", "See attached requisition for quote."])
    else:
        if len(selected_products) >= 2 and random.random() < 0.5:
            # Choose a template that needs two placeholders
            body = random.choice(body_templates_double).format(selected_products[0], selected_products[1])
        else:
            # Choose a template that needs one placeholder
            body = random.choice(body_templates_single).format(", ".join(product_list))

    ending = random.choice(endings)
    email_body = f"{salutation}\n\n{body}\n\n{ending}"

    return subject, email_body

def get_random_attachments():
    """Randomly select 1-5 files from the RFQs folder or return an empty list 25% of the time."""
    if random.choice([True, True, True, False]):  # 75% chance of attaching files
        files = os.listdir(ATTACHMENTS_FOLDER)
        num_files = random.randint(1, 5)
        return [os.path.join(ATTACHMENTS_FOLDER, f) for f in random.sample(files, min(num_files, len(files)))]
    return []

def send_email():
    while True:
        subject, email_body = generate_email()
        attachments = get_random_attachments()

        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = "example@gmail.com"
        msg["Subject"] = subject
        msg.set_content(email_body)

        # Attach files if any
        for file_path in attachments:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
                print(f"Email sent: {subject}")

            sleep_time = random.choice([1, 4, 6])
            time.sleep(sleep_time)

        except Exception as e:
            print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
