# coding=utf-8
import os
import re
import sys
import time
import json
import urllib
import urllib2
import feedparser
import requests
import argparse
import threading
import schedule
#import logging


class MONEYE:
	def __init__(self):
		self.target = "http://www.example.com/"
		self.TodayNotFound = True


	def run(self):
		f = open('fetchPageException.log','w')
		while True:
			time.sleep(10)
			if self.TodayNotFound:
				try:
					self.fetchPageAndGrepDate()
				except Exception as e:
					f.write(e)



	def restoreTodayNotFound(self):
		t = time.localtime()
		t = time.mktime(t[:3] + (0,0,0) + t[6:])
		time.sleep(t + 24*3600 - time.time())
		self.TodayNotFound = True



	def fetchPageAndGrepDate(self):
		def findAInfo(post):
			html = post.content[0]['value']			 
			paragraph = html[html.find("</a>"):]

			pattern = re.compile(ur"([\u4e00-\u9fa5]+)")    
			a = re.findall(pattern,paragraph)[0]    

			a_url = re.search("(?P<url>https?://[^\s]+)", paragraph).group("url")   
			a_url_no_dot = a_url.replace(".","+")[7:]      

			t = html[html.find("https://"):]		 
			t = t[:t.find("JPG")]
			t = t[t.find(":"):]
			picture_evidence_url =  "http"+ t +"JPG"
			local_filename = "evidence.JPG"
			urllib.urlretrieve(picture_evidence_url, local_filename)   

			return a, a_url_no_dot

		print "Start of fetchPageAndGrepDate().."
		print "sysdefault:",sys.getdefaultencoding()
		try:
			if self.isTest:
				proxy = urllib2.ProxyHandler( {"http":"http://127.0.0.1:1080/"})
				d = feedparser.parse(self.target,handlers = [proxy])
			else:
				d = feedparser.parse(self.target)				 
		except:
			print "[WARNING]["+time.strftime('%m-%d %H:%M')+"] Might be proxy error, feedparser can not connect to target!\n"
			return
		count = 1
		current_timestamp = time.strftime("%Y",time.localtime()) + u"年" + time.strftime("%m",time.localtime()).lstrip('0') + u"月" + time.strftime("%d",time.localtime()).lstrip('0') + u"日"	#lstrip('0')去掉月份里多余的0
		
		for post in d.entries:
			if count % 5 == 0:					
				break
			else:
				count+=1
			
			if current_timestamp in post.title:
				print "[MAIN]Todays intrusion found, initializing grepping process."
				print "ALERT!, "+post.title + "\n"
				a_info = findAInfo(post)
				
				print "Sending SMS..."
				self.sendSMS(a_info[0],a_info[1])
				print "Sending Mail..."
				try:
					self.sendMail(a_info[0],a_info[1],local_filename)			 
				except UnicodeEncodeError:
					print UnicodeDecodeError
					pass
				print "[MAIN] SMS and Mail dispatched, setting TodayNotFound to False."
				self.TodayNotFound = False


	def sendMail(self,a,a_url,picture_filename):
		params = {"apiUser": "xxxUser", \
		"apiKey" : "xxxkey",\
		"from" : "xxx@organization.com", \
		"fromname" : "发件人", \
		"to" : "x@x.com", \
		"subject" : "1"+a+"于"+time.strftime('%Y-%m-%d %H:%M')+"发生XX.", \
		"html": "event_site: "+a_url, \
		"resp_email_id": "true",\
		"bcc":"y@y.com;",\
		"attachments":"e.jpg"
		}
		url="https://www.xxx.net/apiv2/mail/send?"+urllib.urlencode(params)
		r = requests.post(url,files={'Filename':picture_filename,'attachments':('evidence.jpg',open(os.getcwd()+"\\"+picture_filename,'rb'),'image/jpeg')})
		print "sendMail Reponse:\n"+r.text
		print "sendMail Ends ----------------------------------------"



	def sendSMS(self,a,a_url):
		time_point = time.strftime('%Y-%m-%d %H:%M')
		data = {'name':a,'website':a_url,'time':time_point}
		url = "http://c.com/?a=b"+urllib.quote(json.dumps(data))
		
		req = urllib2.Request(url)
		req.add_header('X-Ca-Key', 'key')
		req.add_header("X-Ca-Secret", "secret")
		res = urllib2.urlopen(req)
		print res.read().decode('utf-8')


if __name__ == "__main__":
	MONEYE().run()