#encoding:utf-8
import json
from datetime import date
from django.http import HttpResponse

from app.models import *

def calendar(request):
    data = {}
    data['result'] = 'ok'
    today = date.today()
    data['data'] = [{one.date.strftime('%Y-%m-%d'):one.name} for one in Calendar.objects.filter(date__gte=today)]
    return HttpResponse(json.dumps(data), content_type="application/json")
