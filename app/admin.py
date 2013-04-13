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
    list_display = ('start_date', 'start_time', 'end_date', 'end_time', 'title', 'weight', 'abstract',)
    list_filter = ('start_date', 'end_date', 'weight', 'tags', 'source')
    search_fields = ['title', 'content']
    ordering = ('start_time', 'weight')

    def abstract(self, obj):
        return obj.content[:100]



admin.site.register(Calendar, CalendarAdmin)
admin.site.register(City)
admin.site.register(Tag)
admin.site.register(Device)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Reaction)
admin.site.register(Feedback)
