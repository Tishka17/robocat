#!/usr/bin/python
# -*- coding: utf8 -*-

# robocat.py
# RoboCat is a simple jabber bot. It's rather stupid now, but probably will be cleverer later
# Copyright (C) 2008 Tikhonov Andrey aka Tishka17 
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import sys
import xmpp
import random
import re
import time
import afisha,mirkino #2 kino schedule getting libraries
import wiki2txt 
import os
import logwriter
from logwriter import *

if len(sys.argv)<3:
	print "Usage: bot.py username@server.net password"
	sys.exit()
else:
	jid=xmpp.JID(sys.argv[1])
	user,server,resource,password=jid.getNode(),jid.getDomain(),jid.getResource(),sys.argv[2]

	conn=xmpp.Client(server,debug=[])

CONFERENCES={}
#CONFERENCES={u'livejournal@conference.jabber.ru':'',u'кит@conference.psihaven.com':''}
PROXY={}
#PROXY={'host':'http://proxy.ufanet.ru','port':3128}
#PROXY={'host':'192.168.0.1','port':3128,'username':'tishka17','password':'secret'}
ADMINS=[u'tishka17@jabber.ufanet.ru',u'lapin@psihaven.com',u'robocat@psihaven.com']
IGNORE=[u'chat@conference.jabber.ufanet.ru/kenny',u'chat@conference.jabber.ufanet.ru/alengina',u'chat@conference.jabber.ufanet.ru/Metalcore']
COMMANDS={}
LogFileName='../Bot.log.html'
LogFile='../Bot.log0.html'
#LogFile='/media/data/www/BotLog.html'

Greetings=0
Echo=0
MaxChatReply=400
MaxReply=2000

random.seed()
########################### user handlers start ##################################

SimpleAnswer={u'привет':u"Привет! На пиво нет?"}
SimpleAnswer[u'спасибо']=u'Спасибо в стакан не нальешь!'
SimpleAnswer[u'пока всем']=u'Бай бай бэби гуд бай'
SimpleAnswer[u'всем пока']=u'Гуд бай май лав гуд бай'
SimpleAnswer[u'хай']=u'Хайль!'
SimpleAnswer[u'здраст']=u'Здрастхвщ, чего?'
SimpleAnswer[u'ааа']=u'ага!'
SimpleAnswer[u'спокойной ночи']=u'сладких снов, котеночек....'
SimpleAnswer[u'кто такой']=u'хрен моржовый!'
SimpleAnswer[u'аська']=u'Смерть быдлоаське!'
SimpleAnswer[u'айсик']=u'Смерть быдлоаське!'
SimpleAnswer[u'icq']=u'Смерть быдлоаське!'
SimpleAnswer[u'винда']=u'Вендекапец!!!'
SimpleAnswer[u'windows']=u'Вендекапец'
SimpleAnswer[u'хз']=u'хз - хуй знает. Хуй все знает, да молчит...'
SimpleAnswer[u'х.з']=u'х.з - хуй знает. Хуй все знает, да молчит...'

def DoSimpleAnswer(user,command,args,mess):
	text=mess.getBody().lower()
	answer=u''
	for i in SimpleAnswer: 
		if text.find(i)>-1: 
			if answer==u'': answer=SimpleAnswer[i]
			else: answer=answer+u' '+SimpleAnswer[i]
	return answer
	
def JoinConf(CONF):
	if CONF in CONFERENCES:
		secret=CONFERENCES[CONF]
	else:
		secret=''
		CONFERENCES[CONF]=''
	p=xmpp.protocol.Presence(to='%s/%s'%(CONF,jid.getResource()))
	p.setTag('x',namespace=xmpp.protocol.NS_MUC).setTagData('password',secret)
	p.getTag('x').addChild('history',{'maxchars':'0','maxstanzas':'0'})
	conn.send(p)

	if Greetings:
		rnd=random.randrange(1,5)
		if rnd==1:    conn.send(xmpp.Message(xmpp.JID(CONF),u'Всем приветик!',typ='groupchat'))
		elif rnd==2:    conn.send(xmpp.Message(xmpp.JID(CONF),u'Хеллоу всем!',typ='groupchat'))
		elif rnd==3:    conn.send(xmpp.Message(xmpp.JID(CONF),u'Всем мяу!',typ='groupchat'))
		elif rnd==4:    conn.send(xmpp.Message(xmpp.JID(CONF),u'Здравствуйте все!',typ='groupchat'))
	if Echo:	
		now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
		print now+u'Conference %s entered'%CONF
	logger.wrTxt('%ROBOCAT%',u'Conference %s entered'%CONF,'sys')
#	LOG(time.time(),u'',u'Conference %s entered'%CONF,-1)

def LeaveConf(CONF):
	p=xmpp.protocol.Presence(to='%s'%(CONF),typ='unavailable')
	conn.send(p)
	if Echo:	
		now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
		print now+u'Conference %s left'%CONF
	logger.wrTxt('%ROBOCAT%',u'Conference %s left'%CONF,'sys')
#	LOG(time.time(),u'',u'Conference %s left'%CONF,-1)
	
def JoinHandler(user,command,args,mess):
	try: 
		JoinConf(args)
		return u'Захожу в конференцию %s'%args
	except:
		return u'Не могу зайти в конференцию %s'%args

def LeaveHandler(user,command,args,mess):
	try: 
		LeaveConf(args)
		return u'Выхожу из конференции %s'%args
	except:
		return u'Не могу выйти из конференции %s'%args

def SendHandler(user,command,args,mess):
	ls=re.split('^\s*(.*?)\s(.*)\s*',args)
	if len(ls)>2:
		t=ls[1]
		m=ls[2]
		now=time.strftime(u'%H:%M>',time.localtime(time.time()))
		mess1=xmpp.Message(xmpp.JID(t),m,typ='chat')
		#LOG(mess1,t,m,1)
		logger.wrXMPPStanza(mess1)
		if Echo:
			print now,t,u'<--',m
		conn.send(mess1)
		return u'Сообщение отправлено пользователю %s'%t
	else:
		return u'Вы не указали получателя или текст соообщения'

def helpHandler(user,command,args,mess):
	lst=[]
	if args in COMMANDS :
		if not (COMMANDS[args][1]) or (user.getStripped() in ADMINS or user.__str__() in ADMINS):
			return COMMANDS[args][2]
	for i in COMMANDS:
		if not (COMMANDS[i][1]) or (user.getStripped() in ADMINS or user.__str__() in ADMINS):
			lst=lst+[i]
	return u'Доступны следующие команды: '+u', '.join(lst)+u'\nПодробнее: справка имя_команды'

def testHandler(user,command,args,mess):
    return u'Вас проверили'


def exitHandler(user,command,args,mess):
	return u'До свидания!'

def talk(user,command,args,mess):
	rnd=random.randrange(1,5)
	if rnd==1: return u'Куку'
	if rnd==2: return u'Мяу'
	if rnd==3: return u'Ну и че ты сюда пишешь?'
	if rnd==4: return u'Тебе делать нечего?'

def LOG(stanza,nick,text,to=0):
    if type(stanza)==type(time.time()):
    	tm=time.strftime("%H:%M:%S",time.localtime(stanza))
    elif to>-1:
    	ts=stanza.getTimestamp()
    	if not ts:
		ts=stanza.setTimestamp()
		ts=stanza.getTimestamp()
    	tp=time.mktime(time.strptime(ts,'%Y%m%dT%H:%M:%S'))+3600*5
    	if time.localtime()[-1]: tp+=3600
    	tp=time.localtime(tp)
    	day=time.strftime("%d",tp)
    	tm=time.strftime("%H:%M:%S",tp)
    try: open(LogFile)
    except:
        open(LogFile,'w').write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="ru-RU" lang="ru-RU" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="content-type" />
    </head>
    <body>
    <table border="1" cellspacing=0 cellpadding=1><tr><th>time</th><th>who</th><th>text</th></tr>\n""")
    text=text.replace('\n','<br>')
    if to==1:
    	open(LogFile,'a').write((u"<tr><td>%s</td><td>To <font color=#000088>%s</font>:</td><td>%s</td></tr>\n"%(tm,nick,text)).encode('utf-8'))
    elif to==0:
    	open(LogFile,'a').write((u"<tr><td>%s</td><td>From <font color=#008800>%s</font>:</td><td>%s</td></tr>\n"%(tm,nick,text)).encode('utf-8'))
    else:
    	open(LogFile,'a').write((u"<tr><td>%s</td><td colspan=2 align='center'><font color=#880000>%s</font></td></tr>\n"%(tm,text)).encode('utf-8'))


COMMANDS[u'тест']=(testHandler,0,u'Просто проверка связи')
COMMANDS[u'отправь']=(SendHandler,1,u'Отправка сообщения другому пользователю. Синтаксис: джид_получателя сообщение')
COMMANDS[u'зайди']=(JoinHandler,1,u'Приглашение бота в конференцию. Синтаксис: зайди джид_конфы')
COMMANDS[u'выйди']=(LeaveHandler,1,u'Приглашение бота покинуть конференцию. Синтаксис: выйди джид_конфы')
COMMANDS[u'миркино']=(mirkino.kinoHandler,0,u'расписание кино в уфе с ценами. Синтаксис: миркино [кинотеатр]')
COMMANDS[u'кино']=(afisha.kinoAfisha,0,u'Расписание кино. Синтаксис: кино [в час:минута] город [кинотеатр/фильм]')
COMMANDS[u'чезакино']=(wiki2txt.CinemaHandler,0,u'Описание фильмов. Синтаксис; чезакино название_название фильма')
COMMANDS[u'вики']=(wiki2txt.WikiHandler,0,u'Поулчение статей из википедии. Синтаксис; вики название_статьи')
COMMANDS[u'закрыть']=(exitHandler,1,u'Закрыть бота')
COMMANDS[u'справка']=(helpHandler,0,u'Эта справка. Синтаксис: справка [имя команды]')
########################### user handlers stop ###################################
############################ bot logic start #####################################

def messageCB(conn,mess):
    text=mess.getBody()
    user=mess.getFrom()

    if (user in CONFERENCES) or (user in [i+u'/'+jid.getResource() for i in CONFERENCES]) or (user in IGNORE) or (user.getStripped() in IGNORE) or (type(text)!=type(u'')):
	    return
    else:
#	LOG(mess,user,text)
	logger.wrXMPPStanza(mess)
        if text.find(u' ')+1: command,args=text.split(u' ',1)
        else: command,args=text,''
        cmd=command.lower()
	now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
	if Echo:
		print now+user.__str__(),u"-->",text
	personal=1

	if mess.getType()=='groupchat':	
		if command==xmpp.JID(sys.argv[1]).getResource()+u':' or  command==xmpp.JID(sys.argv[1]).getResource()+u',' :
        		if text.find(' ')+1: command,args=text.split(' ',1)
		        else: command,args=text,''
		        cmd=command.lower()
		else: 
			personal=0
	reply=u''
	if re.match(u"icq(.+)",user.getDomain()) or re.match(u"jit(.+)",user.getDomain()):
		reply=u"Вам отвечает бот. Хочу напомнить вам, что более совершенным чем icq является протокол jabber, рекомендую вам переходить на него. В джаббере этот бот предоставляет некоторые интересные функции... Подробнее о джаббере можете прочитать, напрмер, тут: http://jabber.ufanet.ru Мой JID: %s Смерть быдлоаське! Автор бота - Tishka17 (jid: tishka17@jabber.ufanet.ru)"%(jid.getStripped())
        elif COMMANDS.has_key(cmd) and (not (COMMANDS[cmd][1]) or (user.getStripped() in ADMINS or user.__str__() in ADMINS)):
			reply=COMMANDS[cmd][0](user,command,args,mess)
	else: 
		reply=DoSimpleAnswer(user,command,args,mess)
		if reply==u'': 
			if personal:
				reply=talk(user,command,args,mess)
			else: reply=u''

	if len(reply): 
		if len(reply)>MaxReply and MaxReply:
			reply=reply[:MaxReply]+u'...'
		if mess.getType()=='groupchat':
			if len(reply)>MaxChatReply and MaxChatReply:
				now=time.strftime(u'%H:%M>',time.localtime(time.time()))
				mess1=xmpp.Message(mess.getFrom().getStripped(),user.getResource()+u": "+reply[:MaxChatReply]+u"<...>",typ='groupchat')
				mess2=xmpp.Message(mess.getFrom(),reply,typ='chat')
				logger.wrXMPPStanza(mess1)
				#LOG(mess1,mess.getFrom().getStripped(),user.getResource()+u":"+reply[:MaxChatReply]+u"<...>",1)
				logger.wrXMPPStanza(mess2)
				#LOG(mess2,mess.getFrom(),reply,1)
				if Echo:
					print now,mess.getFrom().getStripped(),u'<--',user.getResource()+u": "+reply[:MaxChatReply]+u"<...>"
					print now,mess.getFrom(),u'<--',reply
				conn.send(mess1)
				conn.send(mess2)
			else:
				now=time.strftime(u'%H:%M>',time.localtime(time.time()))
				mess1=xmpp.Message(mess.getFrom().getStripped(),user.getResource()+": "+reply,typ='groupchat')
				logger.wrXMPPStanza(mess1)
				#LOG(mess1,mess.getFrom().getStripped(),user.getResource()+u":"+reply,1)
				if Echo:
					print now,mess.getFrom().getStripped(),u'<--',user.getResource()+u": "+reply
				conn.send(mess1)
		else: 
			now=time.strftime(u'%H:%M>',time.localtime(time.time()))
			mess1=xmpp.Message(mess.getFrom(),reply,typ=mess.getType())
			logger.wrXMPPStanza(mess1)
			#LOG(mess1,mess.getFrom(),reply,1)
			if Echo:
				print now,mess.getFrom(),'<--',reply
			conn.send(mess1)

	if command==u'выход' and (user.getStripped() in ADMINS or user.__str__() in ADMINS):
        	sys.exit()

def PresenceHandler(cn,presence):
	if presence and presence.getType()=='subscribe':
		j=presence.getFrom().getStripped()
		roster=conn.getRoster()
		roster.Authorize(j)
		roster.Subscribe(j)
		if Echo:
			now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
			print now+u"JID: %s authorized"%j
		logger.wrTxt('%ROBOCAT%',u'JID: %s authorized'%j,'sys')
		#LOG(time.time(),u'',u"JID: %s authorized"%j,-1)
############################# bot logic stop #####################################

def StepOn(conn):
	try:
		conn.Process(1)
	except KeyboardInterrupt: return 0
	return 1

def GoOn(conn):
	while StepOn(conn): pass

### INIT
logger=logClass(LogFileName)
if Echo:
	now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
	print now+u"Bot started."
logger.wrTxt('%ROBOCAT%',u'Bot started.','sys')
#LOG(time.time(),u'',u"Bot started.",-1)

conres=conn.connect(proxy=PROXY)
if not conres:
	if Echo:
		now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
		print now+u"Unable to connect to server %s!"%server
	logger.wrTxt('%ROBOCAT%',u"Unable to connect to server %s!"%server,'sys')
	#LOG(time.time(),u'',u"Unable to connect to server %s!"%server,-1)
	sys.exit(1)
if conres<>'tls':
	if Echo:
		now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
		print now+u"Warning: unable to estabilish secure connection - TLS failed!"
	
	logger.wrTxt('%ROBOCAT%',u"Warning: unable to estabilish secure connection - TLS failed!",'sys')
	#LOG(time.time(),u'',u"Warning: unable to estabilish secure connection - TLS failed!",-1)

authres=conn.auth(user,password,resource)
if not authres:
	if Echo:
		now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
		print now+u"Unable to authorize on %s - check login/password."%server
	logger.wrTxt('%ROBOCAT%',u"Unable to authorize on %s - check login/password."%server,'sys')
	#LOG(time.time(),u'',u"Unable to authorize on %s - check login/password."%server,-1)
	sys.exit(1)
if authres<>'sasl':
	if Echo:
		now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
		print now+u"Warning: unable to perform SASL auth os %s. Old authentication method used!"%server
	logger.wrTxt('%ROBOCAT%',u"Warning: unable to perform SASL auth os %s. Old authentication method used!"%server,'sys')
	#LOG(time.time(),u'',u"Warning: unable to perform SASL auth os %s. Old authentication method used!"%server,-1)
conn.RegisterHandler('message',messageCB)
conn.RegisterHandler('presence',PresenceHandler)
conn.sendInitPresence()

if Echo:
	now=time.strftime(u'%H:%M> ',time.localtime(time.time()))
	print now+u"Logged in."
logger.wrTxt('%ROBOCAT%',"Logged in",'sys')
#LOG(time.time(),u'',u"Logged in.",-1)

for CONF in CONFERENCES:
	JoinConf(CONF)
GoOn(conn)
