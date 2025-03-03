import smtplib


def send_email():
    sender = "officialcubein@gmail.com"
    receiver = "pradhanadhyayan@gmail.com"
    message = """From: From Person <officialcubein@gmail.com>
To: To Person <pradhanadhyayan@gmail.com>
Subject: SMTP Test Email

This is a test email.
"""

    try:
        # Connect to the SMTP server
        smtp_obj = smtplib.SMTP("localhost", 1025)
        smtp_obj.sendmail(sender, receiver, message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    send_email()
