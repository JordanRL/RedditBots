import time
import hashlib
import datetime
import settings
import requests

def check_age(submission):
	#Checks if age is < MAX_REMEMBER_LIMIT
	return get_submission_age(submission).days < settings.MAX_REMEMBER_LIMIT

def get_submission_age(submission):
	#Returns a delta time object from the difference of the current time and the submission creation time
	current_date = datetime.datetime.utcfromtimestamp(time.time())
	submission_date = datetime.datetime.utcfromtimestamp(submission.created_utc)
	return current_date - submission_date

def initialise_link_array(reddit):
	#Initialises the link array of all past submissions
	#No need to check about removing older posts, since we do that before checking in the main loop anyway
	list = []
	for submission in reddit.subreddit(settings.REDDIT_SUBREDDIT).new(limit=None):
		if check_age(submission):
			list = check_list(submission, list)
	return list

def check_list(submission, list):
	#Check if a submission url is in the list
	#If it is, remove it from the subreddit
	#If not, add it to the list
	if check_url(submission.url) not in [check_url(sub.url) for sub in list] or submission in list:
		list.append(submission)
	else:
		print("Removing {}".format(submission.url))
		submission.reply(open(settings.REPLY_MESSAGE_LOCATION, "r+").read())
		submission.mod.remove()
	return list

def purge_old_links(list):
	#Removes links older than settings.MAX_REMEMBER_LIMIT from the queue
	for submission in list:
		if get_submission_age(submission).days > settings.MAX_REMEMBER_LIMIT:
			list.remove(submission)
	return list

def check_url(url):
	response = requests.get(url)
	m = hashlib.md5()
	m.update(response.text[1024].encode("utf-8"))
	return m.digest()