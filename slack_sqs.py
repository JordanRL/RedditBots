import json
import boto3
import time


class SlackSQS:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.message_queue = "https://sqs.us-east-1.amazonaws.com/068534578493/slackmessages.fifo"
        self.event_queue = "https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo"
        self.current_message = {}
        self.current_event = {}

    def pack_message(self, channel, text=None, attachment=None):
        message = {
            "channel": channel
        }
        dedupe = ""
        if text is not None:
            message["text"] = text
            dedupe = text
        if attachment is not None:
            message["attachment"] = attachment
            if "text" in attachment:
                dedupe = attachment["text"]
            if "pretext" in attachment:
                dedupe = attachment["pretext"]
        if dedupe == '':
            return False
        else:
            self.sqs.send_message(
                QueueUrl=self.message_queue,
                MessageBody=json.dumps(message),
                MessageGroupId='queued-message',
                MessageDeduplicationId=dedupe+':'+str(time.time())
            )
            return True

    def unpack_message(self):
        message = self.sqs.receive_message(
            QueueUrl=self.message_queue,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        if "Messages" in message:
            self.current_message = json.loads(message["Messages"][0]["Body"])
            self.sqs.delete_message(
                QueueUrl=self.message_queue,
                ReceiptHandle=message["Messages"][0]["ReceiptHandle"]
            )
            return True
        else:
            return False

    def pack_event(self, event):
        self.sqs.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
            MessageBody=json.dumps(event),
            MessageGroupId="slack-event",
            MessageDeduplicationId=event['event_id']
        )
        return True

    def unpack_event(self, event):
        event = self.sqs.receive_message
        return True
