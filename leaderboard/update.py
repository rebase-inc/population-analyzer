import os
import json
import logging

import boto3
import rsyslog
import botocore
import psycopg2

LOGGER = logging.getLogger()

SKILL_DATA_S3_BUCKET = os.environ['SKILL_DATA_S3_BUCKET']
S3_CONFIG = {
        'region_name': 'us-east-1',
        'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
        'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
        }

PROFILE_KEY = 'user-profiles/{github_id}/data'
LEADERBOARD_KEYSPACE = 'population/{language}/{module}/'
LEADERBOARD_ENTRY_KEYSPACE = LEADERBOARD_KEYSPACE + '{github_id}'
LEADERBOARD_KNOWLEDGE_SUFFIX = ':{knowledge:.2f}'


def _update_leaderboard_module(s3bucket, language, module, github_id, knowledge):
    leaderboard_entry_keyspace = LEADERBOARD_ENTRY_KEYSPACE.format(language = language, module = module, github_id = github_id)
    leaderboard_entry_key = leaderboard_entry_keyspace + LEADERBOARD_KNOWLEDGE_SUFFIX.format(knowledge = knowledge)

    # this filter should only container one object
    for obj in s3bucket.objects.filter(Prefix = leaderboard_entry_keyspace):
        if obj.key != leaderboard_entry_key: 
            obj.delete()
            entry_object = s3bucket.Object(leaderboard_entry_keyspace + LEADERBOARD_KNOWLEDGE_SUFFIX.format(knowledge = knowledge))
            entry_object.put(Body = bytes('', 'utf-8'))


def update_leaderboard_with_userdata(github_id):
    s3bucket = boto3.resource('s3', **S3_CONFIG).Bucket(SKILL_DATA_S3_BUCKET)

    user_object = s3bucket.Object(PROFILE_KEY.format(github_id = github_id))
    user_data = json.loads(user_object.get()['Body'].read().decode())

    for language, modules in user_data.items():
        language_knowledge = 0.0
        for module, knowledge in modules.items():
            language_knowledge += knowledge
            _update_leaderboard_module(s3bucket, language, module, github_id, knowledge)
        _update_leaderboard_module(s3bucket, language, '__overall__', github_id, language_knowledge)

if __name__ == '__main__':
    update_leaderboard_with_userdata('andrewmillspaugh')
