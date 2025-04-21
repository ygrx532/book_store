import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka Consumer Configuration
brokers = '3.129.102.184:9092,18.118.230.221:9093,3.130.6.49:9094'
print("[DEBUG] (1) Attempting to connect to Kafka brokers...")

consumer = Consumer({
    'bootstrap.servers': brokers,
    'group.id': 'crm-consumer-group',
    'auto.offset.reset': 'earliest',
})

print("[DEBUG] (1) Connected to Kafka brokers.")

# Email Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'e30254865@gmail.com'
SMTP_PASSWORD = 'qxtmxwblkclbukja'

def send_email(to_email, customer_name):
    subject = "Activate your book store account"
    body = f"""
    Dear {customer_name},
    
    Welcome to the Book store created by yuyangx2.
    Exceptionally this time we won’t ask you to click a link to activate your account.
    """
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    print(f"[DEBUG] (5) Attempting to send email to {to_email}...")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
            print(f"[DEBUG] (5) Email sent successfully to {to_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {str(e)}")

def consume_kafka_messages():
    print("[DEBUG] Subscribing to topic 'yuyangx2.customer.evt'...")
    consumer.subscribe(['yuyangx2.customer.evt'])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())

            print("[DEBUG] (4) Received event message from Kafka.")
            
            # Deserialize the message value
            try:
                message_data = json.loads(msg.value().decode('utf-8'))
                print(f"[DEBUG] Raw message: {message_data}")
            except Exception as e:
                print(f"[ERROR] Failed to parse message: {str(e)}")
                continue

            customer_name = message_data['name']
            customer_email = message_data['userId']

            print(f"[DEBUG] (4) Parsed customer name: {customer_name}, email: {customer_email}")

            # Send email to the customer
            send_email(customer_email, customer_name)

    except KeyboardInterrupt:
        print("[INFO] Shutting down consumer...")
    finally:
        consumer.close()
        print("[INFO] Kafka consumer connection closed.")

# Main entry point
if __name__ == "__main__":
    print("[INFO] Starting CRM consumer service...")
    consume_kafka_messages()
