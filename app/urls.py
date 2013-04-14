from django.conf.urls import patterns, url                                                                                                                               

from app.views import *                                                        
from app.models import *                                                       

urlpatterns = patterns('app.views', 
    url(r'^calendar/$', 'calendar'),
    url(r'^activities/?$', 'activities'),
)
