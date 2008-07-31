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

class logRouter:
	facil={'null':()}
	def __init__(self,fac):
		if fac: self.facil = fac

	def LOG(self,entity,fac='null'):
		#There are some 'if' clauses dependng on given entity
		#type. They aims to form 'val' and 'style' variables,
		#which are then passed to logX.wr()
		if type(entity)==type(('is a tuple',)): 
			val=entity
			style='string_1'
			#there will be better if style will be chosen
			#according to len(val)
		if type(entity)==type(xmpp.Message()):
			f=entity.getFrom()
			t=entity.getTo()
			if (f or t)==f:
				#we have only "From:"
				val=(f,entity.getBody())
				style='xmpp_from'
			elif (f and t)==f:
				#here we have only "To:"
				val=(t,entity.getBody())
				style='xmpp_to'
			else:
				#either none or both "F:" & "T:"
				#will log both
				val=(t,f,entity.getBody())
				style='xmpp_both'
		for f in self.facil[fac]: f(val,style)

class logToFile:
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
			'xmpp_to':u"""<tr><td>%s</td><td>To <font color=#990000>%s</font>:</td><td>%s</td></tr>\n""",
			'xmpp_from':u"""<tr><td>%s</td><td>From <font color=#000099>%s</font>:</td><td>%s</td></tr>\n""",
			'xmpp_both':u"""<tr><td>%s</td><td>To <font color=#990000>%s</font> From <font color=#000099>%s</font>:</td><td>%s</td></tr>\n""",
			'sys':u"""<tr><td>%s</td><td>To <font size=large color=#880000>%s</font>:</td><td>%s</td></tr>\n""",
			'string_1':u"""<tr><td>%s</td><td colspan=2><font size=5 color=#880000>%s</font></td></tr>\n"""}
	def __init__(self, filename='/dev/null'):
		'''Opens and initializes log file 'filename' '''
		try:self.file=open(filename,'w')
		except IOError:
			t,v = sys.exc_info()[:2]
			print(t,v)
		except: print("Some problem occured while opening logfile for writing")
		if self.file.mode=='w': self.file.write(self.fileHeader)
		
	def __del__(self):
		'''Logs last string and closes log file'''
		if file:
#		self.file.write(self.fileFooter) now we are doing it in
#		wr()
			self.file.close()

	def wr(self,val,style='def'):
		'''Writes a tuple into file. 
		val is a tuple or anything, which will be str()`ed
		style is an index of logRecTemplate'''
		if type(val) is not type(('is a tuple',)): 
			logtxt=(str(val),)
			#trying to log anything
		else:
			logtxt=val
		logtime=time.strftime('%H:%M:%S',time.localtime(time.time()))
		if self.file.tell()!=len(self.fileHeader): self.file.seek(-len(self.fileFooter),2)
		#self.file.seek(-len(self.fileFooter),2)
		self.file.write((self.logRecTemplate[style]%((logtime,)+logtxt)).encode('utf-8'))
		self.file.write(self.fileFooter)
		self.file.flush()

class logToCon():
	'''Class-wrapper for print() '''
	logTemplate={'def':"%s"}
	#need to be developed

	def wr(self,var,style='def'):
		if type(val) is not type(('a tuple',)): 
			logtxt=(str(val),)
			#trying to log anything
		else:
			logtxt=val
		logtime=time.strftime('%H:%M:%S',time.localtime(time.time()))
		print(self.logTemplate[style]%(logtime,)+logtxt)
