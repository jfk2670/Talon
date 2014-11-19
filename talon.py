import sys, os, re
#import HTML
import tweepy
from tweepy import OAuthHandler
from optparse import OptionParser
import codecs
import zipfile
import urllib2

def setup():
	"""
	Authenticates with Twitter with OAuth credentials and creates an instance of a Twitter API
	"""
	CONSUMER_KEY = '4S4kMhPkZ0NfRJ00sspA1sJfA'
	CONSUMER_SECRET = 'mqi3E7ELWlPCW6GzDRE8J75bJJdoFyNns1aCYK6K3bNILzLEid'
	ACCESS_KEY = '2808956111-uumNUJgW4or9oqXOZzEAwQOgEYbShImKXjZaVkv'
	ACCESS_SECRET = 'AzHHqljl4IvN20XydnIZnGpUNprjFVYIffXG3kUOfdOaR'

	print "[+] Authenticating..."
	try:
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		api = tweepy.API(auth)
		print "[+] Successfully authenticated!"
		return tweepy.API(auth)
		
	except Exception, e:
		print "[-] Error authenticating to Twitter:"
		print e
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
	print "[+] Retrieving timeline of @%s..."%username
	try:
		timeline = api.user_timeline(screen_name=username, count=count)
		print "[+] %s tweet(s) found"%len(timeline)
		return timeline
		
	except Exception, e:
		print "[-] Error retrieving timeline:"
		print e
		exit(0)
		
def printTimeline():
	"""
	Prints all statuses from loaded timeline
	"""
	try:
		for status in timeline:
			printTweet(status)
		return
	except:
		print "[-] Error printing timeline"

def printTweet(tweet):
	"""
	Prints info on statuses from user's timeline
	
	Arguments:
		tweet	user status object
	"""
	try:
		print "----"
		print "[+] Time:      "+str(tweet.created_at)
		print "[+] Text:      "+tweet.text
		#print "[+] Location:  "+xstr(tweet.place.name)
		print "[+] Sent from: "+xstr(tweet.source)
		print "[+] URL:       http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id)
		return
	except:
		print "[-] Error printing tweet"
		return
	
def printHelp():
	"""
	Prints help menu
	"""	
	print "Command         Description"
	print "-" * 27
	#print "advanced........Prints advanced user info"			#toBeImplemented
	print "exit............Exit"
	print "help............Print help"
	#print "html............Download timeline to html file"		#toBeImplemented
	print "list............Compare timeline against wordlist"
	print "live............Interactive search for specified query"
	print "media...........Downloads and zips photos from timeline"
	print "new.............Change target account"				
	print "print...........Print currently loaded timeline"	
	print "user............Prints basic user info"

def userInfo():
	"""
	Prints info on target account
	"""
	try:
		print "[+] Name: "+str(timeline[0].user.name)
		print "[+] Handle: "+str(timeline[0].user.screen_name)
		print "[+] About: "+xstr(timeline[0].user.description)
		print "[+] Location: "+xstr(timeline[0].user.location)
		print "[+] Profile Link: http://twitter.com/"+timeline[0].user.screen_name
	except Exception, e:
		print "[-] Error getting account info"
		print e

def changeUser():
	"""
	Changes target account
	"""
	try:
		global timeline
		user = ""
		user = raw_input("Enter new username: @")
		count = raw_input("Enter count: ")
		timeline = getTimeline(api, user, count)
	except Exception, e:
		print "[-] Unable to change user account"
		print e
	
def listSearch():
	"""
	Will check the currently gathered timeline and match it against the specified wordlist
	"""
	
	path = ""
	while True:
		path = raw_input("Enter wordlist path: ")
		
		if os.path.isfile(path):
			break
		else:
			print "[-] Error opening file"
	
	print "here"
	try:
		print "[+] Searching timeline for contents of %s..."%path
		wfile = open(path, 'r')
		print "opened file"
		for status in timeline:
			#wfile = open(wordlist, 'r')
			print status.text.lower()
			for word in wfile:
				word = word.strip()
				if word.lower() in status.text.lower():
					#print status.text.lower()
					printTweet(status)
		wfile.close()
		return
	except:
		print "[-] Error searching timeline"
		return
	
def liveSearch():
	"""
	Will check the currently gathered timeline and match it against a specified text query
	"""
	
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
		print "[-] Error with search query"
		print e

def xstr(s):
	"""
	Converts null string to 'N/A'
	"""
	if s is None:
		return 'N/A'
	return str(s)

def getImages():
	print "[+] Downloading images from @%s's timeline..."%str(timeline[0].user.screen_name)
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
		print "[+] Downloaded %d image(s)"%i
		zf.close()
		return
	except Exception, e:
		print "[-] Error downloading pictures"
		print e
		return

def main():

	parser = OptionParser(usage="usage: %prog -u <username>", version="%prog 1.0")
	parser.add_option("-u", "--username", dest="username", help="Twitter username of target account")
	parser.add_option("-c", "--count", dest="count", help="Number of tweets to retrieve (default of 20)")
	(options, args) = parser.parse_args()
	
	if not options.username:
		parser.print_help()
		exit(0)
	
	methodIndex =  {'exit':exit,
					'help':printHelp,
					'list':listSearch,
					'live':liveSearch,
					'media':getImages,
					'new':changeUser,
					'print':printTimeline,
					'user':userInfo
					}
	
	global api, timeline	
	api = setup()
	timeline = getTimeline(api, options.username, options.count)

	#if options.wordlist:
	#	getWordList(options.wordlist)
	
	while True:
		command = raw_input(">>> ")
		
		if command in methodIndex.keys():		
			methodIndex[command]()
		else:
			print "Invalid command"
	
if __name__ == "__main__":
	main()
