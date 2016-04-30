import sys, os, re
import html
from html import HTML
import logging
import datetime
import tweepy
from tweepy import OAuthHandler
from optparse import OptionParser
from datetime import datetime
import codecs
import zipfile
import urllib2
import collections

def setupLogger():
	"""
	Sets up Python logger object
	"""
	logger = logging.getLogger("TALON")
	handler = logging.StreamHandler()
	FORMAT = "%(asctime)-8s [%(levelname)-5s] %(message)s"
	DATE_FORMAT = "%H:%M:%S"
	formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)
	return logger

def setup():
	"""
	Authenticates with Twitter with OAuth credentials and creates an instance of a Twitter API
	"""
	CONSUMER_KEY = '4S4kMhPkZ0NfRJ00sspA1sJfA'
	CONSUMER_SECRET = 'mqi3E7ELWlPCW6GzDRE8J75bJJdoFyNns1aCYK6K3bNILzLEid'
	ACCESS_KEY = '2808956111-uumNUJgW4or9oqXOZzEAwQOgEYbShImKXjZaVkv'
	ACCESS_SECRET = 'AzHHqljl4IvN20XydnIZnGpUNprjFVYIffXG3kUOfdOaR'

	logger = logging.getLogger("TALON")
	logger.info("Authenticating...")
	try:
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		api = tweepy.API(auth)
		logger.info("Successfully authenticated!")
		return tweepy.API(auth)

	except Exception, e:
		logger.error("Error authenticating to Twitter")
		logger.error(e)
		exit(0)

def getTimeline(api, username, count=20):
	"""
	Retrieves timeline of specified user

	Arguments:
		api			Instance of Twitter API
		username	Username of target
		count		# of tweets to retrieve, default 20
	Returns:
		timeline	list of STATUS objects
	"""
	logger = logging.getLogger("TALON")
	logger.info("Retrieving timeline of @%s...", username)
	try:
		timeline = api.user_timeline(screen_name=username, count=count)
		logger.info("%s tweet(s) found", len(timeline))
		return timeline

	except Exception, e:
		logger.error("Error retrieving timeline of %s", username)
		logger.error(e)

def printTimeline():
	"""
	Prints all statuses from loaded timeline
	"""
	logger = logging.getLogger("TALON")
	try:
		for status in timeline:
			printTweet(status)
		return
	except Exception, e:
		logger.error("Error printing timeline")
		logger.error(e)
		return

def printTweet(tweet):
	"""
	Prints info on statuses from user's timeline

	Arguments:
		tweet	user status object
	"""
	try:
		print "------"
		print "%-10s %s" % ("Time:", str(tweet.created_at))
		print "%-10s %s" % ("Text:", xstr(tweet.text))
		print "%-10s %s" % ("Location:", geoInfo(tweet))
		print "%-10s %s" % ("Platform:", xstr(tweet.source))
		print "%-10s %s" % ("Link:", "http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id))
		return
	except Exception, e:
		logger.error("Error printing tweet")
		logger.error(e)
		return

def printHelp():
	"""
	Prints help menu
	"""


def userInfo():
	"""
	Prints info on target account
	"""
	logger = logging.getLogger("TALON")
	try:
		print "%-8s %s" % ("Name:",timeline[0].user.name)
		print "%-8s %s" % (("Handle:", str(timeline[0].user.screen_name)))
		print "%-8s %s" % ("About: ", xstr(timeline[0].user.description))
		print "%-8s %s" % ("Location: ", xstr(timeline[0].user.location))
		print "%-8s %s" % ("Profile:", "http://twitter.com/"+timeline[0].user.screen_name)

	except Exception, e:
		print "[-] Error getting account info"
		logger.error(e)
		return

def changeUser():
	"""
	Changes target account
	"""
	logger = logging.getLogger("TALON")
	try:
		global timeline
		user = ""
		user = raw_input("Enter new username: @")
		count = raw_input("Enter count: ")
		timeline = getTimeline(api, user, count)

	except Exception, e:
		logger.error("Unable to change user account, target is still %s", options.username)
		logger.error(e)
		timeline = getTimeline(api, user, count)
		return

def dateSearch():
	logger = logging.getLogger("TALON")
	try:
		start_entry = raw_input('Enter start date (YYYY-MM-DD): ')
		end_entry = raw_input('Enter end date (YYYY-MM-DD): ')

		if validateDate(start_entry) and validateDate(end_entry):
			syear, smonth, sday = start_entry.split('-')
			eyear, emonth, eday = end_entry.split('-')
			start_date = syear + smonth + sday
			end_date = eyear + emonth + eday
			if start_date > end_date:
				logger.error("End date must come after start date")

			for status in timeline:
				date = str(status.created_at)
				current_date, time = date.split(' ');
				year, month, day = current_date.split('-', 3)
				check_date = year + month + day

				if check_date > start_date and check_date < end_date:
					printTweet(status)
					return
	except Exception, e:
		logger.error("Error performing chronological search")
		logger.error(e)
		return

def validateDate(date_text):
	logger = logging.getLogger("TALON")
	try:
		datetime.strptime(date_text, '%Y-%m-%d')
		return True
	except Exception, e:
		logger.error("One or more dates not in correct format")
		logger.error(e)
		return False

def listSearch():
	"""
	Will check the currently gathered timeline and match it against the given wordlist
	"""
	logger = logging.getLogger("TALON")
	try:
		wordlist = raw_input('Enter filename: ')
		if not os.path.isfile(wordlist):
			logger.error("%s not found", wordlist)
			return
		logger.info("Searching timeline for contents of %s...", wordlist)
		for status in timeline:
			wfile = open(wordlist, 'r')

			for word in wfile:
				word = word.strip()
				if word.lower() in status.text.lower():
					printTweet(status)
		wfile.close()

	except Exception, e:
		logger.error("Error searching timeline")
		logger.error(e)
		return

def liveSearch():
	"""
	Will check the currently gathered timeline and match it against a specified text query
	"""
	logger = logging.getLogger("TALON")
	try:
		query = ""
		while True:
			query = raw_input("Enter search query ('q 'to quit): ")
			if query == "q":
				return
			for status in timeline:
				if query.lower() in status.text.lower():
					printTweet(status)
		return

	except Exception, e:
		logger.error("Error with search query")
		logger.error(e)
		return

def getImages():
	logger = logging.getLogger("TALON")
	logger.info("Downloading images from @%s's timeline...", str(timeline[0].user.screen_name))
	try:
		i = 1
		filename = str(timeline[0].user.screen_name)+"_images.zip"
		zf = zipfile.ZipFile(filename, mode='w')
		for tweet in timeline:
			for media in tweet.entities.get("media",[{}]):
				if media.get("type",None) == "photo":
					s = 'image'
					file = '%s%d' %(s, i)
					ext = '.jpg'
					name = file + ext
					i += 1
					img = urllib2.urlopen(media['media_url'])
					localFile = open(name, 'wb')
					localFile.write(img.read())
					localFile.close()
					zf.write(name)
					os.remove(name)
		logger.info("Downloaded %d image(s)", i)
		zf.close()
		return

	except Exception, e:
		logger.error("Error downloading pictures")
		logger.error(e)
		return

def archive():
	"""
	Downloads HTML archive of currently loaded timeline
	"""
	logger = logging.getLogger("TALON")
	logger.info("Creating HTML archive of timeline...")
	try:
		table = HTML.table(header_row=['Time', 'Text', 'Location', 'Platform', 'Web Link'])

		for tweet in timeline:
			geo =geoInfo(tweet)
			if geo != "N/A":
				geo = HTML.link(geo, geoInfo(tweet, URL=True))
			webUrl = HTML.link('View on web', "http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id))

			newRow = [str(tweet.created_at), tweet.text.encode('utf-8'), geo, xstr(tweet.source),webUrl]
			table.rows.append(newRow)

		name = str(timeline[0].user.screen_name)+"_archive_"+datetime.now().strftime('%Y-%m-%d_%H%M')+".html"
		localFile = open(name, 'w')
		localFile.writelines(str(table))
		localFile.close()

		print "[+] HTML archive successfully created"
		return

	except Exception, e:
		print "[-] Error creating HTML archive from timeline"
		logger.error(e)
		return

def mentions():
	"""
	Prints most common words used in tweets
	"""
	logger = logging.getLogger("TALON")
	mentions = []
	logger.info("Gathering info on mentions...")

	try:
		for tweet in timeline:
			split = tweet.text.lower().split()
			for word in split:
				if word[0]=="@":
					mentions.append(word)
		counter = collections.Counter(mentions)
		mentions = counter.most_common()

		print "\nUser                   Qty"
		print "=========================="
		try:
			for i in range(0,10):
				print '%-20s %05s' % (str(mentions[i][0]), str(mentions[i][1]))
		except:
			logger.info("End of mentions")
		return

	except Exception, e:
		logger.error("Error getting mentions")
		logger.error(e)
		return

def geoInfo(tweet, URL=False):
	"""
	Returns short description geo info from tweet

	Arguments:
		tweet		Tweet object
		URL			bool, whether or not user wants GMaps URL returned
	"""
	try:
		if tweet.place:
			if URL:
				append = tweet.place.full_name.replace (" ", "+")
				url = "http://www.google.com/maps/place/"+append
				return url
			else:
				return tweet.place.full_name
		else:
			return "N/A"

	except Exception, e:
		logger.error("Error getting geolocation info")
		logger.error(e)
		return

def xstr(s):
	"""
	Converts null string to 'N/A'
	"""
	if s is None:
		return 'N/A'
	"""
	emoji_pattern = r'/[U0001F601-U0001F64F]/u'
	re.sub(emoji_pattern, '#', s)
	"""
	try:
		# UCS-4
		highpoints = re.compile(u'[U00010000-U0010ffff]')
	except re.error:
		# UCS-2
		highpoints = re.compile(u'[uD800-uDBFF][uDC00-uDFFF]')
	"""
	try:
		# Wide UCS-4 build
		myre = re.compile(u'['
			u'\U0001F300-\U0001F64F'
			u'\U0001F680-\U0001F6FF'
			u'\u2600-\u26FF\u2700-\u27BF]+',
			re.UNICODE)
	except re.error:
		# Narrow UCS-2 build
		myre = re.compile(u'('
			u'\ud83c[\udf00-\udfff]|'
			u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
			u'[\u2600-\u26FF\u2700-\u27BF])+',
			re.UNICODE)
	#re.sub(highpoints, '', s)
	"""
	return s.encode('utf-8')

def clear():
	os.system('cls' if os.name == 'nt' else 'clear')

def main():

	menu =  {'archive':[archive,"Downloads HTML archive of loaded timeline"],
				'clear':[clear,"Clears the terminal"],
				'date':[dateSearch,"Find tweets in certain date ranges"],
				'exit':[exit,"Exits the program"],
				'help':[printHelp,"Prints this help list"],
				'list':[listSearch,"Compare timeline against a given wordlist"],
				'live':[liveSearch,"Interactive live search for specific queries"],
				'media':[getImages,"Download ZIP archive of images posted by user"],
				'mentions':[mentions,"Find most frequently contacted users"],
				'new':[changeUser,"Change target account"],
				'print':[printTimeline,"Prints timeline"],
				'user':[userInfo,"Prints basic user info"],
				#'advanced':advanced, "Prints advanced user info"]
				}

	logger = setupLogger()

	parser = OptionParser(usage="usage: %prog -u <username>", version="%prog 1.0")
	parser.add_option("-u", "--username", dest="username", help="Twitter username of target account")
	parser.add_option("-c", "--count", dest="count", help="Number of tweets to retrieve (default of 20)")
	(options, args) = parser.parse_args()

	if not options.username:
		parser.print_help(menu)
		exit(0)

	global api, timeline
	api = setup()
	timeline = getTimeline(api, options.username, options.count)

	while True:
		command = raw_input(">>> ")
		if command == 'help':
			print "-" * 24
			for function in menu.keys():
				print "%-10s %s" % (function, menu[function][1])
			print "-" * 24
		elif command in menu.keys():
			menu[command][0]()
		else:
			print "Invalid command"

if __name__ == "__main__":
	main()
