from django.contrib import admin
from app.models import *

class CalendarAdmin(admin.ModelAdmin):
    list_display = ('date', 'name')
    list_filter = ('date', 'name')
    ordering = ('date',)


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(City)
admin.site.register(Tag)
admin.site.register(Device)
admin.site.register(Activity)
admin.site.register(Reaction)
admin.site.register(Feedback)
