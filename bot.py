import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "huodongrili.settings")

from app.models import *

class Bot:
    def __init__(self):
        self.urls = set()

    def add(self, url):
        self.urls.add(url)
        
    def run(self):


if __name__ == '__main__':
    urls = StartURL.objects.filter(status='s')
    for url in urls:
        print url.url

