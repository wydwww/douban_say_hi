#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-10-09 17:11:42
# @Author  : Linsir (vi5i0n@hotmail.com)
# @Link    : http://Linsir.sinaapp.com

import urllib
import urllib2
import cookielib
import re
import random

email = 'xxx@xxx.com'
password = 'xxx'

class douban_robot:

    def __init__(self):
        self.ck = None
        self.data = {
                "form_email": email,
                "form_password": password,
                "source": "index_nav",
                "remember": "on"
        }
        self.cookieFile = "cookies_saved.txt";
        self.cookie = cookielib.LWPCookieJar(self.cookieFile);
        #will create (and save to) new cookie file
        self.login_url = 'http://www.douban.com/accounts/login'
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.addheaders = [("User-agent","Mozilla/5.0 (Windows NT 6.1) \
            AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11)")]
        # self.opener.addheaders = [("Origin", "http://www.douban.com")]
        self.load_cookies()
        self.get_ck()

    def load_cookies(self):
        try:
            self.cookie.load(self.cookieFile)
            print "loading cookies.."
        except:

                print "The cookies file is not exist."
                self.login_douban()
                self.load_cookies()

    def get_ck(self):
        #open a url to get the value of ck.
        self.opener.open('http://www.douban.com')
        for c in list(self.cookie):
            if c.name == 'ck':
                self.ck = c.value.strip('"')
                print "ck:%s" %self.ck
                break

        if self.ck:
            print 'The ck is update.'

        else:
            print 'ck is out of date.'
            self.login_douban()
            self.load_cookies()
            self.get_ck()



    def login_douban(self):
        '''
        login douban and save the cookies into file.

        '''
        response = self.opener.open(self.login_url, urllib.urlencode(self.data))
        html = response.read()

        # fp = open("1.html","wb")
        # fp.write(html)
        # fp.close

        imgurl = re.compile(r'<img id="captcha_image" src="(.+?)" alt="captcha"').findall(html)
        if imgurl:
            #download the captcha_image file.
            print "The captcha_image link is %s" %imgurl[0]
            data = self.opener.open(imgurl[0]).read()
            # f = file("captcha.jpg","wb")
            # f.write(data)
            # f.close()

            captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>', html)
            if captcha:
                vcode=raw_input('打开上面链接的图片的验证码是：')
                self.data["captcha-solution"] = vcode
                self.data["captcha-id"] = captcha.group(1)
                self.data["user_login"] = "登录"
                #验证码验证
                response = self.opener.open(self.login_url, urllib.urlencode(self.data))

        #登录成功
        if response.geturl() == "http://www.douban.com/":
            print 'login success !'
            self.cookie.save();
        else:
            return False
        return True


    def new_topic(self, group_id, title, content):

        group_url = "http://www.douban.com/group/" + group_id
        post_url = group_url + "/new_topic"
        post_data = urllib.urlencode({
            'ck':self.ck,
            'rev_title': title ,
            'rev_text': content,
            'rev_submit':'好了，发言',
            })
        request = urllib2.Request(post_url)

        # request.add_header("Origin", "http://www.douban.com")
        request.add_header("Referer", post_url)
        response = self.opener.open(request, post_data)
        if response.geturl() == group_url:
            print 'Okay, Success !'
            return True
        return False


    def talk_statuses(self, content = '(⊙o⊙)…'):

        post_data = urllib.urlencode({
            'ck' : self.ck,
            'comment' : content,
            })

        request = urllib2.Request("http://www.douban.com/")
        # request.add_header("Origin", "http://www.douban.com")
        request.add_header("Referer", "http://www.douban.com/")
        self.opener.open(request, post_data)


    def send_mail(self, id ,content = 'test'):

        post_data = urllib.urlencode({
           "ck" : self.ck,
           "m_submit" : "test",
           "m_text" : content,
           "to" : id,
           })
        request = urllib2.Request("http://www.douban.com/doumail/write")
        # request.add_header("Origin", "http://www.douban.com")
        request.add_header("Referer", "http://www.douban.com/doumail/write")
        self.opener.open(request, post_data)


    def sofa(self,
        group_id,
        content=['丫鬟命，公主心，怪不得人。',
                '要交流就平等交流，弄得一副跪舔样,谁还能瞧得起你？',
                '己所欲，勿施于人..',
                '人在做，天在看.',]
        ):

        group_url = "http://www.douban.com/group/" + group_id +"/#topics"
        html = self.opener.open(group_url).read()
        topics = re.findall(r'topic/(\d+?)/.*?class="">.*?<td nowrap="nowrap" class="">(.*?)</td>',
                    html, re.DOTALL)

        for item in topics:
            if item[1] == '':
                post_data = urllib.urlencode({
                        "ck" : self.ck,
                        "rv_comment" : random.choice(content),
                        "start" : "0",
                        "submit_btn" : "加上去"
                })
                self.opener.open("http://www.douban.com/group/topic/" + item[0] + "/add_comment#last?", post_data)


    def get_joke(self):
        html = urllib2.urlopen('http://www.xiaohuayoumo.com/').read()
        result = re.compile(r']<a href="(.+?)">(.+?)</a></div>.+?', re.DOTALL).findall(html)
        for x in result[:1]:
            title = x[1]
            # print title
            joke_url = 'http://www.xiaohuayoumo.com' + x[0]
            page = self.opener.open(joke_url).read()
            result = re.compile(r'content:encoded">(.+?)<a href.+?</a>(.+?)</div></div></div></div>',
                        re.DOTALL).findall(page)
            for x in result[:1]:
                content = x[0] + x[1]
                content = re.sub(r'</?\w+[^>]*>',' ',content)
                # print content
        return title, content



# if __name__ == '__main__':
    # app = douban_robot()
    # titile, content = app.get_joke()
    # content = '又到了笑话时间了~\(≧▽≦)/~\n' + content
    # if titile and content:
    #     print app.new_topic("cd", titile, content)

    # app.talk_statuses('Hello.it\'s a test message using python.')
    # app.send_mail(97869782)
    # app.sofa("CentOS")
