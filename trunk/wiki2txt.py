#!/usr/bin/python
# -*- coding: utf8 -*-

# wiki2txt
# Simple library for getting info from some wikies and to traslate it into plain text
# Copyright (C) 2008 Tikhonov Andrey aka Tishka17 
#
# This library is free software; you can redistribute it and/or
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

import re
import urllib


def GetTemplate(name):
	return 'Template'

def MakeTemplate(name,params):
	if name!=u'Галерея' and name!=u'' and name!=None:
		return Wiki2Text(u'\n'.join(params))
	else:
		return u''


def Wiki2Text(wiki):
	def x(s):
		return s.group('adr')
	cat=re.compile(u'(\[\[Category:.*?\]\])|(\[\[Категория:.*?\]\])')
	lnk=re.compile(u'\[\[(?P<adr>.*?)\]\]')

	s=re.sub(u'<!--.*?-->',u'',wiki)
	ls=re.split(u'\{\{(.*?)\|(.*?)\}\}',s)
	lst=zip(ls[1::3],ls[2::3],ls[0::3])
	s1=u''
	for i in lst:
		s2=cat.sub(u'',i[2])
		s4=lnk.sub(x,s2)
		s3=MakeTemplate(i[0],re.split(u'([^|]*)',i[1])[1::2])
		s1=s1+s4+s3
	s2=cat.sub(u'',ls[-1])
	s4=lnk.sub(x,s2)
	s1=s1+s4
	s3=re.sub(u'\n{2,}','\n\n',s1)

	text=s3
	return text
def GetWiki(url):
	f=urllib.urlopen(url)
	s=unicode(f.read(),'utf-8')
	l=re.split(u'(?s)<textarea.*?>(.*?)</textarea>',s)

	if len(l)>1:
		s1=l[1]
		s1=re.sub(u'&lt;',u'<',s1)
		s1=re.sub(u'&gt;',u'>',s1)
		return s1
	else:
		return u''

def CorrectWord(word):
	s=word.title()
	return urllib.quote(s.encode('utf-8'))

def RuWiki(word):
	return 'http://ru.wikipedia.org/w/index.php?title=%s&action=edit'%word

def Cinema(word):
	return 'http://kino.skripov.com/index.php?title=%s&action=edit'%word


def CinemaHandler(user,command,args,mess):
	if len(args):
		n=CorrectWord(args)
		url=Cinema(n)
		s=GetWiki(url)
		txt=Wiki2Text(s)
		if len(txt):
			return txt
		else:
			return u'Фильм не найден. Попробуйте поискать другой.'
	else:
		return u'Укажите, пожалуйста, название фильма.'

def WikiHandler(user,command,args,mess):
	if len(args):
		n=CorrectWord(args)
		url=RuWiki(n)
		s=GetWiki(url)
		txt=Wiki2Text(s)
		if len(txt):
			return txt
		else:
			return u'Статья не найдена. Попробуйте поискать другую.'
	else:
		return u'Укажите, пожалуйста, название статьи.'
