# initialise Notebook
import boto3
from IPython.display import HTML, display, Image as IImage
import time
import os
from io import BytesIO
import uuid

# Get current region to choose correct bucket
def getAwsRegion():
    mySession = boto3.session.Session()
    awsRegion = mySession.region_name
    return awsRegion

# Initialize clients
def getRekogClient():
    rekognition = boto3.client('rekognition')
    return rekognition

def getDynamoClient():
    dynamodb = boto3.client('dynamodb')
    return dynamodb

def getS3Client():
    s3 = boto3.client('s3')
    return s3;

# S3 bucket that contains sample images and videos

# We are providing sample images and videos in this bucket so
# you do not have to manually download/upload test images and videos.
# to change
def getImageBucketName():
    bucketName = "hackathon-lbc-celebrity-faces"
    return bucketName

def getVideoBucketName():
    bucketName = "hackathon-lbc-videos"
    return bucketName

# DynamoDB Table and Rekognition Collection names. We will be creating these in this module.
# to change
def getDynamoTableName():
    ddbTableName = "hackathon-celebrity-faces" 
    return ddbTableName

def getCollectionId():
    collectionId = "celebrity_id"
    return collectionId


