import logging

LOGGER = logging.getLogger()
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)

S3_CONFIG = {
        'region_name': os.environ['AWS_REGION'],
        'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
        'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
        }
BUCKET = os.environ['S3_BUCKET']

def update_ranking_for_user(github_id):
    knowledge = KnowledgeModel(github_id, BUCKET, S3_CONFIG)
    knowledge.calculate_rankings()

