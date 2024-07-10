import base64
from typing import Optional
from datetime import date
import mimetypes
from tempfile import NamedTemporaryFile
from threading import Thread
import io
import boto3
import cv2
import ast
import config
from Utils.gen_utils import resize_func,color_change
from PIL import Image, ImageCms
import numpy as np
import pyexiv2
# import elasticapm
import botocore
s3 = boto3.resource('s3', aws_access_key_id=config.aws_access_key_id,
                    aws_secret_access_key=config.aws_secret_access_key)
                    
s3_client = boto3.client('s3',config = botocore.client.Config(
         s3 = {
             'use_accelerate_endpoint': True
         }
     ) )

default_save_params = {
    "extension": ".png",
    "quality": 100,
    "input_resolution":False
}

color_profile_to_profile = {
    "sRGB": ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
}


def validate_save_params(save_params):
    save_params = ast.literal_eval(str(save_params))
    if "extension" in save_params:
        if save_params["extension"] not in [".png", ".jpg", ".webp", ".jpeg"]:
            save_params["extension"] = ".png"
    else:
        save_params["extension"] = ".png"
    if "quality" not in save_params:
        save_params["quality"] = 95
    return save_params


def save_thread(img, imagename, key, process, save_params=default_save_params, bucket_name=config.spyne_bucket):
    img = resize_func(img, save_params)
    with NamedTemporaryFile(dir="/dev/shm/", suffix=save_params["extension"]) as temp:
        cv2.imwrite(temp.name, img, [int(cv2.IMWRITE_JPEG_QUALITY), save_params["quality"]])
        url = save_file_to_cloud(temp.name, imagename, key, process, save_params["extension"], bucket_name=bucket_name)

# @elasticapm.capture_span()
def save_to_cloud(img, imagename, process, key: Optional[str] = None, save_params=default_save_params, bucket_name=config.spyne_bucket ,cache = None):
    key = date.today().strftime("%Y-%m-%d") + "/" if key is None else key

    if cache is None:
        cache = config.cache
    if cache:
        img = color_change(img)
        img = Image.fromarray(img)
        bytes_image = io.BytesIO()
        img.save(bytes_image, format='PNG')
        return base64.b64encode(bytes_image.getvalue())
    save_params = validate_save_params(save_params)
    extension = save_params["extension"]
    # t = Thread(target=save_thread, args=(img, imagename, key, process, save_params, bucket_name))
    # t.start()
    save_thread(img, imagename, key, process, save_params, bucket_name)
    aws_path = key + process + "_" + imagename + extension
    if bucket_name == 'spyne-acceleration':
        url = f"https://{bucket_name}.s3-accelerate.amazonaws.com/{aws_path}"
    else:
        url = f"https://{bucket_name}.s3.amazonaws.com/{aws_path}"
    return url
def save_thread_ecom(img, imagename, key, process, save_params=default_save_params, bucket_name=config.spyne_bucket):
    with NamedTemporaryFile(dir="/dev/shm/", suffix=save_params["extension"]) as temp:
        if np.array(img).shape[-1] != 4:
            img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        else:
            img=cv2.cvtColor(img,cv2.COLOR_RGBA2BGRA)
        img=Image.fromarray(img)
        color_profile = save_params.get('color_profile', None)
        icc_profile = color_profile_to_profile[color_profile] if color_profile is not None else None
        img.save(
            temp.name,
            quality=save_params["quality"],
            dpi=(int(save_params["dpi"]),int(save_params["dpi"])),
            icc_profile=icc_profile
        )
        # cv2.imwrite(temp.name, img, [int(cv2.IMWRITE_JPEG_QUALITY), save_params["quality"]])
        url = save_file_to_cloud(temp.name, imagename, key, process, save_params["extension"], bucket_name=bucket_name)


def save_to_cloud_ecom(img, imagename, key, process, save_params=default_save_params, bucket_name=config.spyne_bucket):
    save_params = validate_save_params(save_params)
    extension = save_params["extension"]
    # t = Thread(target=save_thread, args=(img, imagename, key, process, save_params, bucket_name))
    # t.start()
    save_thread_ecom(img, imagename, key, process, save_params, bucket_name)
    aws_path = key + process + "_" + imagename + extension
    url = f"https://{bucket_name}.s3.amazonaws.com/{aws_path}"
    return url


def save_file_to_cloud(file_path, imagename, key, process, extension, bucket_name=config.spyne_bucket):
    with pyexiv2.Image(file_path) as img:
        # print(img.read_exif())
        # print(img.read_xmp())
        img.modify_xmp({"Xmp.plus.CopyrightOwnerName":"spyne.ai"})
        img.modify_exif({'Exif.Image.ProcessingSoftware': 'spyne.ai',"Exif.Image.Artist":"AI Team","Exif.Image.Copyright":"Copyright 2023 Spyne.ai All rights reserved","Exif.Photo.MakerNote":"spyne.ai added discription by neel","Exif.Image.ImageDescription":"processed by spyne.ai (AI Photography and Editing for Car Dealerships & Marketplaces)"})
        img.modify_comment('processed by spyne.ai (AI Photography and Editing for Car Dealerships & Marketplaces) \n')
    aws_path = key + process + "_" + imagename + extension
    content_type = mimetypes.guess_type(aws_path)[0]
    if bucket_name == 'spyne-acceleration':
        s3_client.upload_file(file_path, bucket_name,aws_path,ExtraArgs={'ContentType': content_type, "Metadata": {'Exif.Image.ProcessingSoftware': 'spyne.ai',"Exif.Image.Artist":"AI Team","Exif.Image.Copyright":"Copyright 2023 Spyne.ai All rights reserved","Exif.Photo.MakerNote":"spyne.ai added discription by neel","Exif.Image.ImageDescription":"processed by spyne.ai (AI Photography and Editing for Car Dealerships & Marketplaces)"}})
    else:
        s3.Bucket(bucket_name).upload_file(file_path, aws_path, ExtraArgs={'ContentType': content_type, "Metadata": {'Exif.Image.ProcessingSoftware': 'spyne.ai',"Exif.Image.Artist":"AI Team","Exif.Image.Copyright":"Copyright 2023 Spyne.ai All rights reserved","Exif.Photo.MakerNote":"spyne.ai added discription by neel","Exif.Image.ImageDescription":"processed by spyne.ai (AI Photography and Editing for Car Dealerships & Marketplaces)"}})
    if bucket_name == 'spyne-acceleration':
        url = f"https://{bucket_name}.s3-accelerate.amazonaws.com/{aws_path}"
    else:
        url = f"https://{bucket_name}.s3.amazonaws.com/{aws_path}"
    return url

def save_anyfile_to_cloud(file_path, imagename, date, extension,mimetype, bucket_name='spyne'):
    
    aws_path = date + "_" + imagename + extension
    content_type = mimetype if mimetype is not None else mimetypes.guess_type(aws_path)[0]
    if bucket_name=='spyne' or bucket_name=='spyne-media':
        s3.Bucket(bucket_name).upload_file(file_path, aws_path, ExtraArgs={'ContentType': content_type})
    else:
        s3_client.upload_file(file_path, bucket_name,aws_path,ExtraArgs={'ContentType': content_type})
    if bucket_name == 'spyne-acceleration':
        url = f"https://{bucket_name}.s3-accelerate.amazonaws.com/{aws_path}"
    else:
        url = f"https://{bucket_name}.s3.amazonaws.com/{aws_path}"
    return url

# def save_to_gcp(img, imagename, key, process, extension, bucket_name="spyne"):
#     storage_client = storage.Client.from_service_account_json("vision_api.json")
#     gcp_bucket = storage_client.get_bucket(bucket_name)
#     with NamedTemporaryFile(dir="/dev/shm/", suffix=extension) as temp:
#         cv2.imwrite(temp.name, img)
#         imgname = process + "_" + imagename + extension
#         blob = gcp_bucket.blob(key + imgname)
#         # blob.upload_from_filename(temp.name)
#         reset_retry(blob.upload_from_filename)(temp.name)
#     return blob.public_url


# def save_file_to_gcp(file_path, imagename, key, process, extension, bucket_name='spyne'):
#     storage_client = storage.Client.from_service_account_json("vision_api.json")
#     gcp_bucket = storage_client.get_bucket(bucket_name)
#     imgname = process + "_" + imagename + extension
#     blob = gcp_bucket.blob(key + imgname)
#     reset_retry(blob.upload_from_filename)(file_path)
#     return blob.public_url
