#encoding:utf-8
import os, re
import time
import urllib2
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

class WeiboBot(Bot):
    def __init__(self):
         self.xpaths = {
                 'title': u'//div[@id="pl_event_copy"]/strong/text()|//h3[@class="ev_title"]/text()',
                 'duration': u'//div[contains(@class,"ev_detail_cont")]/p[1]/span[2]/text()',
                 'start_datetime': u'//span[contains(text(),"开始时间")]/../span[2]/text()',
                 'end_datetime': u'//span[contains(text(),"结束时间")]/../span[2]/text()',
                 'location': u'//span[contains(text(),"地　　点")]/../span[2]/text()',
                 'content': u'//div[@class="ev_details"]/text()|//div[@class="ev_details"]/*/text()',
                 }
         super(WeiboBot, self).__init__()

    def scrap(self, url):
        tree = self.get_tree(url)
        if not tree:
            return
        
        try:
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
            weight = 60
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
            url.save()

            print 'Done.'
        except Exception, e:
            print e
            #url.status = 'e'
        finally:
            pass

class DamaiBot(Bot):
    def __init__(self):
         self.xpaths = {
                 'title': u'//div[@id="pl_event_copy"]/strong/text()|//h3[@class="ev_title"]/text()',
                 'duration': u'//div[contains(@class,"ev_detail_cont")]/p[1]/span[2]/text()',
                 'start_datetime': u'//span[contains(text(),"开始时间")]/../span[2]/text()',
                 'end_datetime': u'//span[contains(text(),"结束时间")]/../span[2]/text()',
                 'location': u'//span[contains(text(),"地　　点")]/../span[2]/text()',
                 'content': u'//div[@class="ev_details"]/*/text()',
                 }
         super(WeiboBot, self).__init__()

    def scrap(self, url):
        tree = self.get_tree(url)
        if not tree:
            return
        
        try:
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
            content = '\n'.join(contents)
            print 'content = ', content[:20]

            city_name = location[:2]
            city = City.objects.get(name=city_name)
            print 'city = ', city, 'city_id = ', city.id

            source = u'新浪微博'
            weight = 60
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
            url.save()

            print 'Done.'
        except Exception, e:
            print e
            #url.status = 'e'
        finally:
            pass


bot_routes = (
        (r'^http://[\w\d\.]*weibo.com', 'WeiboBot'),

        )

instances = {}
for route in bot_routes:
    instances[route[1]] = globals()[route[1]]()


if __name__ == '__main__':
    urls = StartURL.objects.filter(status='s')
    for url in urls:
        for route in bot_routes:
            if re.search(route[0], url.url):
                instances[route[1]].add(url)
                break

    for instance in instances:
        instances[instance].run()
