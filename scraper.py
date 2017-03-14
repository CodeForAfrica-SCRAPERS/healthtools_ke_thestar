import requests
import boto3
import os, json

import sys

import watson_developer_cloud
import watson_developer_cloud.natural_language_understanding.features.v1 as features

nlu = watson_developer_cloud.NaturalLanguageUnderstandingV1(
    version='2017-02-27',
    username=os.environ['MORPH_WATSON_USERNAME'],
    password=os.environ['MORPH_WATSON_PASSWORD'])

r = requests.get('http://www.the-star.co.ke/api/mobile/views/mobile_app?args[0]=24&limit=50')

feed = r.json()
articles = []

for article in feed:
    tags = []
    tags_weighted = []

    response = nlu.analyze(
        text=article['body'],
        features=[features.Concepts()])

    for concept in response['concepts'][:5]:
        tags.append(concept['text'])
        tags_weighted.append({concept['text']: concept['relevance']})

    article['sorted_tags'] = list(set(tags))
    article['theme'] = tags_weighted

    articles.append({'node': article})

data = {
    'nodes': articles,
    'tags' : []
}


s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['MORPH_AWS_ACCESS_KEY'],
    aws_secret_access_key=os.environ['MORPH_AWS_SECRET_KEY'],
    region_name='eu-west-1'
)

s3.put_object(
    Bucket='cfa-healthtools-ke',
    ACL='public-read',
    Key='starhealth-news.json',
    Body=json.dumps(data)
)

print "Successfully finished."
