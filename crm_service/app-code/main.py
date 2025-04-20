import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka Consumer Configuration
brokers = '3.129.102.184:9092,18.118.230.221:9093,3.130.6.49:9094'
consumer = Consumer({
    'bootstrap.servers': brokers,  # Use a placeholder for Kafka brokers
    'group.id': 'crm-consumer-group',
    'auto.offset.reset': 'earliest',  # Consume from the beginning
})

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
    
    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Encrypt connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def consume_kafka_messages():
    consumer.subscribe(['yuyangx2.customer.evt'])

    try:
        while True:
            msg = consumer.poll(1.0)  # Poll for messages for up to 1 second
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            
            # Deserialize the message value
            message_data = json.loads(msg.value().decode('utf-8'))
            customer_name = message_data['name']
            customer_email = message_data['userId']  # Assuming userId is the email

            # Send an email to the newly registered customer
            send_email(customer_email, customer_name)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

# Start consuming messages in the background
if __name__ == "__main__":
    consume_kafka_messages()
