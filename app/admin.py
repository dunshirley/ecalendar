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
    ordering = ('-start_date', '-start_time', '-weight')

    def abstract(self, obj):
        return obj.content[:40]

class StartURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'modified_time', 'crawl_start_time', 'crawl_end_time')
    ordering = ('-modified_time',)
    actions = ['make_submitted']

    def make_submitted(self, request, queryset):
        queryset.update(status='s')
    make_submitted.short_description = 'Mark selected URL as submitted status'


class ReactionAdmin(admin.ModelAdmin):
    list_display = ('activity', 'device', 'like', 'dislike', 'clicked', 'created_time')
    ordering = ('-created_time',)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('content', 'device', 'created_time')
    ordering = ('-created_time',)

class CityAdmin(admin.ModelAdmin):
    list_display = ('pinyin', 'name')
    ordering = ('pinyin',)

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Tag)
admin.site.register(Device)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Reaction, ReactionAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(StartURL, StartURLAdmin)
