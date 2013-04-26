#encoding:utf-8
import json
from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import redirect

from app.models import *

error_resp = HttpResponse(json.dumps({"result":"error"}, ensure_ascii=False), content_type="application/json; charset=utf-8")

def calendar(request):
    if 'last_timestamp' in request.GET:
        last_timestamp = request.GET['last_timestamp']
    else:
        last_timestamp = 0
    last_date = datetime.fromtimestamp(float(last_timestamp))

    data = {}
    data['result'] = 'ok'
    today = date.today()
    data['data'] = [{"date":one.date.strftime('%Y-%m-%d'),"name":one.name} for one in Calendar.objects.filter(date__gte=today, modified_time__gte=last_date)]
    data['timestamp'] = datetime.today().strftime('%s')
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8")

def activities(request):
    if 'city' not in request.GET:
        return error_resp
    city = request.GET['city']
    if not City.objects.filter(pinyin=city):
        return error_resp
    city = City.objects.get(pinyin=city)
    if 'last_timestamp' in request.GET:
        last_timestamp = request.GET['last_timestamp']
    else:
        last_timestamp = 0
    last_date = datetime.fromtimestamp(float(last_timestamp))

    data = {}
    data['result'] = 'ok'
    today = date.today()
    two_months_later = today + timedelta(days=62)
    data['timestamp'] = datetime.today().strftime('%s')
    activities = Activity.objects.filter(start_date__gte=today, start_date__lte=two_months_later, modified_time__gte=last_date, city=city, public=True)
    ans = []
    for activity in activities:
        one = {}
        one['id'] = str(activity.id)
        one['start_date'] = activity.start_date.strftime('%Y-%m-%d')
        if activity.start_time:
            one['start_time'] = activity.start_time.strftime('%H:%M')
        else:
            one['start_time'] = ''
        if activity.end_date:
            one['end_date'] = activity.end_date.strftime('%Y-%m-%d')
        else:
            one['end_date'] = ''
        if activity.end_time:
            one['end_time'] = activity.end_time.strftime('%H:%M')
        else:
            one['end_time'] = ''
        one['title'] = activity.title
        one['content'] = activity.content
        one['location'] = activity.location
        one['url'] = activity.url
        one['source'] = activity.source
        one['weight'] = activity.weight
        one['tags'] = [t.name for t in activity.tags.all()]
        ans.append(one)

    data['data'] = ans
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8")

def reaction(request):
    post = json.loads(request.body)
    if 'device_id' not in post or 'data' not in post:
        return error_resp

    reactions = post['data']
    device_id = post['device_id']
    device, _ = Device.objects.get_or_create(identification=device_id, os='a')

    for reaction in reactions:
        activity_id = reaction['activity_id']
        like = reaction['like'] == '1'
        dislike = reaction['dislike'] == '1'
        clicked = reaction['clicked'] == '1'
        if not Activity.objects.filter(id=activity_id):
            return error_resp
        activity = Activity.objects.get(id=activity_id)
        reaction = Reaction(activity=activity, device=device, 
                like=like, dislike=dislike, clicked=clicked)
        reaction.save()

    data = {'result':'ok'}
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8")

def feedback(request):
    post = json.loads(request.body)
    if 'device_id' not in post or 'data' not in post:
        return error_resp

    content = post['data']
    device_id = post['device_id']
    device, _ = Device.objects.get_or_create(identification=device_id, os='a')

    feedback = Feedback(content=content, device=device)
    feedback.save()
    
    data = {'result':'ok'}
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8")

def update(request):
    data = {'has_new':'0', 'result':'ok'}
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8")

def download(request):
    if 'version' in request.GET:
        version = request.GET['version']
        try:
            apk = Apk.objects.get(version=version)
        except:
            return error_resp
    else:
        try:
            apk = Apk.objects.all().order_by('-id')[0]
        except:
            return error_resp

    data = {'result':'/download/' + apk.apkfile.url}
    return redirect('/download/' + apk.apkfile.url)
    return HttpResponse(json.dumps(data), content_type="application/json")


def bot(request):
    data = """
    <!DOCTYPE html>
    <html>
    <head><title>EventsCalendar Bot</title></head>
    <body>
    <h1>EventsCalendar Bot</h1>
    <p>
    EventsCalendarBot is EventsCalendar's web crawling bot (sometimes also called a "spider"). 
    Crawling is the process by which EventsCalendarBot discovers new and updated pages to be added to the EventsCalendar index.
    </p>

    <p>
    We use a set of computers to fetch (or "crawl") pages on the web. 
    EventsCalendarBot uses an algorithmic process: 
    computer programs determine which sites to crawl, how often, and how many pages to fetch from each site.
    </p>

    <p>
    EventsCalendarBot's crawl process begins with a list of webpage URLs, 
    generated from previous crawl processes and augmented with Sitemap data provided by webmasters.
    As EventsCalendarBot visits each of these websites it detects links (SRC and HREF) on each page and adds them to its list of pages to crawl. 
    New sites, changes to existing sites, and dead links are noted and used to update the EventsCalendar index.
    </p>
    <p>
    If you find EventsCalendarBot abnormally accesses your website(for example in a much higher frequency), please report to <a href="mailto:i@liangsun.org">Liang Sun</a>.
    </p>
    </body>
    </html>
    """
    return HttpResponse(data)
