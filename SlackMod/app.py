# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import bot
import re
from flask import Flask, request, make_response, render_template

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)

actionVotes = {}

def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.
    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event
    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error
    """
    team_id = slack_event["team_id"]
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        # Send the onboarding message
        pyBot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200,)

    # =========== Message Channels Events ============= #
    elif event_type == "message.channels":
        channel_info = pyBot.channel_info(slack_event["event"]["item"]["channel"])

        # User Actions
        if channel_info["channel"]["name"] == "discipline":
            message = slack_event["event"]["text"]
            # The matching patterns
            searchExpr = r"User: (.*?) \| (.*?) | Threshold: ([0-9].?)"
            searchObj = re.search(searchExpr, message)
            if searchObj is not None:
                actionVotes[slack_event["event"]["ts"]+"_"+slack_event["event"]["channel"]] = {"user": searchObj.group(1),
                                                                                               "threshold": searchObj.group(3),
                                                                                               "confirm": 0,
                                                                                               "permaban": 0,
                                                                                               "tempban": 0}
                replyMessage = "Discipline Vote Called | :banhammer: = Permaban | :timer: = Tempban (2-days) | :exclamation: = Warn"
                replyAttachments = [
                    {
                        "title": searchObj.group(1),
                        "title_link": "https://www.reddit.com/user/"+searchObj.group(1),
                        "text": "Please provide quotes from the user in this thread",
                        "fields": [
                            {
                                "title": "Suggested Action",
                                "value": searchObj.group(2),
                                "short": 1
                            },
                            {
                                "title": "Action Threshold",
                                "value": searchObj.group(3),
                                "short": 1
                            }
                        ]
                    }
                ]
                pyBot.add_reply_attachments(slack_event["event"]["ts"],
                                            slack_event["event"]["channel"],
                                            replyMessage,
                                            replyAttachments)

        # Thread Actions
        elif channel_info["channel"]["name"] == "danger-room":
            message = slack_event["event"]["text"]


    # ============= Reaction Added Events ============= #
    elif event_type == "reaction_added":
        channel_info = pyBot.channel_info(slack_event["event"]["item"]["channel"])

        if channel_info["channel"]["name"] == "discipline":
            if slack_event[""]
        return make_response("Welcome message updates with reactji", 200,)

    # =============== Pin Added Events ================ #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "pin_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_pin(team_id, user_id)
        return make_response("Welcome message updates with pin", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)