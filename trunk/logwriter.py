import sys
import time
import xmpp
import types


def getXMPPStanzaTime(stanza):
	ts=stanza.getTimestamp()
	if not ts:
		ts=stanza.setTimestamp()
		ts=stanza.getTimestamp()
#	print(ts)
	tp=time.mktime(time.strptime(ts,'%Y%m%dT%H:%M:%S'))
	#got the local time in py-useable form from stanza
	if not time.daylight: 
		tp=tp-time.timezone 
	else:
		tp=tp-time.altzone
	# tp is in seconds in UTC now
	return tp
	#tp=time.localtime(tp)
	#tp is a tuple
	#day=time.strftime("%d",tp)
	#tm=time.strftime("%H:%M:%S",tp)
 

class logClass:
	fileHeader='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="ru-RU" lang="ru-RU" xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta content="text/html; charset=utf-8" http-equiv="content-type" />
</head>
<body>
	<table border="1" cellspacing=0 cellpadding=1><tr><th>time</th><th>who</th><th>text</th></tr>\n'''
	fileFooter='''    </table>
</body>
</html>'''
	logRecTemplate={'def':u"""<tr><td>%s</td><td>To <font color=#000088>%s</font>:</td><td>%s</td></tr>\n""",
			'xmpp':u"""<tr><td>%s</td><td>To <font color=#008800>%s</font>:</td><td>%s</td></tr>\n""",
			'sys':u"""<tr><td>%s</td><td>To <font size=large color=#880000>%s</font>:</td><td>%s</td></tr>\n"""}

	def __init__(self, filename='/dev/null'):
		'''Opens and initializes log file 'filename' '''
		try:self.file=open(filename,'w')
		except IOError:
			t,v,tb = sys.exc_info()
			print(t,v,tb)
		except: print("Some problem occured while opening file")
		self.file.write(self.fileHeader)
		
	def __del__(self):
		'''Logs last string and closes log file'''
		if file:
			self.file.write(self.fileFooter)
			self.file.close()

	def wrTxt(self,src,text,style='def'):
		'''Writes a text log message into file. 
		Src is a readable message source,
		text is a tuple or single string,
		style is an index of logRecTemplate'''
		if type(text) is not types.TupleType: 
			logtxt=(text,)
#			print('text accepted')
		else:
			logtxt=text
		logtime=time.strftime('%H:%M:%S',time.localtime(time.time()))
#		print(logtime)
#		print(self.logRecTemplate[style])
#		print((logtime,src))
#		print("%s qweqew %s 123123 %s"%((logtime,src)+logtxt))
		#print((logtime,src)+logtxt)
		self.file.write((self.logRecTemplate[style]%((logtime,src)+logtxt)).encode('utf-8'))
		self.file.flush()

	def wrXMPPStanza(self,stanza,style='xmpp'): 
		'''Logs XMPP stanza into file.
		Must have xmpp module.
		style is an index of logRecTemplate'''
		logtime=time.strftime('%H:%M:%S',time.localtime(getXMPPStanzaTime(stanza)))
		self.file.write((self.logRecTemplate[style]%(logtime,stanza.getFrom(),stanza.getBody())).encode('utf-8'))
		self.file.flush()

