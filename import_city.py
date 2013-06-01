#encoding:utf-8
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huodongrili.settings")

from app.models import *

f = open('city')
for line in f:
    name, pinyin = line.split()
    pinyin = pinyin.lower()
    print name, pinyin
    city = City()
    city.name = name
    city.pinyin = pinyin
    city.save()
f.close()
