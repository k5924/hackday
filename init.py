from shared import *

# Get current region to choose correct bucket
awsRegion = getAwsRegion()

# Initialize clients
rekognition = getRekogClient()
dynamodb = getDynamoClient()
s3 = getS3Client()

# S3 bucket that contains sample images and videos

# We are providing sample images and videos in this bucket so
# you do not have to manually download/upload test images and videos.
# to change
bucketName = getBucketName()

# DynamoDB Table and Rekognition Collection names. We will be creating these in this module.
# to change
ddbTableName = getDynamoTableName()
collectionId = getCollectionId()

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

# this inserts into the dynamo db
# addCelebrityToDynamoDB("4", "Andrew Marr", "https://hackathon-lbc-celebrity-faces.s3.amazonaws.com/Andrew+Marr.png")

def getDynamoDBItem(itemId):
    ddbGetItemResponse = dynamodb.get_item(
        Key={'celebrity_id': {'S': itemId} },
        TableName=ddbTableName
    )

    itemToReturn = ('', '', '')

    if('Item' in ddbGetItemResponse):
        itemToReturn = (ddbGetItemResponse['Item']['id']['S'],
                ddbGetItemResponse['Item']['name']['S'],
                ddbGetItemResponse['Item']['url']['S'])

    return itemToReturn

# uncomment this and run it to create the collections, then use the below lines to ensure they have been created successfully
# createCollectionResponse = rekognition.create_collection(
#     CollectionId=collectionId
# )
# display(createCollectionResponse)

# List Rekognition Collections
# Let us make sure that Recognition we just created now appears in the list of collections in our AWS account.
# listCollectionsResponse = rekognition.list_collections()

# display(listCollectionsResponse["CollectionIds"])
# display(listCollectionsResponse["FaceModelVersions"])

# # describeCollectionResponse = rekognition.describe_collection(
# #     CollectionId=collectionId
# # )
# # display(describeCollectionResponse)

# describeCollectionResponse = rekognition.describe_collection(
#     CollectionId=collectionId
# )
# display("FaceCount: {0}".format(describeCollectionResponse["FaceCount"]))

# indexFace(bucketName, "James O'Brien.jpg", "e6669e13-dc7c-44d3-9a22-f7eb7e81d49d")

videoName = "Andrew Castle questions how 'achieving' Net-Zero will impact our living standards.mp4"

startFaceSearchResponse = rekognition.start_face_search(
    Video={
        'S3Object': {
            'Bucket': "hackathon-lbc-videos",
            'Name': videoName
        }
    },
    FaceMatchThreshold=90,
    CollectionId=collectionId,
)


faceSearchJobId = startFaceSearchResponse['JobId']
display("Job ID: {0}".format(faceSearchJobId))

getFaceSearch = rekognition.get_face_search(
    JobId=faceSearchJobId,
    SortBy='TIMESTAMP'
)

while(getFaceSearch['JobStatus'] == 'IN_PROGRESS'):
    time.sleep(5)
    print('.', end='')

    getFaceSearch = rekognition.get_face_search(
    JobId=faceSearchJobId,
    SortBy='TIMESTAMP'
)

# display(getFaceSearch['JobStatus'])

# display(getFaceSearch)

theCelebs = {}

# Display timestamps and celebrites detected at that time
strDetail = "Celebrites detected in vidoe<br>=======================================<br>"
strOverall = "Celebrities in the overall video:<br>=======================================<br>"

# Faces detected in each frame
for person in getFaceSearch['Persons']:
    if('FaceMatches' in person and len(person["FaceMatches"])> 0):
        ts = person["Timestamp"]
        theFaceMatches = {}
        for fm in person["FaceMatches"]:
            conf = fm["Similarity"]
            eid =  fm["Face"]["ExternalImageId"]
            if(eid not in theFaceMatches):
                theFaceMatches[eid] = (eid, ts, round(conf,2))
            if(eid not in theCelebs):
                theCelebs[eid] = (getDynamoDBItem(eid))
        for theFaceMatch in theFaceMatches:
            celeb = theCelebs[theFaceMatch]
            fminfo = theFaceMatches[theFaceMatch]
            strDetail = strDetail + "At {0} ms<br> {2} (ID:{1}) Conf: {4}%<br>".format(fminfo[1],
                       celeb[0], celeb[1], celeb[2], fminfo[2])

# Unique faces detected in video
for theCeleb in theCelebs:
    tc = theCelebs[theCeleb]
    strOverall = strOverall + "{1} (ID: {0})<br>".format(tc[0], tc[1], tc[2])

# Display results
print(strOverall)