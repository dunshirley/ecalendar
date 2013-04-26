from datetime import date
from django.contrib import admin
from django import forms
from django.contrib.admin import SimpleListFilter
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

class OutdatedListFilter(SimpleListFilter):
    title = 'Outdated'
    parameter_name = 'outdated'

    def lookups(self, request, model_admin):
        return (
                ('Yes', 'Yes'),
                ('No', 'No'),
                )
    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == 'Yes':
            return queryset.filter(start_date__lt=today)
        else:
            return queryset.filter(start_date__gte=today)


class ActivityAdmin(admin.ModelAdmin):
    form = ActivityForm
    list_display = ('title', 'abstract', 'public', 'source', 'start_date', 'start_time', 'end_date', 'end_time', 'weight', 'created_time', 'modified_time')
    list_display_links = ('public', 'start_date')
    list_editable = ('weight',)
    list_filter = (OutdatedListFilter, 'public', 'city', 'start_date', 'end_date', 'weight', 'tags', 'source',)
    search_fields = ['title', 'content']
    ordering = ('-start_date', '-start_time', '-weight')
    actions = ['make_public', 'make_private', 'recrawl']

    def make_public(self, request, queryset):
        queryset.update(public=True)
    make_public.short_description = 'Mark selected as public'

    def make_private(self, request, queryset):
        queryset.update(public=False)
    make_private.short_description = 'Mark selected as private'

    def recrawl(self, request, queryset):
        for obj in queryset:
            try:
                starturl = StartURL.objects.get(url=obj.url)
                starturl.status = 's'
                starturl.save()
            except:
                continue
    recrawl.short_description = 'Re crawl selected'

    def abstract(self, obj):
        ans = obj.content[:20]
        if not ans:
            ans = 'Content is empty.'
        ans = '<a href="' + obj.url + '" target="_blank">' + ans + '</a>'
        return ans
    abstract.allow_tags = True

class StartURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'modified_time', 'crawl_start_time', 'crawl_end_time', 'go')
    list_display_links = ('url', 'modified_time',)
    list_filter = ('status',)
    search_fields = ['url']
    ordering = ('-modified_time',)
    actions = ['make_submitted']

    def make_submitted(self, request, queryset):
        queryset.update(status='s')
    make_submitted.short_description = 'Mark selected URL as submitted status'

    def go(self, obj):
        return '<a href="' + obj.url + '" target="_blank">go</a>'
    go.allow_tags = True


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
admin.site.register(Apk)
