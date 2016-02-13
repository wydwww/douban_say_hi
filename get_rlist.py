#!/usr/bin/env python
#-*-coding:utf-8-*-
__author__ = 'wydwww'

import urllib2  # functions and classes which help in opening URLs
import bs4      # extract data from HTML or XML files
import re
import time
import string
import cookielib
from douban import douban_robot

wydwww = douban_robot()

req = urllib2.Request('http://www.douban.com/contacts/rlist')
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(wydwww.cookie))
content = opener.open(req)

old = []
soup = bs4.BeautifulSoup(content,'lxml')
div = soup.find('ul','user-list')
followers_list1 = re.findall('u\d{8}',str(div))
followers_list2 = list(set(followers_list1))
for a in followers_list2:
    a = a.strip('u')
    old.append(a)

while 1:
    req = urllib2.Request('http://www.douban.com/contacts/rlist')
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(wydwww.cookie))
    content = opener.open(req)

    followers_list=[]
    soup = bs4.BeautifulSoup(content,"lxml")
    div = soup.find('ul','user-list')
    followers_list1 = re.findall('u\d{8}',str(div))
    followers_list2 = list(set(followers_list1))
    for a in followers_list2:
        a = a.strip('u')
        followers_list.append(a)
    print followers_list

    aa = set(old)
    bb = set(followers_list)
    print list(bb.difference(aa))
    for dif in list(bb.difference(aa)):
        wydwww.send_mail(dif)
    old = followers_list

    time.sleep(5)
