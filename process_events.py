import boto3
import praw
import json
import os
import pprint
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

channel_list = {}
user_list = {}
joined_channels = []
active_votes = {}

auth_test = slack_client.api_call("auth.test")

starterbot_id = slack_client.api_call("auth.test")["user_id"]

sqs = boto3.client('sqs')

channel_request = slack_client.api_call(
    "channels.list",
    exclude_archived=1
)
print('Building channel list')
for channel_item in channel_request["channels"]:
    channel_list[channel_item["name"]] = channel_item["id"]
    if starterbot_id in channel_item["members"]:
        joined_channels.append(channel_item["name"])
        print('Already in channel '+channel_item["name"])
user_request = slack_client.api_call(
    "users.list"
)
print("Building user list")
for user_item in user_request["members"]:
    user_list[user_item["name"]] = user_item["id"]

print('Startup complete. Listening for events.')
while True:
    print('Polling Queue')
    messages = sqs.receive_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )
    if 'Messages' in messages:
        for message in messages["Messages"]:
            event_data = json.loads(message['Body'])
            print('Processed Event: '+event_data['event']['type'])
            if event_data['event']['type'] == "message":
            elif event_data['event']['type'] == "message.im":
            sqs.delete_message(
                QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
                ReceiptHandle=message['ReceiptHandle']
            )
    else:
        print('Queue Empty, Repolling')
