import os
import re
import signal
import logging

import boto3
from stdlib_list import stdlib_list

from knowledgemodel import Knowledge, S3Population, PostgresPopulation

LOGGER = logging.getLogger()
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)

S3_CONFIG = {
        'region_name': os.environ['AWS_REGION'],
        'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
        'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
        }
BUCKET = os.environ['S3_BUCKET']

STANDARD_LIBRARY = set(stdlib_list('3.5')) | set(stdlib_list('2.7'))

def update_ranking_for_user(github_id):
    s3population = S3Population(BUCKET, S3_CONFIG, depth = 2)
    pgpopulation = PostgresPopulation(depth = 2)
    knowledge = s3population.get_user_knowledge(github_id)
    rankings = s3population.calculate_rankings(knowledge)
    pgpopulation.add_user_ranking(github_id, rankings)

def clean():
    bucket = boto3.resource('s3', **S3_CONFIG).Bucket(BUCKET)
    prefix = 'leaderboard/python'
    for obj in bucket.objects.filter(Prefix = 'leaderboard/python'):
        package = re.match('leaderboard/python/([^/]+)/', obj.key).group(1)
        if package in STANDARD_LIBRARY:
            signal.alarm(180) # rq keepalive
            LOGGER.info('Deleting {}'.format(obj.key))
            obj.delete()
