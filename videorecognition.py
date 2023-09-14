import boto3
from IPython.display import HTML, display, Image as IImage
import time
import os
from io import BytesIO
from shared import *

# Run the video recognition by calling the method as in the format below
# performVideoRecognition(rekognition, dynamodb, ddbTableName, collectionId, videoNameInS3Bucket)

def getDynamoDBItem(dynamodb, ddbTableName, itemId):

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

def performVideoRecognition(rekognition, dynamodb, ddbTableName: str, collectionId: str, videoName: str):

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
        # print('.', end='')
    
        getFaceSearch = rekognition.get_face_search(
        JobId=faceSearchJobId,
        SortBy='TIMESTAMP'
    )
        
    # display(getFaceSearch['JobStatus'])

    # display(getFaceSearch)

    f = open("test.json", "a")
    f.write(str(getFaceSearch))
    f.close()

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
                # A match with a confidence less than 90% will be removed
                if((eid not in theCelebs) and (conf >= 90)):
                    theCelebs[eid] = (getDynamoDBItem(dynamodb, ddbTableName, eid))
            for theFaceMatch in theFaceMatches:
                celeb = theCelebs[theFaceMatch]
                fminfo = theFaceMatches[theFaceMatch]
                strDetail = strDetail + "At {0} ms<br> {2} (ID:{1}) Conf: {4}%<br>".format(fminfo[1],
                        celeb[0], celeb[1], celeb[2], fminfo[2])
    
    printedCelebs = []

    # Unique faces detected in video
    for theCeleb in theCelebs:
        tc = theCelebs[theCeleb]
        if (tc[1] and (tc[1] not in printedCelebs)):
            print("Celebrity: {1} with Id: {0}".format(tc[0], tc[1]))
        printedCelebs.append(tc[1])

    # Display results
    # print(strOverall)