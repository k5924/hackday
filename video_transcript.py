import uuid
import boto3
import time
from IPython.display import display
import json

def transcribe_audio_in_video(bucket_name, file):

    s3 = boto3.client('s3')
    transcribe = boto3.client('transcribe')
    job_name = f'video_moderation_{str(uuid.uuid1())[0:4]}'
    file_out = f'transcriptions/jobs/{job_name}'
    transcribe.start_transcription_job(
            TranscriptionJobName = job_name,
            Media={
                'MediaFileUri': f's3://{bucket_name}/{file}'
            },
            OutputBucketName=bucket_name,
            OutputKey=file_out,
            MediaFormat='mp4',
            LanguageCode='en-US'
        )

    getTranscription = transcribe.get_transcription_job(TranscriptionJobName=job_name)

    while(getTranscription['TranscriptionJob']['TranscriptionJobStatus'] == 'IN_PROGRESS'):
        time.sleep(5)
        print('.', end='')

        getTranscription = transcribe.get_transcription_job(TranscriptionJobName = job_name)

    display(getTranscription['TranscriptionJob']['TranscriptionJobStatus'])

    filename = f'transcriptions/{file}.txt'
    s3_clientobj = s3.get_object(Bucket=bucket_name, Key=file_out)
    s3_clientdata = s3_clientobj["Body"].read().decode("utf-8")
    original = json.loads(s3_clientdata)
    output_transcript = original["results"]["transcripts"][0]['transcript'] #

    print(output_transcript)
    s3.put_object(Bucket=bucket_name, Key=filename, Body=output_transcript)
    run_sentiment(output_transcript)

def run_sentiment(text):
    comprehend=boto3.client('comprehend')
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    print(json.dumps(response, sort_keys=True, indent=4))


if __name__ == "__main__":

    bucketName = "hackathon-lbc-videos"
    file = "Caller discusses rising costs of groceries with James O'Brien.mp4"
    transcribe_audio_in_video(bucket_name=bucketName, file=file)
