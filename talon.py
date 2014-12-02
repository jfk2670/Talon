import sys, os, re
import HTML
import tweepy
from tweepy import OAuthHandler
from optparse import OptionParser
import codecs
import zipfile
import urllib2
import collections

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

def getTimeline(api, username, count=20, verbose=True):
	"""
	Retrieves timeline of specified user
	
	Arguments:
		api			Instance of Twitter API
		username	Username of target
		count		# of tweets to retrieve, default 20
	Returns:
		timeline	list of STATUS objects
	"""
	if verbose == True:
		print "[+] Retrieving timeline of @%s..."%username
	try:
		timeline = api.user_timeline(screen_name=username, count=count)
		if verbose == True:
			print "[+] %s tweet(s) found"%len(timeline)
		return timeline
		
	except Exception, e:
		print "[-] Error retrieving timeline of "+username
		print e
		
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
		print "[+] Location:  "+geoInfo(tweet, URL=False)
		print "[+] Sent from: "+xstr(tweet.source)
		print "[+] Link:       http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id)
		return
	except:
		print "[-] Error printing tweet"
		return
	
def printHelp():
	"""
	Prints help menu
	"""	
	print "-" * 27
	print "Command         Description"
	print "-" * 27
	print "archive" 	 + " " * 9 + "Downloads HTML archive of loaded timeline"
	print "clear"	 + " " * 11 + "Clears the terminal"
	print "date"	 + " " * 12 + "Find tweets in certain date ranges"
	print "exit" 	 + " " * 12 + "Exits the program"
	print "help" 	 + " " * 12 + "Prints this help list"
	#print "html" 	 + " " * 12 + "Download timeline to an html file"		
	print "live" 	 + " " * 12 + "Interactive live search for specific queries"
	print "match" 	 + " " * 11 + "Compare timeline against a given wordlist"
	print "mentions" 	 + " " * 8 + "Find most frequently contacted users"
	print "new" 	 + " " * 13 + "Change target account"				
	print "user" 	 + " " * 12 + "Prints basic user info"
	#print "advanced" + " " * 8  + "Prints advanced user info"			
	print "zip" 	 + " " * 13 + "Download and zip timeline"

def userInfo():
	"""
	Prints info on target account
	"""
	try:
		print "[+] Name: "+timeline[0].user.name
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
		print "[-] Unable to change user account, target is still"+options.username
		print e
		timeline = getTimeline(api, user, count, verbose=False)

def dateSearch():
	start_entry = raw_input('Enter start date (YYYY-MM-DD): ')
	end_entry = raw_input('Enter end data (YYYY-MM-DD): ')

	syear, smonth, sday = start_entry.split('-')
	eyear, emonth, eday = end_entry.split('-')
	start_date = syear + smonth + sday
	end_date = eyear + emonth + eday

	for status in timeline:
		date = str(status.created_at)
		current_date, time = date.split(' ');
		year, month, day = current_date.split('-', 3)
		check_date = year + month + day

		if check_date > start_date and check_date < end_date:
			printTweet(status)
		
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

	try:
		print "[+] Searching timeline for contents of %s..."%path
		wfile = open(path, 'r')
		for status in timeline:
			#wfile = open(wordlist, 'r')
			for word in wfile:
				word = word.strip()
				print word
				if word.lower() in status.text.lower():
					print status.text.lower()
					#print "MATCH"
					#printTweet(status)
		wfile.close()
		return
	except Exception, e:
		print "[-] Error searching timeline"
		print e
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

def archive():
	"""
	Downloads HTML archive of currently loaded timeline
	"""
	print "[+] Creating HTML archive of timeline..."
	
	try:
		table = HTML.Table(header_row=['Time', 'Text', 'Location', 'Platform', 'Web Link'])
		
		for tweet in timeline:
			geo =geoInfo(tweet)
			if geo != "N/A":
				geo = HTML.link(geo, geoInfo(tweet, URL=True))
			webUrl = HTML.link('View on web', "http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id))
			
			newRow = [str(tweet.created_at), tweet.text, geo, xstr(tweet.source),webUrl]
			table.rows.append(newRow)
		
		name = str(timeline[0].user.screen_name)+"_archive.html"
		localFile = open(name, 'w')
		localFile.writelines(str(table))
		localFile.close()
		print "[+] HTML archive successfully created"
		return
		
	except Exception, e:
		print "[-] Error creating HTML archive from timeline"
		print e
								
		
def mentions():
	"""
	Prints most common words used in tweets
	"""
	mentions = []
	print "[+] Gathering info on mentions..."
	
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
			print "[+] End of mentions"
		return
	except:
		print "[-] Error getting mentions"
	
def xstr(s):
	"""
	Converts null string to 'N/A'
	"""
	if s is None:
		return 'N/A'
	try:
		# UCS-4
		highpoints = re.compile(u'[\U00010000-\U0010ffff]')
	except re.error:
		# UCS-2
		highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
	s = highpoints.sub(u'\u25FD', s)
	return str(s)	
	
def clear():
	os.system('cls' if os.name == 'nt' else 'clear')
	
def geoInfo(tweet, URL=False):
	if tweet.place:
		if URL:
			append = tweet.place.full_name.replace (" ", "+")
			url = "http://www.google.com/maps/place/"+append
			return url
		else:
			return tweet.place.full_name
	else:
		return "N/A"

def main():

	parser = OptionParser(usage="usage: %prog -u <username>", version="%prog 1.0")
	parser.add_option("-u", "--username", dest="username", help="Twitter username of target account")
	parser.add_option("-c", "--count", dest="count", help="Number of tweets to retrieve (default of 20)")
	(options, args) = parser.parse_args()
	
	if not options.username:
		parser.print_help()
		exit(0)
	
	methodIndex =  {'archive':archive,
					'clear':clear,
					'date':dateSearch,
					'exit':exit,
					'help':printHelp,
					'list':listSearch,
					'live':liveSearch,
					'media':getImages,
					'mentions':mentions,
					'new':changeUser,
					'print':printTimeline,
					'user':userInfo,
					}
	
	global api, timeline	
	api = setup()
	timeline = getTimeline(api, options.username, options.count)
	
	while True:
		command = raw_input(">>> ")
		
		if command in methodIndex.keys():		
			methodIndex[command]()
		else:
			print "Invalid command"
	
if __name__ == "__main__":
	main()

	
