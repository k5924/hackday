import urllib.request
import boto3
import json

def run_sentiment(text):

    comprehend=boto3.client('comprehend')
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    print(json.dumps(response, sort_keys=True, indent=4))

if __name__ == "__main__":

    bucketName = "hackathon-lbc-videos"
    upload_video_to_s3(bucket_name=bucketName)

