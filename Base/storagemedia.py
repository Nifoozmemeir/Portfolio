from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorageDev(S3Boto3Storage):
    location = 'media-dev'
    file_overwrite = False

class MediaStorageProd(S3Boto3Storage):
    location = 'media'
    file_overwrite = False