from django.db import models

class Activity(models.Model):
    title = models.CharField(max_length=2000)
    content = models.CharField(max_length=10000)
    url = models.CharField(max_length=1000)
    source = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    weight = models.IntegerField(blank=True, null=True)
    public = models.NullBooleanField()

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField('Tag', blank=True)

    def __unicode__(self):
        return self.title
    

class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Calendar(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return str(self.date) + '(' + self.name + ')'

