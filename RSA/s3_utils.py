import boto3 # type: ignore

def upload_to_s3(file_path, s3_path):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, "your-bucket-name", s3_path)
