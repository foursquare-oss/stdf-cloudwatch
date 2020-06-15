import json
import boto3
import os
import base64
import zlib


def get_sns_topic():
    return os.environ['SNS_TOPIC']


def post_to_sns(stdf_message, sns_topic):
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=sns_topic,
        Subject='stdfMessage',
        Message=json.dumps(stdf_message)
    )


def format_to_stdf(single_event):
    return {
        'payload': {
            'title': os.getenv('MESSAGE_TITLE'),
            'description': os.getenv('MESSAGE_DESCRIPTION'),
            'raw_data': single_event['message']
        },
        'meta': {
            'timestamp': single_event['timestamp'],
            'source': {
                'provider': 'AWS',
                'account_id': os.getenv('SOURCE_ACCOUNT_NUMBER'),
                'region': os.getenv('SOURCE_REGION'),
                'service': 'CloudWatch',
                'event_id': single_event['id'],
                'app_name': os.getenv('APP_NAME')
            },
        },
        'stdf_version': 2,
    }


def extract_log_events(event):
    raw_payload = event['awslogs']['data']
    json_payload = json.loads(zlib.decompress(base64.b64decode(raw_payload), 16 + zlib.MAX_WBITS).decode('utf-8'))
    return json_payload['logEvents']


def lambda_handler(event, context):
    log_events = extract_log_events(event)
    for single_event in log_events:
        processed_event = format_to_stdf(single_event)
        post_to_sns(processed_event, get_sns_topic())
