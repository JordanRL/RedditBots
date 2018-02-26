import os
import json
import boto3
import pprint
from flask import Flask, request, make_response


SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# This `app` represents your existing Flask app
app = Flask(__name__)
sqs = boto3.client('sqs')

# An example of one of your Flask app's routes
@app.route("/")
def hello():
    return "Hello there!"

@app.route("/interactive-message", methods=['GET', 'POST'])
def interactive_message():
    # If a GET request is made, return 404.
    if request.method == 'GET':
        return make_response("These are not the slackbots you're looking for.", 404)

    # Parse the request payload into JSON
    event_data = json.loads(request.data.decode('utf-8'))

    # Verify the request token
    request_token = event_data.get("token")
    if SLACK_VERIFICATION_TOKEN != request_token:
        return make_response("Request contains invalid Slack verification token", 403)

    # Echo the URL verification challenge code
    if "challenge" in event_data:
        return make_response(
            event_data["challenge"], 200, {"content_type": "application/json"}
        )

    sqs.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
        MessageBody=json.dumps(event_data),
        MessageGroupId="interactive-event-"+str(event_data["message_ts"]),
        MessageDeduplicationId=event_data["user"]["id"]
    )
    return make_response("", 200)

@app.route("/slack/events", methods=['GET', 'POST'])
def event_handler():
    # If a GET request is made, return 404.
    if request.method == 'GET':
        return make_response("These are not the slackbots you're looking for.", 404)

    # Parse the request payload into JSON
    event_data = json.loads(request.data.decode('utf-8'))

    # Verify the request token
    request_token = event_data.get("token")
    if SLACK_VERIFICATION_TOKEN != request_token:
        return make_response("Request contains invalid Slack verification token", 403)

    # Echo the URL verification challenge code
    if "challenge" in event_data:
        return make_response(
            event_data["challenge"], 200, {"content_type": "application/json"}
        )

    sqs.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
        MessageBody=json.dumps(event_data),
        MessageGroupId=event_data["event"]["type"],
        MessageDeduplicationId=event_data['event_id']
    )
    return make_response("", 200)


# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=3000)