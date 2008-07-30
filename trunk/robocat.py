
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

class RoboCat:
	Settings={u'show':u'available',u'status':u'Робокот в сети. Юзайте справку'}
	Conferences={}

	def getState(self):
		'Returns show and status strings'
		return self.Settings[u'show'],self.Settings[u'status']

	def setState(self, show, status):
		'Sets show and status strings. Changes xmpp presense'
		if show:
			show = show.lower()
		if show == "online" or show == "on" or show == "available":
			show = "available"
		elif show == "busy" or show == "dnd":
			show = "dnd"
		elif show == "away" or show == "idle" or show == "off" or show == "out" or show == "xa":
			show = "xa"
		else:
			show = "available"
		self.Settings[u'show'] = show

		if status:
			self.Settings[u'status'] = status
		if self.conn:
			pres=xmpp.Presence(priority=5, show=self.Settings[u'show'], status=self.Settings[u'status'])
			self.conn.send(pres)
		
	def joinConf(conf,secret=u''):
		if not conf:
			return u'No conference jid'
		if secret:
			self.Conferences[conf]
		elif self.Conferences and conf in self.Conferences:
			secret=self.Conferences[conf]
		else:
			secret=''
			CONFERENCES[CONF]=''
		p=xmpp.protocol.Presence(to='%s/%s'%(CONF,jid.getResource()))
		p.setTag('x',namespace=xmpp.protocol.NS_MUC).setTagData('password',secret)
		p.getTag('x').addChild('history',{'maxchars':'0','maxstanzas':'0'})
		if self.conn:
			conn.send(p)

			if self.Settings[u'Greetings']:
				rnd=random.randrange(1,5)
				if rnd==1:	self.conn.send(xmpp.Message(xmpp.JID(conf),u'Всем приветик!',typ='groupchat'))
				elif rnd==2:	self.conn.send(xmpp.Message(xmpp.JID(conf),u'Хеллоу всем!',typ='groupchat'))
				elif rnd==3:	self.conn.send(xmpp.Message(xmpp.JID(conf),u'Всем мяу!',typ='groupchat'))
				elif rnd==4:	self.conn.send(xmpp.Message(xmpp.JID(conf),u'Здравствуйте все!',typ='groupchat'))

	def leaveConf(conf):
		if self.conn:
			p=xmpp.protocol.Presence(to='%s'%(conf),typ='unavailable')
			conn.send(p)


	def senMessage(self,to,message,type):
		if not message or not type or not to: return 'Not enough parameters'
		if not self.conn: return 'Not connected'

		if len(message)>int(self.Settings[u'MaxMessage']):
			message=message[:int(self.Settings[u'MaxMessage'])]+' ...'
		if type='groupchat':
			if type(to)==type('') or type(to)==type(u''):
				jid=JID(to)
			else: jid=to
			conf=jid.getStripped()
			res=jid.getResource()
			if len(message)>int(self.Settings[u'MaxGroupChat']):
				mess1=xmpp.Message(conf,res+u": "+message[:int(self.Settings[u'MaxMessage'])]+u"<...>",typ='groupchat')
				self.conn.send(mess1)
				mess2=xmpp.Message(to,message,typ='chat')
				self.conn.send(mess2)
			else:
				mess1=xmpp.Message(conf,res+u": "+reply[],typ='groupchat')
				self.conn.send(mess1)

		elif type='chat' or type='message':
			mess1=xmpp.Message(to,message,typ)	
			self.conn.send(mess1)
