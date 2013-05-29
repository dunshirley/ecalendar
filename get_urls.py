#encoding=utf-8
#!/usr/bin/env python
import os, urllib2,re
from lxml import etree

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huodongrili.settings")
from app.models import City, StartURL

class Url(object):
    def __init__(self, url):
        self.url = url

    def save(self):
        try:
            url_model = StartURL.objects.get(url=self.url)
        except StartURL.DoesNotExist:
            url_model = StartURL()
            url_model.url = self.url
            url_model.save()

class FindUrl(object):
    def __init__(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible; EventsCalendarbot/1.0; +http://huodongrili.com/bot)')]

    def get_citys(self):
        return (i.pinyin for i in City.objects.all())

    def get_html_etree(self, url):
        try:
            page = self.opener.open(url).read()
            return etree.HTML(page)
        except:pass

class DoubanUrl(FindUrl):
    def __init__(self):
        super(DoubanUrl, self).__init__()
        self.url_type = "http://www.douban.com/location/%s/events/%s"
        self.city_map = {u'电影-展览': 'future-1802',
                         u'展览': 'future-exhibition',
                         u'讲座': 'future-salon',
                         u'主题放映': 'future-1801',
                         }

    def city_urls(self):
        citys = self.get_citys()
        return [self.url_type % (m, n) for m in citys for n in self.city_map.values()]


    def out_url(self, html_etree, xpath):
       return html_etree.xpath(xpath)

    def max_url(self, html_etree):
        xpath = "//div[@class='paginator']/a/@href"
        tag_a = html_etree.xpath(xpath)
        max_page = 10
        for a in tag_a:
            number = re.match(r'\?start=(\d+)', a)
            if number:
                tmp_max = int(number.group(1))
                if max_page < tmp_max: max_page = tmp_max
        print "get_max_page:" + str(max_page)
        return max_page

    def run(self, sleep_time):
        for city_url in self.city_urls():
            tree = self.get_html_etree(city_url)
            max_page = self.max_url(tree)
            for i in range(10, max_page+10, 10):
                next_page = city_url + "?start=%s" % i
                print next_page
                next_page_tree = self.get_html_etree(next_page)
                urls = self.out_url(next_page_tree, "//div[@class='title']/a[@title]/@href")
                for url in urls: Url(url).save()
                print "sleep " + str(sleep_time)
                time.sleep(sleep_time)

if __name__ == '__main__':
    a = DoubanUrl()
    a.run(120)
