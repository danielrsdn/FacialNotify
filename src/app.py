import json
import boto3
import os
from threading import Thread
from deepface import DeepFace

BUCKET_NAME = "arducambucket"

MESSAGE_TEMPLATE = '''Hello %s %s,\n\nThis is a push notification from the Cloud Doorbell Service. A person with the following description has been detected by your device:\n\nAge: %s\nGender: %s\nEmotions: %s (%s), %s (%s)\nEthnicity: %s (%s), %s (%s)\n\nYou can view and manage the captured photo by signing into your account at https://service.com\n'''

REGION = "us-west-2"
QUEUE_URL = "https://sqs.us-west-2.amazonaws.com/555446187154/NotificationQueue"

TMP_FILE_PATH = "/tmp/image/"

def predict(image):
    analysis = DeepFace.analyze(img_path=image, actions=["age", "gender", "emotion", "race"])
    return analysis[0]

def createMessageBody(analysis, recipient):
   age = analysis['age']
   dominant_gender = analysis['dominant_gender']
   emotions = [(k, "{:.2f}".format(float(v)) + "%") for k,v in sorted(analysis['emotion'].items(), key=lambda item: item[1], reverse=True)][:2]
   ethnicities = [(k, "{:.2f}".format(float(v)) + "%") for k,v in sorted(analysis['race'].items(), key=lambda item: item[1], reverse=True)][:2]
   print(MESSAGE_TEMPLATE)

   return MESSAGE_TEMPLATE % (
      recipient['fname'], recipient['lname'], 
      str(age), 
      dominant_gender,
      emotions[0][0], emotions[0][1], emotions[1][0], emotions[1][1],
      ethnicities[0][0], ethnicities[0][1], ethnicities[1][0], ethnicities[1][1])

def listen():
    sqs = boto3.client('sqs', region_name=REGION)

    while (True):
      response = sqs.receive_message(QueueUrl=QUEUE_URL, AttributeNames=['SentTimestamp'], MaxNumberOfMessages=10, MessageAttributeNames=['All'], VisibilityTimeout=10, WaitTimeSeconds=10)
      if 'Messages' in response:
         for message in response['Messages']:
            body = json.loads(message['Body'])
            sqs.delete_message(QueueUrl =QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])
            Thread(target=handleMessage, args=(body,), daemon=True).start()
      
def handleMessage(body):
    s3 = boto3.resource('s3', region_name=REGION)
    sns = boto3.resource('sns', region_name=REGION)
    recipients = body["recipients"]
    image_key = body["photoName"]
    filename = TMP_FILE_PATH + image_key
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    s3.meta.client.download_file(BUCKET_NAME, image_key, filename)
    analysis = predict(filename)
    for recipient in recipients:
        message = createMessageBody(analysis, recipient)
        sns.meta.client.publish(PhoneNumber=recipient["mobile"], Message=message)

    print('''Successfully processed message.''')


def main():
     listen()


if __name__ == "__main__":
    main()