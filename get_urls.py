#encoding=utf-8
#!/usr/bin/env python
import os, urllib2, re, time
from lxml import etree

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huodongrili.settings")
#from app.models import City, StartURL

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
    def save_csv(self, file_handle):
        file_handle.write(self.url+"\n")

class FindUrl(object):
    def __init__(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (compatible; EventsCalendarbot/1.0; +http://huodongrili.com/bot)')]

    def get_citys(self):
        return (i.pinyin for i in City.objects.all())

    def out_url(self, html_etree, xpath):
       return html_etree.xpath(xpath)


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

class HeadinUrl(FindUrl):
    def __init__(self):
        super(HeadinUrl, self).__init__()
        self.source_url = "http://www.headin.cn/OutWall/WallActivityList/?page=%s&type=not&searchName=&tag=&city=&tagType=0&_=1369796509070"

    def get_max_page(self, html_etree, xpath):
        nothing = html_etree.xpath(xpath)
        if nothing:
            return False
        else:
            return True

    def result_url(self, cur_dir, url):
        base_name = os.path.basename(url)
        return cur_dir + '/' + base_name

    def run(self, sleep_time, file_handle):
        for i in range(1, 201):
            process_url = self.source_url % i
            html_etree = self.get_html_etree(process_url)
            begin = self.get_max_page(html_etree, "//div[@class='nothingBox']/text()")
            print process_url, begin
            urls = self.out_url(html_etree, "//div[@class='info']/h3/a/@href")
            for url in urls:
                url = self.result_url("http://www.headin.cn/Themes/Activity/Details", url)
                Url(url).save()
            time.sleep(sleep_time)
            if not begin: break

class SinaUrl(HeadinUrl):
    def __init__(self):
        super(SinaUrl, self).__init__()
        self.source_url = 'http://event.weibo.com/eventlist?type=1&class=5&p=%s'

    def run(self, sleep_time):
        for i in range(1, 2):
            process_url = self.source_url % i
            html_etree = self.get_html_etree(process_url)
            begin = self.get_max_page(html_etree, "//div[@class='ev_listNoEv']/text()")
            print process_url, begin
            urls = self.out_url(html_etree, "//div[@class='evlist_img']/a/@href")
            print urls
            for url in urls:
                url = self.result_url(url, "http://event.weibo.com")
                Url(url).save()
            time.sleep(sleep_time)
            if not begin: break

class DamaiUrl(HeadinUrl):
    def __init__(self):
        super(DamaiUrl, self).__init__()
        self.source_url ='http://www.damai.cn/projectlist.aspx?%s&pageIndex=%s'

    def result_url(self, cur_dir, url):
        base_name = re.search("\d+", url)
        if base_name:
            return cur_dir % base_name.group(0)
        else:return False
    def run(self, sleep_time):
        find_list = ('mcid=1&ccid=10', 'mcid=1&ccid=12', 'mcid=3&ccid=21',
                     'mcid=3&ccid=19', 'mcid=4&ccid=26', 'mcid=6&ccid=33'
                    )
        for one in find_list:
            for i in range(1, 201):
                process_url = self.source_url % (one, i)
                html_etree = self.get_html_etree(process_url)
                if not html_etree:break
                begin = self.get_max_page(html_etree, "//div[@class='dm-nodata-text pl10 mt15 mb15']/text()")
                print process_url, begin
                urls = self.out_url(html_etree, "//div[@class='ri-infos']/h2/a/@href")
                for url in urls:
                    url = self.result_url("http://union.damai.cn/gotoUnion.aspx?pid=%s&sourceCode=3278020", url)
                    if url:Url(url).save()
                time.sleep(sleep_time)
                if not begin: break

def run():
    instance_list = (
            'DamaiUrl' ,
            'HeadinUrl',)
    for i in instance_list:
        eval(i)().run(10)
    out.close()


if __name__ == '__main__':
    from tendo import singleton
    me = singleton.SingleInstance()
    run()
