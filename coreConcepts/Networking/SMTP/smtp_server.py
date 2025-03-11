import smtpd
import asyncore


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print(f"Received message from: {mailfrom}")
        print(f"To: {rcpttos}")
        print(f"Message length: {len(data)}")
        print(f"Message data:\n{data.decode('utf-8')}")
        print("-" * 40)


# Start the SMTP server on localhost:1025
server = CustomSMTPServer(("localhost", 1025), None)

print("SMTP server started on localhost:1025")
asyncore.loop()
