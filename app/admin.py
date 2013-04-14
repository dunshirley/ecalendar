from django.contrib import admin
from django import forms
from app.models import *

class CalendarAdmin(admin.ModelAdmin):
    list_display = ('date', 'name')
    list_filter = ('date', 'name')
    ordering = ('date',)

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        widgets = {
            'tags':forms.SelectMultiple(attrs={'size': 12})
        }

class ActivityAdmin(admin.ModelAdmin):
    form = ActivityForm
    list_display = ('public', 'start_date', 'start_time', 'end_date', 'end_time', 'title', 'weight', 'abstract', 'created_time', 'modified_time')
    list_filter = ('public', 'start_date', 'end_date', 'weight', 'tags', 'source',)
    search_fields = ['title', 'content']
    ordering = ('start_date', 'start_time', '-weight')

    def abstract(self, obj):
        return obj.content[:40]

class StartURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'crawl_start_time', 'crawl_end_time')

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(City)
admin.site.register(Tag)
admin.site.register(Device)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Reaction)
admin.site.register(Feedback)
admin.site.register(StartURL, StartURLAdmin)
