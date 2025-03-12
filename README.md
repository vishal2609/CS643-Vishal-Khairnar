# AWS Image Recognition Pipeline

## Overview
I implemented an **image recognition pipeline** in AWS using two EC2 instances, S3, SQS, and Rekognition. The pipeline consists of:
- **Car Detection**: Detects images containing cars with over 90% confidence using AWS Rekognition.
- **Text Recognition**: Identifies text within images that contain cars.
- **Parallel Processing**: Uses SQS to pass image indexes between two EC2 instances running in parallel.

## Architecture
The pipeline consists of the following AWS services:
1. **S3**: Stored the dataset of images.
2. **EC2 A (Car Recognition Service)**: Detected cars in images using AWS Rekognition.
3. **SQS (Queue Service)**: Stored indexes of images that contain cars.
4. **EC2 B (Text Recognition Service)**: Read image indexes from SQS and performed text recognition.
5. **AWS Rekognition**: Performed object (car) and text recognition.
6. **Output**: Generated a file containing indexes of images with cars and recognized text.

## Prerequisites
1. **AWS Account** (Standard or AWS Educate).
2. **AWS CLI Installed** ([Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)).
3. **Amazon Linux EC2 Instances** with `t2.micro` (Free Tier).
4. **AWS SDK** for the chosen programming language (Python, Java, Node.js, etc.).
5. **Security Group** allowing SSH, HTTP, and HTTPS (restricted SSH to my IP).

## Setup Instructions

### 1. Launched EC2 Instances
- Launched **two EC2 instances** (Amazon Linux AMI).
- Assigned the same **.pem key** to both instances.

### 2. Configured AWS Credentials
For an **AWS Educate** account, I retrieved credentials via **Vocareum** and updated `~/.aws/credentials`:

```bash
mkdir -p ~/.aws
nano ~/.aws/credentials
```

Added:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
aws_session_token = YOUR_SESSION_TOKEN  # (Required for AWS Educate)
region = us-east-1
```

For a **standard AWS account**, I followed [this guide](https://docs.aws.amazon.com/rekognition/latest/dg/setup-awscli-sdk.html).

### 3. Set Up S3 Bucket
- The dataset was hosted at: `https://njit-cs-643.s3.us-east-1.amazonaws.com`
- To copy images locally, I ran:

```bash
aws s3 cp s3://njit-cs-643 ./images --recursive
```

### 4. Set Up SQS Queue
- Created an SQS queue in AWS Console.
- Retrieved its **queue URL** and **ARN**.

```bash
aws sqs create-queue --queue-name ImageProcessingQueue
```

### 5. Installed Dependencies
For **Python**:
```bash
sudo yum install python3 -y
pip3 install boto3
```

For **Java**:
```bash
sudo yum install java-1.8.0-openjdk-devel -y
```

### 6. Deployed Code on EC2 Instances

#### EC2 A: Car Recognition Service
- Downloaded images from S3.
- Used **AWS Rekognition** to detect cars.
- If confidence >90%, it sent the image index to SQS.

Ran:

```bash
python3 car_recognition.py
```

#### EC2 B: Text Recognition Service
- Read image indexes from SQS.
- Downloaded images from S3.
- Used **AWS Rekognition** to extract text.
- Outputted the results to a file.

Ran:

```bash
python3 text_recognition.py
```

### 7. Terminated and Cleaned Up
To avoid charges, I **terminated my EC2 instances** and **deleted the SQS queue**:

```bash
aws sqs delete-queue --queue-url YOUR_QUEUE_URL
aws ec2 terminate-instances --instance-ids INSTANCE_ID
```

## Running the Application
Once both instances were running, the processing pipeline worked as follows:
1. EC2 A downloaded images and detected cars.
2. If a car was detected, it pushed the index to SQS.
3. EC2 B read indexes from SQS and extracted text.
4. The final output file contained **image indexes with both cars and text**.

## Output Example
```bash
Detected cars in images: ['2.jpg', '5.jpg', '9.jpg']
Recognized text:
2.jpg: "New Jersey 123ABC"
5.jpg: "Parking Lot B"
9.jpg: "Speed Limit 55"
```
