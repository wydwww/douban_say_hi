#!/usr/bin/env python
# -*-coding:utf-8-*-

__author__ = 'wydwww'

import urllib2  # functions and classes which help in opening URLs
import urllib
import bs4  # extract data from HTML or XML files
import re
import time
import string
import cookielib
import logging

email = raw_input('Email:')
password = raw_input('Password:')
cookies_file = 'Cookies_saved.txt'


class douban_robot:
    def __init__(self):
        self.email = email
        self.password = password
        self.data = {
            "form_email": email,
            "form_password": password,
            "source": "index_nav",
            "remember": "on"
        }

        self.login_url = 'https://www.douban.com/accounts/login'
        self.load_cookies()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.addheaders = [("User-agent", "Mozilla/5.0 (X11; Linux x86_64)\
          AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36")]
        # self.opener.addheaders = [("Origin", "https://www.douban.com")]
        self.get_ck()

    def load_cookies(self):
        try:
            self.cookie = cookielib.MozillaCookieJar()
            self.cookie.load(cookies_file)
            print "loading cookies for file..."
        except Exception, e:

            print "The cookies file is not exist."
            self.login_douban()
            # reload the cookies.
            self.load_cookies()

    def get_ck(self):
        # open a url to get the value of ck.
        self.opener.open('https://www.douban.com')
        # read ck from cookies.
        for c in list(self.cookie):

            if c.name == 'ck':
                self.ck = c.value.strip('"')
                print "ck:%s" % self.ck
                break
        else:
            print 'ck is end of date.'
            self.login_douban()
            # #reload the cookies.
            self.cookie.revert(cookies_file)
            self.get_ck()

    def login_douban(self):
        '''
        login douban and save the cookies into file.

        '''
        cookieJar = cookielib.MozillaCookieJar(cookies_file)
        # will create (and save to) new cookie file

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
        # !!! following urllib2 will auto handle cookies
        response = opener.open(self.login_url, urllib.urlencode(self.data))
        html = response.read()
        regex = r'<img id="captcha_image" src="(.+?)" alt="captcha"'
        imgurl = re.compile(regex).findall(html)
        if imgurl:
            # urllib.urlretrieve(imgurl[0], 'captcha.jpg')
            print "The captcha_image url address is %s" % imgurl[0]

            # download the captcha_image file.
            # data = opener.open(imgurl[0]).read()
            # f = file("captcha.jpg","wb")
            # f.write(data)
            # f.close()

            captcha = re.search(
                '<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
            if captcha:
                vcode = raw_input('CAPTCHA')
                self.data["captcha-solution"] = vcode
                self.data["captcha-id"] = captcha.group(1)
                self.data["user_login"] = "login"
                response = opener.open(
                    self.login_url, urllib.urlencode(self.data))
                # fp = open("2.html","wb")
                # fp.write(response.read())
                # fp.close

        cookieJar.save()
        if response.geturl() == "http://www.douban.com/":
            print 'login success !'
            # update cookies, save cookies into file
            # cookieJar.save();
        else:
            return False
        return True

    def send_mail(self, id, content = 'Hi！This message is sent from [https://github.com/wydwww/douban_say_hi]. Enjoy!'):

        post_data = urllib.urlencode({
            "ck": self.ck,
            "m_submit": "Hi！This message is sent from [https://github.com/wydwww/douban_say_hi]. Enjoy!",
            "m_text": content,
            "to": id,
        })
        request = urllib2.Request("https://www.douban.com/doumail/write")
        # request.add_header("Origin", "https://www.douban.com")
        request.add_header("Referer", "https://www.douban.com/doumail/write")
        self.opener.open(request, post_data)


wydwww = douban_robot()

req = urllib2.Request('http://www.douban.com/contacts/rlist')
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(wydwww.cookie))
content = opener.open(req)

old = []
soup = bs4.BeautifulSoup(content, 'lxml')
div = soup.find('ul', 'user-list')
followers_list1 = re.findall('u\d{8}', str(div))
followers_list2 = list(set(followers_list1))
for a in followers_list2:
    a = a.strip('u')
    old.append(a)

# Logging config
fmt = '%(asctime)s [%(levelname)s] %(message)s'
datefmt = '%Y-%m-%d,%H:%M:%S'

logging.basicConfig(
    level=logging.INFO,
    format=fmt,
    datefmt=datefmt,
    filename='douban.log',
    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(fmt, datefmt)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.getLogger('requests').setLevel(logging.CRITICAL)

while 1:
    req = urllib2.Request('http://www.douban.com/contacts/rlist')
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(wydwww.cookie))
    content = opener.open(req)

    followers_list = []
    soup = bs4.BeautifulSoup(content, "lxml")
    div = soup.find('ul', 'user-list')
    followers_list1 = re.findall('u\d{8}', str(div))
    followers_list2 = list(set(followers_list1))
    for a in followers_list2:
        a = a.strip('u')
        followers_list.append(a)
    # print followers_list
    # logging.info('Followers in page 1: %s' % followers_list)

    aa = set(old)
    bb = set(followers_list)
    difference = list(bb.difference(aa))
    # print difference
    for dif in difference:
        wydwww.send_mail(dif)
        logging.info('Send Msg To %s' % dif)

    old = followers_list

    time.sleep(10)
