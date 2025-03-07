import boto3

# Define AWS region
AWS_REGION = "us-east-1"

# Initialize AWS services
s3 = boto3.client('s3', region_name=AWS_REGION)
rekognition = boto3.client('rekognition', region_name=AWS_REGION)
sqs = boto3.client('sqs', region_name=AWS_REGION)

# ✅ Use the correct S3 bucket and SQS queue URL
BUCKET_NAME = "njit-cs-643"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/392322659569/CS643-car-image-queue"

# Output file
output_file = "recognized_text.txt"

def recognize_text(image):
    response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': image}}
    )
    return [text['DetectedText'] for text in response['TextDetections']]

processed_images = set()  # ✅ Keep track of processed images to prevent duplicates

with open(output_file, "w") as file:
    while True:
        # ✅ Receive messages from SQS
        messages = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            VisibilityTimeout=20  # ✅ Prevents another instance from processing the same message too soon
        )

        if "Messages" not in messages:
            continue  # No messages available, keep waiting

        for msg in messages["Messages"]:
            image = msg["Body"]
            receipt_handle = msg["ReceiptHandle"]  # ✅ Store receipt handle for deletion

            # ✅ Stop processing if we receive the "-1" message
            if image == "-1":
                print("No more images to process.")
                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)  # ✅ Ensure "-1" is deleted
                exit()

            # ✅ Avoid re-processing the same image multiple times
            if image in processed_images:
                print(f"Skipping duplicate entry for {image}")
            else:
                print(f"Processing {image} for text recognition.")
                detected_texts = recognize_text(image)

                if detected_texts:
                    file.write(f"{image}: {', '.join(detected_texts)}\n")
                    print(f"Text found in {image}: {detected_texts}")

                processed_images.add(image)  # ✅ Add image to the processed set

            # ✅ Delete message from SQS after processing
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
            print(f"Deleted {image} from queue.")

print("Text recognition completed.")