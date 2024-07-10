import os
import ast

sentry_dsn = "https://40d5cf00e79f5daa568c55acaafc56ed@sentry.spyne.xyz/2"
aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")
Hotspot_server_uri = os.environ.get("Hotspot_server_uri","beta-api.spyne.xyz")
octo_api_key = os.environ.get("octo_api_key", None) 

try:
    triton_endpoint = os.environ["triton_endpoint"]
except KeyError:
    triton_endpoint = "localhost:8001"

try:
    spyne_bucket = os.environ["spyne_bucket"]
except KeyError:
    spyne_bucket = "spyne-media"
try:
    GRPC_client = ast.literal_eval(os.environ["GRPC_client"])
except KeyError:
    GRPC_client= True
REQUEST_URL = "http://localhost:80"
weights_pth = './weights'
imagewizard_pth = './'
cache = False
image_thr = 470
memory_flush_per = 95 # enter memory percent 4
REDIS_URL = "redis://default:eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81@localhost:6379/0"
streaming_response = False
cache_dir = "/imagewizard-cache"
cache_size = int(30e9)
# weights_pth = '/home/ai-team/imagewizard/weights'
# imagewizard_pth = '/home/ai-team/staging/new/imagewizard'
