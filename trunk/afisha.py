#!/usr/bin/python
# -*- coding: utf8 -*-
# afisha.py
# module for getting cinema schedule from http://www.afisha.ru
# Copyright (C) 2008 Tikhonov Andrey aka Tishka17 
#
# This module is free software; you can redistribute it and/or
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
import time

Cities={u'москва':'msk',u'мск':'msk',u'питер':'spb',u'петербург':'spb',u'спб':'spb',u'волгоград':'volgograd',u'воронеж':'voronezh',u'ебург':'ekaterinburg',u'екатеринбург':'ekaterinburg',u'иркутск':'irkutsk',u'казань':'kazan',u'калининград':'kaliningrad',u'краснодар':'krasnodar',u'липецк':'lipetsk',u'мурманск':'murmansk',u'нижний_новгород':'nnovgorod',u'нновгород':'nnovgorod',u'нн':'nnovgorod',u'новосибирск':'novosibirsk',u'пермь':'perm',u'петрозаводск':'petrozavidsk',u'ростов-на-дону':'rostov-na-donu',u'самара':'samara',u'сочи':'sochi',u'ставрополь':'stavropol',u'тула':'tula',u'уфа':'ufa',u'челябинск':'chelyabinsk',u'ярославль':'yaroslavl'}

Cinema={}
DeltaTime={'msk':-2,'spb':-2,'volgograd':-2,'voronezh':-2,'ekaterinburg':0,'irkutsk':+3,'kazan':-2,'kaliningrad':-3,'krasnodar':-2,'lipetsk':-2,'murmansk':-2,'nnovgorod':-2,'novosibirsk':+1,'perm':0,'petrozavodsk':-1,'rostov-na-donu':-2,'samara':-1,'sochi':-2,'stavropol':-2,'tula':-2,'ufa':0,'chelyabinsk':0,'yaroslavl':-1}

def CompareTimes(x,y):
	if (x[3]>y[3] and (y[3]>3 or (y[3]<=3 and x[3]<=3))) or (x[3]==y[3] and x[4]>y[4]) or (x[3]<=3 and y[3]>3):
		return 1
	if (y[3]>x[3] and (x[3]>3 or (x[3]<=3 and y[3]<=3))) or (y[3]==x[3] and y[4]>x[4]) or (y[3]<=3 and x[3]>3):
		return -1
	return -1

def CompareSchedules(a,b):
	if type(a)==type(()):
		x=time.strptime(a[2],'%H:%M')
	elif type(a)==type(u''):
		x=time.strptime(a,'%H:%M')
	else:
		x=a
	if type(b)==type(()):
		y=time.strptime(b[2],'%H:%M')
	elif type(b)==type(u''):
		y=time.strptime(b,'%H:%M')
	else:
		y=b
	return CompareTimes(x,y)	

def AfishaCities():
	c1=[]
	c2=[]
	keys=Cities.keys()
	keys.sort()
	for i in keys:
		if Cities[i] not in c2:
			c1.append(i)
			c2.append(Cities[i])
	c1.sort()
	return c1

def AfishaFullSchedule(city):
	now=u''
	now=time.localtime(time.time())
	if Cinema.has_key(city): 
		x=time.localtime(Cinema[city]['lastupdated'])
		x1=time.localtime(Cinema[city]['lastupdated']+24*3600)
		if (now[2]==x[2] and now[1]==x[1] and now[0]==x[0] and (x[3]>3 and now[3]>3 or x[3]<=3 and now[3]<=3)) or (now[2]==x1[2] and now[1]==x1[1] and now[0]==x1[0] and now[3]<=3 and x1[3]>3): 
			return Cinema[city]['schedule']
	else:
		Cinema[city]={}
	schedule=[]
	getcinema=re.compile(u'class="b-td-item">(?:[^>]+)>([^<]+)</a')
	gettime=re.compile(u'<span (?:[^>]+)>(?:\s*)([^\r]+)(?:\s*)<')
	gettime2=re.compile(u'<a (?:[^>]+)>(?:\s*)([^\r]+)(?:\s*)<')
	site=urllib.urlopen('http://www.afisha.ru/%s/schedule_cinema/'%city)
	content=unicode(site.read(),'cp1251')
	#text=re.search(u'"schedule-table movie">(.+?)<!--',content,re.DOTALL).group()
	text=content
	list1=re.split(u'<h3 class="usetags">([^>]+)>(?:\s*)([^\r]+)(?:\s*)<',text,re.DOTALL)
	timetable=re.compile(u'table>')
	films=zip(list1[2::3],list1[3::3])
	for film in films:
		list2=getcinema.split(timetable.split(film[1])[1],re.DOTALL)
		cinemas=zip(list2[1::2],list2[2::2])
		for cinema in cinemas:
			list3=gettime.split(cinema[1],re.DOTALL)
			for time1 in list3[1::2]:
				if gettime2.match(time1):
					if gettime2.split(time1)[1].find(":")>-1:
						schedule.append((film[0],cinema[0],gettime2.split(time1)[1]))
				else:
					if time1.find(":")>-1:
						schedule.append((film[0],cinema[0],time1))
	schedule.sort(CompareSchedules)
	Cinema[city]['lastupdated']=time.time()
	Cinema[city]['schedule']=schedule
	return schedule

def AfishaCinemas(city):
	sch=AfishaFullSchedule(city)
	c=[]
	for i in sch:
		if i[1] not in c:
			c.append(i[1])
	c.sort()
	return c

def AfishaFilms(city):
	sch=AfishaFullSchedule(city)
	c=[]
	for i in sch:
		if i[0] not in c:
			c.append(i[0])
	c.sort()
	return c

def AfishaSchedule(city,time,cinema,film):
	sch=AfishaFullSchedule(city)
	ls=[]
	n=0
	for i in sch:
		if (cinema==u'' or cinema.lower()==i[1].lower()) and (film==u'' or film.lower()==i[0].lower()) and (CompareSchedules(i[2],time)>0 or time==u'') and n<5:
			ls.append(i)
			n=n+1
	return ls

def kinoAfisha(user,command,args,mss):
	ls=re.split(u'(?:\s*)(\S+)(?:\s*)(.*)(?:\s*)',args)
	if len(ls)>1:
		if ls[1]==u'в':
			ls1=re.split(u'(?:\s*)в(?:\s*)(\S+)(?:\s*)(\S+)(?:\s*)(.*)(?:\s*)',args)
			if len(ls1):
				if Cities.has_key(ls1[2]):
					city=Cities[ls1[2]]
					city1=ls1[2]
				else:
					city=u''
				if ls1[1].find(u':')>=0:
					now=time.strptime(ls1[1],'%H:%M')
				elif ls1[1].find(u'.')>=0:
					now=time.strptime(ls1[1],'%H.%M')
				elif ls1[1].find(u',')>=0:
					now=time.strptime(ls1[1],'%H,%M')
				else:
					now=time.localtime(time.time()+DeltaTime[city]*3600)
				cinema=ls1[3]
		else:
			if Cities.has_key(ls[1]):
				city=Cities[ls[1]]
				city1=ls[1]
				now=time.localtime(time.time()+DeltaTime[city]*3600)
				cinema=ls[2]
			else:
				city=u''
	else:
		city=u''
	
	if city==u'':
		return u'Укажите, пожалуйста, один из следующих городов: '+u', '.join(AfishaCities()) 
	if (cinema==u''):
		schedule=AfishaSchedule(city,now,u'',u'')
		if len(schedule):
			return u'После '+time.strftime(u'%H:%M',now)+u' в городе '+city1+u' пройдут фильмы: \n'+u',\n'.join([i[2]+u' : '+i[0]+u' - '+i[1]  for i in schedule])
		else:
			return u'После '+time.strftime(u'%H:%M',now)+u' в городе '+city1+u' фильмов не найдено'
	elif cinema.lower() in [i.lower() for i in AfishaCinemas(city)]:
		schedule=AfishaSchedule(city,now,cinema,u'')
		if len(schedule):
			return u'После '+time.strftime(u'%H:%M',now)+u' в кинотеатре '+cinema+u' пройдут фильмы: \n'+u',\n'.join([i[2]+u' : '+i[0] for i in schedule])
		else:
			return u'После '+time.strftime(u'%H:%M',now)+u' в кинотеатре '+cinema+u' фильмов не найдено'
	elif cinema.lower() in [i.lower() for i in AfishaFilms(city)]:
		schedule=AfishaSchedule(city,now,u'',cinema)
		if len(schedule):
			return u'После '+time.strftime(u'%H:%M',now)+u' фильм '+cinema+u' пройдет в следующих кинотеатрах: \n'+u',\n'.join([i[2]+u' : '+i[1] for i in schedule])
		else:
			return u'После '+time.strftime(u'%H:%M',now)+u' фильм '+cinema+u' не найден'
	else:
		return u'Укажите кинотеатр, расписание которго Вы хотите посмотреть ( '+u', '.join(AfishaCinemas(city))+u')\nИли один из фильмов: '+u', '.join(AfishaFilms(city))

