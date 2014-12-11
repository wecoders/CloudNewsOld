from django.db import models


class News(models.Model):
    # id = models.IntegerField(default=0)
    news_id = models.CharField(max_length=250, default=None)
    site = models.CharField(max_length=200)
    title = models.CharField(max_length=250)
    sub_title = models.CharField(max_length=250)
    url = models.CharField(max_length=250, default=None, blank=True)
    source_url = models.CharField(max_length=250, default=None, blank=True)
    sorts = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    vote_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = "news"

    def __unicode__(self):              # __unicode__ on Python 2
        return "%d - %s - %s - %s" %(self.id, self.site , self.title, self.url)

class NewsSite(models.Model):
    # id = models.IntegerField(default=0)
    uri = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=255, default=None, blank=True)
    sorts = models.IntegerField(default=0)
    domain = models.CharField(max_length=200, default=None, blank=True)
    author = models.CharField(max_length=200, default=None, blank=True)
    bg_color = models.CharField(max_length=200, default=None, blank=True)
    status = models.IntegerField(default=0)
    show_votes = models.IntegerField(default=0)
    show_comments = models.IntegerField(default=0)

    class Meta:
        db_table = "news_site"

    def __unicode__(self):              # __unicode__ on Python 2
        return "%s - %s - %s" %(self.name , self.title, self.domain)