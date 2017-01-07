import re
import os
import json
import bisect
import pickle
import logging

import boto3
import rsyslog
import botocore
import psycopg2

LOGGER = logging.getLogger()
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)

S3_CONFIG = {
        'region_name': os.environ['AWS_REGION'],
        'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
        'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
        }
BUCKET = os.environ['S3_BUCKET']

def update_ranking_for_user(github_id, knowledge = None):
    bucket = boto3.resource('s3', **S3_CONFIG).Bucket(BUCKET)

    if not knowledge:
        knowledge = json.loads(bucket.Object('users/{}'.format(github_id)).get()['Body'].read().decode())

    rankings = dict()
    for language, modules in knowledge.items():
        rankings[language] = dict()
        for module, score in modules.items():
            rankings[language][module] = _get_ranking(bucket, language, module, score)

    write_rankings_to_db(github_id, rankings)

def _get_ranking(bucket, language, module, score):
    knowledge_regex = re.compile('.*\:([0-9,.]+)')
    key = 'leaderboard/{}/{}/'.format(language, module)
    score = float('{:.2f}'.format(score))

    all_users = []
    for user in bucket.objects.filter(Prefix = key):
        knowledge = float(re.match('.*\:([0-9,.]+)', user.key).group(1))
        all_users.append(knowledge)

    return bisect.bisect_left(all_users, score) / len(all_users)

def write_rankings_to_db(github_id, rankings):
    with psycopg2.connect(dbname = 'postgres', user = 'postgres', password = '', host = 'database') as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM github_user WHERE login = %(github_id)s', {'github_id': github_id})
            github_user_id = cursor.fetchone()[0]
            cursor.execute('SELECT user_id FROM github_account WHERE github_user_id = %(github_user_id)s', {'github_user_id': github_user_id})
            user_id = cursor.fetchone()[0]
            cursor.execute('SELECT id FROM role WHERE user_id = %(user_id)s AND type = %(type)s', {'user_id': user_id, 'type': 'contractor'})
            skill_set_id = cursor.fetchone()[0] # skill_set_id == contractor_id
            cursor.execute('UPDATE skill_set SET skills=%(skills)s WHERE id=%(skill_set_id)s', {'skills': pickle.dumps(rankings), 'skill_set_id': skill_set_id})
