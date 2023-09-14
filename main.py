# initialise Notebook
import boto3
from IPython.display import HTML, display, Image as IImage
from PIL import Image, ImageDraw, ImageFont
import time
import os
from io import BytesIO

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
bucketName = "aws-rek-immersionday-" + awsRegion

# DynamoDB Table and Rekognition Collection names. We will be creating these in this module.
# to change
ddbTableName = "my-celebrities" 
collectionId = "my-celebrities"

# Create temporary directory
# This directory is not needed to call Rekognition APIs.
# We will only use this directory to download images from S3 bucket and draw bounding boxes
# to change
!mkdir m2tmp
tempFolder = 'm2tmp/'
