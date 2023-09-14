import boto3
from IPython.display import HTML, display, Image as IImage
import time
import os
from io import BytesIO

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