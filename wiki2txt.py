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
import urllib2


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
	cat=re.compile(u'(\[\[Category:.*?\]\])|(\[\[Категория:.*?\]\])|(\[\[Image:.*?\]\])|(\[\[Изображение:.*?\]\])')
	lnk=re.compile(u'\[\[(?P<adr>.*?)\]\]')
	lnk2=re.compile(u'\[\[(?:[^]]*)\|(?P<adr>.*?)\]\]')

	s=re.sub(u'<!--.*?-->',u'',wiki)
	ls=re.split(u'\{\{(.*?)\|(.*?)\}\}',s)
	lst=zip(ls[1::3],ls[2::3],ls[0::3])
	s1=u''
	for i in lst:
		s2=cat.sub(u'',i[2])
		s3=lnk2.sub(x,s2)
		s4=lnk.sub(x,s3)
		s3=MakeTemplate(i[0],re.split(u'([^|]*)',i[1])[1::2])
		s1=s1+s4+s3
	s2=cat.sub(u'',ls[-1])
	s4=lnk.sub(x,s2)
	s1=s1+s4
	s3=re.sub(u'\n{2,}','\n\n',s1)
	return s3

def GetWiki(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Opera/10.00 (X11; Linux x86_64 ; U; ru) Presto/2.2.0')
	request.add_header('Accept-Charset', 'utf-8')
	opener = urllib2.build_opener()                                   
	data = opener.open(request).read()                      
	s=unicode(data,'utf-8')
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

def Lurkmore(word):
	return 'http://lurkmore.ru/index.php?title=%s&action=edit'%word


def LurkmoreHandler(user,command,args,mess):
	if len(args):
		n=CorrectWord(args)
		url=Lurkmore(n)
		s=GetWiki(url)
		txt=Wiki2Text(s)
		if len(txt):
			return txt
		else:
			return u'Статья не найдена. Попробуйте поискать другой.'
	else:
		return u'Укажите, пожалуйста, название фильма.'
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
		if not len(s):
			return u'Статья не найдена. Попробуйте поискать другую'
		txt=Wiki2Text(s)
		if len(txt):
			return txt
		else:
			return u'Статья пустая. Попробуйте почитать другую.'
	else:
		return u'Укажите, пожалуйста, название статьи.'
