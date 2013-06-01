#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import os, re
import time
import random
import urllib2
import json
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huodongrili.settings")

from app.models import *

class DoubanBot(object):
    def __init__(self):
        self.cities = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'chengdu', 'hangzhou']
        self.types = ['film', 'salon', 'exhibition']
        self.urls = set()
        self.interval = 7 # in seconds
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible; EventsCalendarbot/1.0; +http://huodongrili.com/bot)')]
        self.encoding = 'utf-8'
        self.blacklist = list(Blacklist.objects.all())
        

    def run(self):
        for city in self.cities:
            for t in self.types:
                state = (city, t, 0)
                while state:
                    state = self.scrap(*state)
                    time.sleep(self.interval)

    def scrap(self, city, t, init):
        print '-'*100
        url = 'https://api.douban.com/v2/event/list?loc=%s&type=%s&start=%d' % (city, t, init)
        print 'url = ', url
        page = self.opener.open(url).read().decode(self.encoding)
        data = json.loads(page)

        count = data['count']
        start = data['start']
        total = data['total']
        events = data['events']

        for event in events:
            self.save(event)

        if total > start+count:
            return (city, t, start+count)

    def in_balcklist(self, title):
        for black in self.blacklist:
            words = black.word.split()
            appear = True
            for word in words:
                if not word in title:
                    appear = False
                    break
            if appear:
                return True
        return False

    def save(self, event):
        try:
            m = re.match(ur'(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):\d+', event['begin_time'])
            if m:
                start_date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                start_time = datetime.time(int(m.group(4)), int(m.group(5)))
                print 'start_date', start_date

            m = re.match(ur'(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):\d+', event['end_time'])
            if m:
                end_date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                end_time = datetime.time(int(m.group(4)), int(m.group(5)))

            city = City.objects.get(name=event['loc_name'])
            
            try:
                activity = Activity.objects.get(url=event['alt'], start_date=start_date)
                print 'This event is already stored.'
                return
            except:
                activity = Activity()
            
            print 'title = ', event['title']
            if self.in_balcklist(event['title']):
                print 'This event is in blacklist'
                return

            activity.title = event['title']
            activity.content = event['content']
            activity.start_date = start_date
            activity.start_time = start_time
            activity.end_date = end_date
            activity.end_time = end_time
            activity.location = event['address']
            activity.url = event['alt']
            activity.city = city
            activity.weight = 70 + random.randint(0,10)
            activity.public = 0
            activity.source = u'豆瓣'
            activity.save()

            print 'Done.'
        except Exception, e:
            print e

if __name__ == '__main__':
    douban_bot = DoubanBot()
    douban_bot.run()
