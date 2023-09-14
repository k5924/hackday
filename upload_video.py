import urllib.request
import boto3
import urllib.request
from botocore.exceptions import NoCredentialsError
from shared import *
from videorecognition import *
from video_transcript import *
from labels import *

def download_video_from_url():
    url = input("Enter the Youtube-url\n")
    name = input("Enter the name for the video\n")
    name=name+".mp4"
    try:
        print("Downloading starts...\n")
        urllib.request.urlretrieve(url, name)
        print("Download completed..!!")
        return name
    except Exception as e:
        print(e)


def upload_video_to_s3(bucket_name='hackathon-lbc-videos'):
    url = input("Enter the Youtube-url\n")
    name = input("Enter the name for the video\n")
    s3_file_name = name + ".mp4"

    s3 = boto3.client('s3')

    try:
        print("Fetching video from URL...\n")
        # Fetching video content
        video_data = urllib.request.urlopen(url).read()

        print("Uploading to S3...\n")
        # Uploading the in-memory content to S3
        s3.put_object(Bucket=bucket_name, Key=s3_file_name, Body=video_data)

        print(f"Upload completed to {bucket_name}/{s3_file_name}!")

        print("Transcribing...")
        transcribe_audio_in_video(bucket_name, s3_file_name)

        print("Video Recognition for labels...")
        makeRequestForLabels(s3_file_name)

        print("Video Recognition for faces...")
        performVideoRecognition(getRekogClient(), getDynamoClient(), getDynamoTableName(), getCollectionId(), s3_file_name)
    except urllib.error.HTTPError as err:
        print(f"Failed to fetch the video from URL. HTTP Error: {err.code}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(e)


def upload_to_s3(file_name, bucket='hackathon-lbc-videos', s3_file_name=None):
    """
    Uploads a file to AWS S3

    :param file_name: Path to the file you want to upload
    :param bucket: Name of the S3 bucket
    :param s3_file_name: Name of the file as it should appear in S3. Defaults to the original file name.
    :return: True if file was uploaded, else False
    """

    # Create an S3 client
    s3 = boto3.client('s3')

    # If no S3 name provided, use the original file name
    if not s3_file_name:
        s3_file_name = file_name

    try:
        # Uploads the given file using a managed uploader, which will split up the
        # file if it's large and uploads parts in parallel.
        s3.upload_file(file_name, bucket, s3_file_name)
        print(f"Upload Successful! File uploaded as {s3_file_name} to {bucket}")
        return True
    except FileNotFoundError:
        print(f"The file {file_name} was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

    # Example usage:
    # upload_to_s3('local_path_to_file.txt', 'my_bucket_name', 'desired_name_in_s3.txt')


def recognize_celebrities(photo):

    client = boto3.client('rekognition')

    with open(photo, 'rb') as image:
        response = client.recognize_celebrities(Image={'Bytes': image.read()})

    print('Detected faces for ' + photo)
    for celebrity in response['CelebrityFaces']:
        print('Name: ' + celebrity['Name'])
        print('Id: ' + celebrity['Id'])
        print('KnownGender: ' + celebrity['KnownGender']['Type'])
        print('Smile: ' + str(celebrity['Face']['Smile']['Value']))
        print('Position:')
        print('   Left: ' + '{:.2f}'.format(celebrity['Face']['BoundingBox']['Height']))
        print('   Top: ' + '{:.2f}'.format(celebrity['Face']['BoundingBox']['Top']))
        print('Info')
        for url in celebrity['Urls']:
            print('   ' + url)
        print()
    return len(response['CelebrityFaces'])


if __name__ == "__main__":

    bucketName = "hackathon-lbc-videos"
    upload_video_to_s3(bucket_name=bucketName)

