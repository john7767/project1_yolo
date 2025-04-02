import os, sys
import glob
import boto3
import pathlib

workingFolder = "src/assets/tmp"
extensions = ("jpg", "png")

bucket_name = ""


# s3 client 가져오기
def get_s3Client():
    global bucket_name

    my_file = str(pathlib.Path.home()) + "/.aws/credentials"
    with open(my_file, mode="r") as f:
        for line in f.readlines():
            if line.startswith("aws_access_key_id = "):
                aws_access_key_id = line.split("=")[-1].strip()
            elif line.startswith("aws_secret_access_key = "):
                aws_secret_access_key = line.split("=")[-1].strip()

    key_id = aws_access_key_id
    access_key = aws_secret_access_key

    return boto3.client(
        "s3",
        aws_access_key_id=key_id,
        aws_secret_access_key=access_key,
        region_name="ap-northeast-2",
    )


# s3 bucket 에서 이미지 리스트 가져오기
def get_s3List(bName):
    s3 = get_s3Client()

    obj_list = s3.list_objects(Bucket=bName)

    s3_list = []

    for content in obj_list["Contents"]:
        content_key = content["Key"]
        if content_key.endswith(extensions):
            s3_list.append(content_key)

    return s3_list


# s3 bucket 에서 이미지 가져오기
def get_s3Object(bucketName):
    s3 = get_s3Client()

    try:
        if not os.path.exists(workingFolder):
            os.makedirs(workingFolder)
    except OSError:
        print("Error: Creating directory. " + workingFolder)
        sys.exit(1)

    for keyName in get_s3List(bucketName):
        bName = os.path.basename(keyName)
        s3.download_file(
            Bucket=bucketName, Key=keyName, Filename=f"{workingFolder}/{bName}"
        )


# s3 bucket 에 이미지 저장하기
def put_s3Object(bucket_name, save_files):
    s3 = get_s3Client()

    for file in save_files:
        s3.upload_file(
            f"src/assets/tmp_done/{file}",
            bucket_name,
            file,
        )  ### (path, bucket, file name)


if __name__ == "__main__":
    get_s3Client()
# get_s3Object(bucket_name)
# put_s3Object()
