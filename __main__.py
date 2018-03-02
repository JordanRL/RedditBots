import os
import json
import boto3
import pprint
import subprocess as s
from multiprocessing import Process
import sys
import signal
import shlex
import praw
import settings
import re
from datetime import datetime
from flask import Flask, request, make_response
from slackclient import SlackClient
from slack_messenger import SlackMessenger
from attachmentBuilder import Attachment


reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# This `app` represents your existing Flask app
app = Flask(__name__)
#sqs = boto3.client('sqs')
subprocesses = {}
slack_users = {}
slack_channels = {}
slack_joined_channels = []
slack_client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))
bot_user = None
bot_admin_users = [
    'jledoux'
]
server_process = Process(target=app.run, kwargs={"port": 3000})
root_process = True


def interrupt_handler(signal, frame):
    if root_process is not None and root_process is True:
        print('\nScript Shutdown Received')
        print('Stopping child processes')
        for name, process in subprocesses.items():
            process["process"].terminate()
            print('Process Terminated: '+name)
        print('Child Processes Stopped')
        print('Stopping Flask Server')
        server_process.terminate()
        print('Flask Server Stopped')
        print('Goodbye.')
    sys.exit(1)


signal.signal(signal.SIGINT, interrupt_handler)


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
        MessageGroupId="interactive-event",
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

    if event_data["event"]["type"] == "message" or event_data["event"]["type"] == "message.im":
        message_text = event_data["event"]["text"]
        message_channel = event_data["event"]["channel"]
        mentioned_user = 0
        user_id, message_body = parse_direct_mention(message_text)
        direct_processed = False
        if user_id is not None:
            mentioned_user = user_id
            message_text = message_body
        if (message_channel.startswith("D") or mentioned_user == starterbot_id) and event_data["event"]["user"] in globals()["bot_admin_users"]:
            messenger = SlackMessenger(slack_client)
            messenger.set_channel(message_channel)
            if message_text.startswith("!listProcesses"):
                if len(subprocesses) == 0:
                    messenger.set_text("There are no processes running on ABB right now.")
                    messenger.send_message()
                else:
                    reddit_process = {}
                    slack_process = {}
                    for process_name, process_info in subprocesses.items():
                        if process_info["type"] == "reddit":
                            reddit_process[process_name] = process_info
                        elif process_info["type"] == "slack":
                            slack_process[process_name] = process_info
                    header_attachment = Attachment("", "")
                    reddit_attachment = Attachment("", "")
                    slack_attachment = Attachment("", "")
                    header_attachment.set_content(
                        pretext="These are the currently running processes on ABB",
                        text="The processes have been broken into two groups: those that monitor reddit and those that monitor slack"
                    )
                    reddit_attachment.set_content(
                        text="These processes run loops which monitor *reddit*"
                    )
                    slack_attachment.set_content(
                        text="These processes run loops which monitor *slack*"
                    )
                    for reddit_name, reddit_info in reddit_process.items():
                        if reddit_info["process"].poll() is not None:
                            reddit_attachment.add_field(
                                title=reddit_name,
                                value="Stopped",
                                short=False
                            )
                        else:
                            reddit_attachment.add_field(
                                title=reddit_name,
                                value="Running Since: "+reddit_info["start_dt"].strftime("%b %d, %I:%M %p %Z"),
                                short=False
                            )
                    for slack_name, slack_info in slack_process.items():
                        if slack_info["process"].poll() is not None:
                            slack_attachment.add_field(
                                title=slack_name,
                                value="Stopped",
                                short=False
                            )
                        else:
                            slack_attachment.add_field(
                                title=slack_name,
                                value="Running Since: "+slack_info["start_dt"].strftime("%b %d, %I:%M %p %Z"),
                                short=False
                            )
                    messenger.add_attachment(header_attachment)
                    messenger.add_attachment(reddit_attachment)
                    messenger.add_attachment(slack_attachment)
                    messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!startProcess"):
                command = message_text.replace("!startProcess", "")
                command_args = command.split('|')
                process_args = {}
                for arg in command_args:
                    arg_parts = arg.split(':')
                    if len(arg_parts) == 2:
                        arg_name = arg_parts[0].strip().lower()
                        arg_val = arg_parts[1].strip()
                        process_args[arg_name] = arg_val
                if "name" not in process_args:
                    messenger.set_text("A name is required to start a new process")
                    messenger.send_message()
                    messenger.set_channel(message_channel)
                if "script" not in process_args:
                    messenger.set_text("A script is required to start a new process")
                    messenger.send_message()
                    messenger.set_channel(message_channel)
                popen_script = shlex.split(process_args["script"])
                if popen_script[0] != "python3" or popen_script[1].startswith("../") or popen_script[1].startswith("/") or popen_script[1].startswith("~"):
                    globals()["bot_admin_users"] = []
                    panic_attachment = Attachment("", "")
                    panic_attachment.set_content(
                        pretext="@channel An attempt to inject code into ActualBernieBot was detected from a slack user. Process management is locked until the bot is restarted.",
                        text="The information on the injection attempt is listed below."
                    )
                    panic_attachment.add_field(
                        title="From Slack User",
                        value=list(slack_users.keys())[list(slack_users.values()).index(event_data["event"]["user"])],
                        short=False
                    )
                    panic_attachment.add_field(
                        title="Attempted Command",
                        value=process_args["script"],
                        short=False
                    )
                    panic_attachment.set_color(
                        color="danger"
                    )
                    messenger.set_channel(slack_channels["bot-notifications"])
                    messenger.add_attachment(panic_attachment)
                    messenger.send_message()
                else:
                    started = start_process(process_args["name"], process_args["type"], popen_script)
                    if not started:
                        messenger.set_text("A process with that name is already running. Try !listProcesses to see which are on.")
                        messenger.send_message()
                    else:
                        messenger.set_text("Your requested process has been started.")
                        messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!killProcess"):
                name = message_text.replace("!killProcess", "").strip()
                killed = kill_process(name)
                if not killed:
                    messenger.set_text("That process isn't currently running, so I can't kill it. Try !listProcesses to see which are on.")
                    messenger.send_message()
                else:
                    messenger.set_text("The process *"+name+"* has been killed.")
                    messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!pauseProcess"):
                name = message_text.replace("!pauseProcess", "").strip()
                stopped = stop_process(name)
                if not stopped:
                    messenger.set_text("That process doesn't exist.")
                    messenger.send_message()
                else:
                    messenger.set_text("The process *"+name+"* has been paused.")
                    messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!unpauseProcess"):
                name = message_text.replace("!unpauseProcess", "").strip()
                stopped = refresh_process(name)
                if not stopped:
                    messenger.set_text("That process doesn't exist.")
                    messenger.send_message()
                else:
                    messenger.set_text("The process *"+name+"* has been unpaused.")
                    messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!restartProcess"):
                name = message_text.replace("!restartProcess", "").strip()
                restarted = restart_process(name)
                if not restarted:
                    messenger.set_text("Failed to restart process *"+name+"*. If it is in the process list, try stopping the process and starting it again.")
                    messenger.send_message()
                else:
                    messenger.set_text("Process *"+name+"* has been restarted.")
                    messenger.send_message()
                direct_processed = True
        elif message_channel.startswith("D") or mentioned_user == starterbot_id:
            messenger = SlackMessenger()
            messenger.set_channel(message_channel)
            if message_text.startswith("!queueSize"):
                item_count = 0
                for item in subreddit.mod.modqueue(limit=None):
                    item_count += 1
                messenger.set_text("The modqueue currently has *" + str(item_count) + "* items in it.")
                messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!top"):
                top_post = subreddit.top(time_filter='day', limit=1)
                reddit_link = Attachment("", "")
                for post in top_post:
                    reddit_link.set_content(
                        text="This is the current post at the top of the sub"
                    )
                    reddit_link.set_author(
                        author_name=post.author.name,
                        author_link="https://www.reddit.com/user/"+post.author.name
                    )
                    reddit_link.set_link(
                        title=post.title,
                        url=post.permalink
                    )
                messenger.add_attachment(reddit_link)
                messenger.send_message()
                direct_processed = True
            elif message_text.startswith("!controversial"):
                contro_post = subreddit.controversial(time_filter='day', limit=1)
                reddit_link = Attachment("", "")
                for post in contro_post:
                    reddit_link.set_content(
                        text="This is today's most controversial post"
                    )
                    reddit_link.set_author(
                        author_name=post.author.name,
                        author_link="https://www.reddit.com/user/"+post.author.name
                    )
                    reddit_link.set_link(
                        title=post.title,
                        url=post.permalink
                    )
                messenger.add_attachment(reddit_link)
                messenger.send_message()
                direct_processed = True
        if direct_processed is False:
            sqs.send_message(
                QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
                MessageBody=json.dumps(event_data),
                MessageGroupId="slack-event",
                MessageDeduplicationId=event_data['event_id']
            )
    else:
        sqs.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/068534578493/slackbotevent.fifo",
            MessageBody=json.dumps(event_data),
            MessageGroupId="slack-event",
            MessageDeduplicationId=event_data['event_id']
        )
    return make_response("", 200)


def start_process(name, type, popen_args):
    if name in subprocesses:
        return False
    subprocesses[name] = {
        "type": type,
        "start_dt": datetime.now(),
        "process": s.Popen(popen_args),
        "popen_args": popen_args
    }
    return True


def refresh_process(name):
    if name not in subprocesses:
        return False
    del subprocesses[name]["process"]
    subprocesses[name]["process"] = s.Popen(subprocesses[name]["popen_args"])
    if subprocesses[name]["process"].poll is not None:
        return False
    else:
        return True


def restart_process(name):
    if name not in subprocesses:
        return False
    stop_process(name)
    return refresh_process(name)


def stop_process(name):
    if name not in subprocesses:
        return False
    subprocesses[name]["process"].terminate()
    return True


def kill_process(name):
    if name not in subprocesses:
        return False
    if subprocesses[name]["process"].poll() is None:
        subprocesses[name]["process"].terminate()
        del subprocesses[name]["type"]
        del subprocesses[name]["start_dt"]
        del subprocesses[name]["process"]
        del subprocesses[name]["popen_args"]
        del subprocesses[name]
        return True
    else:
        return False


def create_user_list(next_cursor=None):
    user_list = {}
    if next_cursor is None:
        user_request = slack_client.api_call(
            'users.list'
        )
    else:
        user_request = slack_client.api_call(
            'users.list',
            cursor=next_cursor
        )
    if not user_request["ok"]:
        return user_list
    for user in user_request["members"]:
        user_list[user["name"]] = user["id"]
    if "request_metadata" in user_request and "next_cursor" in user_request["request_metadata"]:
        return {**user_list, **create_user_list(user_request["request_metadata"]["next_cursor"])}
    else:
        return user_list


def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


# Start the server on port 3000
if __name__ == "__main__":
    starterbot_id = slack_client.api_call("auth.test")["user_id"]
    channel_request = slack_client.api_call(
        "channels.list",
        exclude_archived=1
    )
    for channel_item in channel_request["channels"]:
        slack_channels[channel_item["name"]] = channel_item["id"]
        if starterbot_id in channel_item["members"]:
            slack_joined_channels.append(channel_item["name"])
    slack_users = create_user_list()
    server_process.start()
