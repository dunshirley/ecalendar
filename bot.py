#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import os, re
import time
import random
import urllib2
import json
from lxml import etree
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huodongrili.settings")

from app.models import *

class Bot(object):
    def __init__(self):
        self.urls = set()
        self.interval = 60 # in seconds
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible; EventsCalendarbot/1.0; +http://huodongrili.com/bot)')]
        self.encoding = 'utf-8'

    def add(self, url):
        self.urls.add(url)

    def run(self):
        for url in self.urls:
            self.scrap(url)
            time.sleep(self.interval)

    def get_tree(self, url):
        try:
            print '-'*100 + '\n' + url.url
            #url.status = 'i'
            page = self.opener.open(url.url).read().decode(self.encoding)
            return etree.HTML(page)
        except Exception, e:
            print e

    def scrap(self, url):
        pass

    def get_date(self, month, day):
        month = int(month)
        day = int(day)
        today = datetime.date.today()
        year = today.year

        ans = datetime.date(year, month, day)
        tmp = datetime.date(year+1, month, day)
        if abs(tmp-today) < abs(ans-today):
            ans = tmp
        return ans

    def get_time(self, hour, minute):
        hour = int(hour)
        minute = int(minute)
        ans = datetime.time(hour, minute)
        return ans

class HeadinBot(Bot):
    def __init__(self):
        self.xpaths = {
                'title': u'//h2/@title',
                'start_datetime': u'//div[@class="countdown"]/@*',
                'localtion': u'//p[@id="pAddress"]/text()',
                'content': u'//div[@class="event-description"]/p//text()|//div[@class="event-description"]/h1//text()',
            }
        super(HeadinBot, self).__init__()

    def find_city(self, *city_list):
        city = None
        for one_city in city_list:
            try:
                city = City.objects.get(name=one_city)
                break
            except:
                continue
        return city

    def scrap(self, url):
        crawl_start_time = datetime.datetime.now()
        tree = self.get_tree(url)
        if tree is None:
            return

        title = tree.xpath(self.xpaths['title'])[0].strip()
        try:
            start_datetime = tree.xpath(self.xpaths['start_datetime'])[1].strip()
        except:
            start_datetime = "end"
        print start_datetime
        print 'get title = ', title
        time_list = re.split('/|:|\s+',start_datetime)
        if len(time_list) == 6:
            start_date = self.get_date(*time_list[1:3])
            start_time = self.get_time(*time_list[3:5])
            end_date = self.get_date(12, 31)
            end_time = self.get_time(23, 59)
        else:return
        print "start_date=%s; start_time =%s;\nend_date=%s;end_time=%s" %(start_date, start_time, end_date, end_time)
        tmp_location = tree.xpath(self.xpaths['localtion'])[0].strip().split()
        location = tmp_location[-1]
        city = self.find_city(tmp_location[1], tmp_location[-1][:2])
        if not city:return
        print "localtion=%s;city=%s" % (location,city.name)
        content_list = tree.xpath(self.xpaths['content'])
        content =  "".join(content_list)
        content = re.sub('\n+', '\n', content).strip().replace('\t','')
        print "content = ", content

        source = u'海丁'
        weight = 75 + random.randint(0,10)
        public = 0
        try:
            activity = Activity.objects.get(url=url.url, start_date=start_date)
        except:
            activity = Activity()

        activity.title = title
        activity.content = content
        activity.start_date = start_date
        activity.start_time = start_time
        activity.location = location
        activity.url = url.url
        activity.city = city
        activity.weight = weight
        activity.public = public
        activity.source = source
        activity.save()

        url.status = 'd'
        url.crawl_start_time = crawl_start_time
        url.crawl_end_time = datetime.datetime.now()
        url.save()

        print 'Done.'

class WeiboBot(Bot):
    def __init__(self):
         self.xpaths = {
                 'title': u'//div[@id="pl_event_copy"]/strong/text()|//h3[@class="ev_title"]/text()',
                 'duration': u'//div[contains(@class,"ev_detail_cont")]/p[1]/span[2]/text()',
                 'start_datetime': u'//span[contains(text(),"开始时间")]/../span[2]/text()',
                 'end_datetime': u'//span[contains(text(),"结束时间")]/../span[2]/text()',
                 'location': u'//span[contains(text(),"地　　点")]/../span[2]/text()',
                 'content': u'//div[@class="ev_details"]/descendant-or-self::*/text()',
                 }
         super(WeiboBot, self).__init__()

    def scrap(self, url):
        crawl_start_time = datetime.datetime.now()
        tree = self.get_tree(url)
        if tree is None:
            return

        title = tree.xpath(self.xpaths['title'])[0].strip()
        print 'get title = ', title

        found_date = False
        durations = tree.xpath(self.xpaths['duration'])
        if len(durations) > 0:
            duration = durations[0].strip()
            m = re.match(ur'(\d+)月(\d+)日\s+(\d+):(\d+)\s+-\s+(\d+)月(\d+)日\s+(\d+):(\d+)', duration)
            if m:
                start_date = self.get_date(m.group(1), m.group(2))
                start_time = self.get_time(m.group(3), m.group(4))
                end_date = self.get_date(m.group(5), m.group(6))
                end_time = self.get_time(m.group(7), m.group(8))
                found_date = True
        if not found_date:
            start_datetime = tree.xpath(self.xpaths['start_datetime'])[0].strip()
            m = re.search(ur'(\d+)月(\d+)日\s+(\d+):(\d+)', start_datetime)
            start_date = self.get_date(m.group(1), m.group(2))
            start_time = self.get_time(m.group(3), m.group(4))

            end_datetime = tree.xpath(self.xpaths['end_datetime'])[0].strip()
            m = re.search(ur'(\d+)月(\d+)日\s+(\d+):(\d+)', end_datetime)
            end_date = self.get_date(m.group(1), m.group(2))
            end_time = self.get_time(m.group(3), m.group(4))

        print 'start_date = ', start_date

        location = tree.xpath(self.xpaths['location'])[0].strip()
        print 'location = ', location


        contents = tree.xpath(self.xpaths['content'])
        content = '\n'.join([n for n in contents if n.strip()])
        print 'content = ', content[:20]

        city_name = location[:2]
        city = City.objects.get(name=city_name)
        print 'city = ', city, 'city_id = ', city.id

        source = u'新浪微博'
        weight = 60 + random.randint(0,10)
        public = 0

        try:
            activity = Activity.objects.get(url=url.url, start_date=start_date)
        except:
            activity = Activity()


        activity.title = title
        activity.content = content
        activity.start_date = start_date
        activity.start_time = start_time
        activity.end_date = end_date
        activity.end_time = end_time
        activity.location = location
        activity.url = url.url
        activity.city = city
        activity.weight = weight
        activity.public = public
        activity.source = source
        activity.save()

        url.status = 'd'
        url.crawl_start_time = crawl_start_time
        url.crawl_end_time = datetime.datetime.now()
        url.save()

        print 'Done.'

class DamaiBot(Bot):
    def __init__(self):
         self.xpaths = {
                 'title': u'//h1/text()',
                 'start_datetime': u'//div[@class="ri-t"]/time/@datetime',
                 'location': u'//span[@itemprop="location"]/span[1]/text()',
                 'content': u'//div[@class="tab-all-infor-all"]/div[1]/descendant-or-self::*/text()',
                 'city': u'//p[@class="city-name"]/text()',
                 }
         super(DamaiBot, self).__init__()

    def get_date(self, year, month, day):
        ans = datetime.date(int(year), int(month), int(day))
        return ans


    def scrap(self, url):
        crawl_start_time = datetime.datetime.now()
        tree = self.get_tree(url)
        if tree is None:
            return

        title = tree.xpath(self.xpaths['title'])[0].strip()
        print 'get title = ', title

        start_datetime = tree.xpath(self.xpaths['start_datetime'])[0].strip()
        m = re.search(ur'(\d+)-(\d+)-(\d+)T(\d+):(\d+)', start_datetime)
        start_date = self.get_date(m.group(1), m.group(2), m.group(3))
        start_time = self.get_time(m.group(4), m.group(5))

        print 'start_date = ', start_date

        location = tree.xpath(self.xpaths['location'])[0].strip()
        print 'location = ', location


        contents = tree.xpath(self.xpaths['content'])
        content = '\n'.join([n for n in contents if n.strip()])
        print 'content = ', content[:20]

        city_name = tree.xpath(self.xpaths['city'])[0].strip()[:2]
        city = City.objects.get(name=city_name)
        print 'city = ', city, 'city_id = ', city.id

        source = u'大麦'
        weight = 75 + random.randint(0,10)
        public = 0

        try:
            activity = Activity.objects.get(url=url.url, start_date=start_date)
        except:
            activity = Activity()


        activity.title = title
        activity.content = content
        activity.start_date = start_date
        activity.start_time = start_time
        activity.location = location
        activity.url = url.url
        activity.city = city
        activity.weight = weight
        activity.public = public
        activity.source = source
        activity.save()

        url.status = 'd'
        url.crawl_start_time = crawl_start_time
        url.crawl_end_time = datetime.datetime.now()
        url.save()

        print 'Done.'

class DoubanBot(Bot):
    def __init__(self):
        super(DoubanBot, self).__init__()
        self.interval = 7 # in seconds

    def get_date(self, year, month, day):
        ans = datetime.date(int(year), int(month), int(day))
        return ans

    def scrap(self, url):
        crawl_start_time = datetime.datetime.now()
        print '-'*100 + '\n' + url.url
        m = re.search(r'http://www\.douban\.com/event/(\d+)/?$', url.url)
        event_id = m.group(1)
        api_url = 'http://api.douban.com/v2/event/%s' % event_id
        print '-'*100 + '\n-->' + api_url

        page = self.opener.open(api_url).read().decode(self.encoding)
        data = json.loads(page)

        m = re.search(ur'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', data['begin_time'])
        start_date = self.get_date(m.group(1), m.group(2), m.group(3))
        start_time = self.get_time(m.group(4), m.group(5))

        m = re.search(ur'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', data['end_time'])
        end_date = self.get_date(m.group(1), m.group(2), m.group(3))
        end_time = self.get_time(m.group(4), m.group(5))

        city = City.objects.get(name=data['loc_name'])
        print 'city = ', city, 'city_id = ', city.id

        weight = 60 + random.randint(0,10)
        public = False
        source = '豆瓣'

        try:
            activity = Activity.objects.get(url=url.url, start_date=start_date)
        except:
            activity = Activity()

        activity.title = data['title']
        activity.content = data['content']
        activity.start_date = start_date
        activity.start_time = start_time
        activity.end_date = end_date
        activity.end_time = end_time
        activity.location = data['address']
        activity.url = url.url
        activity.city = city
        activity.weight = weight
        activity.public = public
        activity.source = source
        activity.save()

        url.status = 'd'
        url.crawl_start_time = crawl_start_time
        url.crawl_end_time = datetime.datetime.now()
        url.save()

        print 'Done.'

bot_routes = (
        (r'^http://[\w\d\.]*weibo\.com', 'WeiboBot'),
        (r'^http://union\.damai\.cn', 'DamaiBot'),
        (r'^http://www\.douban\.com', 'DoubanBot'),
        (r'^http://www\.headin\.cn', 'HeadinBot'),
        )

instances = {}
for route in bot_routes:
    instances[route[1]] = globals()[route[1]]()


def run():
    urls = StartURL.objects.filter(status='s')
    for url in urls:
        for route in bot_routes:
            if re.search(route[0], url.url):
                instances[route[1]].add(url)
                break

    for instance in instances:
        instances[instance].run()

if __name__ == '__main__':
    from tendo import singleton
    me = singleton.SingleInstance()
    run()
