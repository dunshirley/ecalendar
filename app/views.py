#encoding:utf-8
import json
from datetime import date, datetime, timedelta
from django.http import HttpResponse

from app.models import *

error_resp = HttpResponse(json.dumps({"result":"error"}))

def calendar(request):
    data = {}
    data['result'] = 'ok'
    today = date.today()
    data['data'] = [{"date":one.date.strftime('%Y-%m-%d'),"name":one.name} for one in Calendar.objects.filter(date__gte=today)]
    return HttpResponse(json.dumps(data), content_type="application/json")

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
    last_date = date.fromtimestamp(float(last_timestamp))
    data = {}
    data['result'] = 'ok'
    today = date.today()
    two_months_later = today + timedelta(days=62)
    data['timestamp'] = datetime.today().strftime('%s')
    activities = Activity.objects.filter(start_date__gte=today, start_date__lte=two_months_later, modified_time__gt=last_date, city=city)
    ans = []
    for activity in activities:
        one = {}
        one['start_date'] = activity.start_date.strftime('%Y-%m-%d')
        if activity.start_time:
            one['start_time'] = activity.start_time.strftime('%M:%S')
        if activity.end_date:
            one['end_date'] = activity.end_date.strftime('%Y-%m-%d')
        if activity.end_time:
            one['end_time'] = activity.end_time.strftime('%M:%S')
        one['title'] = activity.title
        one['content'] = activity.content
        one['location'] = activity.location
        one['url'] = activity.url
        one['source'] = activity.source
        one['weight'] = activity.weight
        one['tags'] = [t.name for t in activity.tags.all()]
        ans.append(one)

    data['data'] = ans
    return HttpResponse(json.dumps(data), content_type="application/json")

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
    return HttpResponse(json.dumps(data), content_type="application/json")

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
    return HttpResponse(json.dumps(data), content_type="application/json")

def download(request):
    data = {'has_new':'0', 'result':'ok'}
    return HttpResponse(json.dumps(data), content_type="application/json")


