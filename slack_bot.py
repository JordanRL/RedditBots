import os
import time
import re
import praw
import settings
import pprint
from attachmentBuilder import Attachment
from slack_messenger import SlackMessenger
from datetime import datetime
from slackclient import SlackClient

reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

channel_list = {}
joined_channels = []
active_votes = {}


def parse_bot_commands(slack_events):
    """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            if event["channel"].startswith('D'):
                return event["text"], event["channel"]
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format('help')

    # Finds and executes the given command, filling in response
    response = None
    response_sent = False
    # This is where you start to implement more commands!
    if command.startswith('!help'):
        response = "These are the commands available right now: !help, !time, !queueSize, !testComplex"
    elif command.startswith('!time'):
        response = datetime.now().timetz().isoformat()
    elif command.startswith('!queueSize'):
        print('Calculating Queue Size')
        item_count = 0
        for item in subreddit.mod.modqueue(limit=None):
            item_count += 1
        messenger = SlackMessenger()
        response = "The modqueue currently has *"+str(item_count)+"* items in it."
        result = messenger.set_text(response).set_channel(channel).send_message()
        if result:
            print('Queue Size Sent')
        else:
            print('Problem Sending Queue Size')
        response_sent = True
    elif command.startswith('!testComplex'):
        print('Building Complex')
        messenger = SlackMessenger(slack_client)
        attachment = Attachment("This should test a more complex message", "This should test a more complex message")
        attachment.set_author(
            author_name="JordanLeDoux",
            author_link="https://www.reddit.com/user/JordanLeDoux"
        )
        attachment.set_content(
            text="This should test a more complex message",
            pretext="A test message now"
        )
        attachment.set_color(
            color="good"
        )
        attachment.set_footer(
            footer="Provided By ActualBernieBot"
        )
        result = messenger.post_attachment(attachment, channel)
        if result:
            print('Complex Sent')
        else:
            print('Problem Sending Complex')
        response_sent = True
    elif command.startswith('!postQuote'):
        if "random" not in joined_channels:
            slack_client.api_call(
                "channels.join",
                channel=channel_list["random"]
            )
        response = "I was told to post a quote here, but I'm not an intelligent bot yet..."
        channel = channel_list["random"]
    elif command.startswith('!banVote'):
        command = command.replace('!banVote', '')
        command_args = command.split('|')
        ban_args = {}
        for arg in command_args:
            arg_parts = arg.split(':')
            arg_name = arg_parts[0].strip().lower()
            arg_val = arg_parts[1].strip().lower()
            ban_args[arg_name] = arg_val
        if "user" not in ban_args:
            response = "The !banVote command requires a user parameter in this format: !banVote User: username | ..."
        if "type" not in ban_args:
            response = "The !banVote command requires a type parameter in this format: !banvote Type: temp | ..."
        elif ban_args["type"] == "temp":
            ban_args["type_readable"] = "Temporary"
        elif ban_args["type"] == "perm":
            ban_args["type_readable"] = "Permanent"
        if response is None:
            username = ban_args['user']
            pretext = "A vote to ban has been called"
            text = "Please vote"
            actions = [
                {
                    'name': 'ban',
                    'text': 'Permaban (Requested)',
                    'type': 'button',
                    'value': 'permaban',
                    'style': 'danger',
                    'confirm': {
                        "title": "Are you sure?",
                        "text": "This will permanently ban this user if the vote passes.",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                },
                {
                    'name': 'ban',
                    'text': 'Tempban (Default: 2 Days)',
                    'type': 'button',
                    'value': 'tempban'
                },
                {
                    'name': 'ban',
                    'text': 'Warn Via PM (Using Cited Rules)',
                    'type': 'button',
                    'value': 'warn'
                },
                {
                    'name': 'ban',
                    'text': 'No Action',
                    'type': 'button',
                    'value': 'none'
                }
            ]
            fields = [
                {
                    'title': 'Duration',
                    'value': ban_args["type_readable"],
                    'short': True
                }
            ]
            color = "danger"
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                callback_id="vote_button",
                attachments=[
                    {
                        "author_name": username,
                        "author_link": "https://www.reddit.com/user/" + username,
                        "pretext": pretext,
                        "text": text,
                        "actions": actions,
                        "fields": fields,
                        "color": color,
                        "mrkdwn_in": ["pretext", "text", "fields"],
                        "footer": "Provided By ActualBernieBot"
                    }
                ]
            )
            #response = "I will call a vote to ban *"+ban_args["user"]+"* with a *"+ban_args["type_readable"]+"* ban"

    # Sends the response back to the channel
    if not response_sent:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response
        )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
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
        print('Startup complete. Listening for events.')
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                print('Command Received: '+command+' in '+channel)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")