from shared import *

client = getRekogClient()

def detectLabels(videoNameInS3Bucket):
    print("detecing labels")
    response = client.start_label_detection(
            Video= {
                'S3Object': {
                    'Bucket': getVideoBucketName(),
                    'Name': videoNameInS3Bucket
                    }
                }
            )
    return response


def getLabels(request):
    print("getting labels")
    result = client.get_label_detection(
            JobId = request['JobId']
            )
    return result

def parseResponse(response):
    labelSet = set()
    for obj in response['Labels']:
        label = obj['Label']['Name']
        confidence = obj['Label']['Confidence']
        if (float(confidence) > 90):
            labelSet.add(label)
    return labelSet

def blockUntilJobIsFinished(job):
    print("begin blocking")
    while True:
        getLabelsResponse = getLabels(job)
        if getLabelsResponse['JobStatus'] != 'IN_PROGRESS':
            return getLabelsResponse

def makeRequestForLabels(videoNameInS3Bucket):
    tryToDetectLabels = detectLabels(videoNameInS3Bucket)
    finishedJob = blockUntilJobIsFinished(tryToDetectLabels)
    if (finishedJob['JobStatus'] != "FAILED"):
        result = parseResponse(finishedJob)
        print(result)
    else:
        print("Failed because {}".format(finishedJob['StatusMessage']))

makeRequestForLabels("Andrew Castle questions how 'achieving' Net-Zero will impact our living standards.mp4")
