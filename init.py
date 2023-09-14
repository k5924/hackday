# initialise Notebook
import boto3
from IPython.display import HTML, display, Image as IImage
import time
import os
from io import BytesIO
import uuid

# Get current region to choose correct bucket
mySession = boto3.session.Session()
awsRegion = mySession.region_name

# Initialize clients
rekognition = boto3.client('rekognition')
dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

# S3 bucket that contains sample images and videos

# We are providing sample images and videos in this bucket so
# you do not have to manually download/upload test images and videos.
# to change
bucketName = "hackathon-lbc-celebrity-faces"

# DynamoDB Table and Rekognition Collection names. We will be creating these in this module.
# to change
ddbTableName = "hackathon-celebrity-faces" 
collectionId = "celebrity_id"

# Create temporary directory
# This directory is not needed to call Rekognition APIs.
# We will only use this directory to download images from S3 bucket and draw bounding boxes
# to change
tempFolder = 'm2tmp/'

# List existing DynamoDB Tables
# Before creating DynamoDB table, let us first look at the list of existing DynamoDB tables in our account.

listTablesResponse = dynamodb.list_tables()
display(listTablesResponse["TableNames"])

def indexFace (bucketName, imageName, celebrityId):

    indexFaceResponse = rekognition.index_faces(
        CollectionId=collectionId,
        Image={
            'S3Object': {
                'Bucket': bucketName,
                'Name': imageName,
            }
        },
        ExternalImageId=celebrityId,
        DetectionAttributes=[
            'DEFAULT' #'DEFAULT'|'ALL',
        ],
        MaxFaces=1,
        QualityFilter='AUTO' #NONE | AUTO | LOW | MEDIUM | HIGH
    )
    
    display(indexFaceResponse)

# We will define a method to write metadata (id, name, url) of celebrity to DynamoDB
def addCelebrityToDynamoDB(celebrityId, celebrityName, celebrityUrl):
    ddbPutItemResponse = dynamodb.put_item(
        Item={
            'celebrity_id': {'S': str(uuid.uuid4())},
            'id': {'S': celebrityId},
            'name': {'S': celebrityName},
            'url': { 'S': celebrityUrl},
        },
        TableName=ddbTableName,
    )

addCelebrityToDynamoDB("4", "Andrew Marr", "https://hackathon-lbc-celebrity-faces.s3.amazonaws.com/Andrew+Marr.png")
