#!/usr/bin/python
# -*- coding: utf8 -*-

# mirkino.py
# Simple library for getting info from http://kinoufa.ru
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
import time
import urllib

MirUrl={u'искра':u'http://www.kinoufa.ru/new/?i=2&mode=time&cid=1',u'мир':u'http://www.kinoufa.ru/new/?i=2&mode=time&cid=2',u'мир кино':u'http://www.kinoufa.ru/new/?i=2&mode=time&cid=2',u'победа':u'http://www.kinoufa.ru/new/?i=2&mode=time&cid=3',u'салават':u'http://www.kinoufa.ru/new/?i=2&mode=time&cid=15'}

def MirFilms():
	result=u''
	s=u''
	mir=urllib.urlopen('http://www.kinoufa.ru/new/?i=2&mode=time&cid=2')
	s=mir.read()
	if len(s):
		listt=re.split(u'"color:white">([^<]+)<img',s)
		list1=listt[1::2]
		list2=[]
		for c in listt[2::2]:
			list=re.split(u'lentaText">([^<]+)</a',c)
			films=u''
			if list[1::2]!=[]:
				for j in list[1::2]: 
					films=films+unicode(j,'cp1251')+', '
			list2=list2+[films]
		list3=zip(list1,list2)
		for j in list3:
			result=result+unicode(j[0],'cp1251')+u': '+j[1]+u'\n'
	return result[:-2]

def MirTimeTable(url):
	result=[]
	if url==u'': 
		return result
	s=u''
	list1=[]
	list2=[]
	list3=[]
	inside=0
	mir=urllib.urlopen(url)
	s=mir.read()
	if len(s):
		if s.find('class="sessionTable">'):
			inside=1
		if inside:
			list1=list1+re.split(u'sessionTime">([^<]+)</td',s)[1::2]
			list2=list2+re.split(u'text-decoration:none">([^<]+)</span',s)[1::2]
			list3=list3+re.split(u'sessionTime" align="center">([^<]+)</td',s)[1::2]
		if s.find('</table>'):
			inside=0
	result=zip(list1[0::2],list2,list3[0::3],list3[1::3],list3[2::3])
	return result

def TimeTable2Str(list):
	result=u''
	now=u''
	now=time.localtime(time.time())
	n=0
	for i in list:
		t=time.strptime(i[0],'%H:%M')
		if ((now[3]>0 and (t[3]>now[3] or (t[3]==now[3] and t[4]>now[4]))) or t[3]==0) and n<5:
			n=n+1
			result=result+unicode(i[0],'cp1251')+u' '+unicode(i[1],'cp1251')+u' - '+unicode(i[2],'cp1251')+u'р. ('+unicode(i[3],'cp1251')+u'р., '+unicode(i[4],'cp1251')+u'р.)\n'
	return result 

def kinoHandler(user,command,args,mess):
	if len(args): 
		if args.lower() in MirUrl:
			s=TimeTable2Str(MirTimeTable(MirUrl[args.lower()]))		
			if len(s):
				return u'В ближайшее время кинотеатре '+args+u' пройдут фильмы: \n'+s
			else:
				return u'На ближайшее время в кинотеатре '+args+u' фильмов не найдено'
		else: 
			return u'Кинотеатр не найден. Доступны следующие названия: '+u', '.join(MirUrl)
	return u'Сечас в кинотеатрах:\n'+MirFilms()
