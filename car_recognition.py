import boto3
import json

# AWS Services
s3 = boto3.client('s3', region_name="us-east-1")  # Update with your AWS region if needed
rekognition = boto3.client('rekognition', region_name="us-east-1")
sqs = boto3.client('sqs', region_name="us-east-1")

# S3 and SQS Configurations (Update these values)
BUCKET_NAME = "njit-cs-643"  # Update with your S3 bucket name
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/392322659569/CS643-car-image-queue"  # Update with your SQS URL

# List images in S3 bucket
response = s3.list_objects_v2(Bucket=BUCKET_NAME)
images = [img['Key'] for img in response.get('Contents', [])]

# Process each image
for image in images:
    print(f"Processing {image}...")

    # Call AWS Rekognition for Object Detection
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': image}},
        MinConfidence=90  # Confidence threshold for car detection
    )

    # Check if a car is detected
    car_detected = any(label['Name'] == 'Car' and label['Confidence'] >= 90 for label in response['Labels'])

    if car_detected:
        print(f"Car detected in {image}. Sending to SQS.")

        # Send image name to SQS
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=image)

# Signal EC2 B to stop processing (-1 is the stop signal)
sqs.send_message(QueueUrl=QUEUE_URL, MessageBody="-1")

print("Car recognition completed.")