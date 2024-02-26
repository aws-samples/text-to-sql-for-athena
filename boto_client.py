import boto3
from botocore.config import Config
import logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

retry_config = Config(
        region_name = 'us-east-1',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
)

class Clientmodules():
    def __init__(self):
        pass

    def createBedrockClient():
        session = boto3.session.Session()
        bedrock_client = session.client('bedrock',config=retry_config)
        logger.info(f'bedrock client created for profile')
        return bedrock_client
    def createBedrockRuntimeClient():
        session = boto3.session.Session()
        bedrock_runtime_client = session.client('bedrock-runtime',config=retry_config)
        logger.info(f'bedrock runtime client created ')
        return bedrock_runtime_client
    def createAthenaClient():
        session = boto3.session.Session()
        athena_client = session.client('athena',config=retry_config)
        logger.info(f'athena client created ')
        return athena_client
    def createS3Client():
        session = boto3.session.Session()
        s3_client = session.client('s3',config=retry_config)
        logger.info(f's3 client created !!')
        return s3_client