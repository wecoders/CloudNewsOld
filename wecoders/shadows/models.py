from django.db import models

# Create your models here.

class User(models.Model):
    #id = models.IntegerField(default=0)
    username = models.CharField(max_length=250, default=None)
    
    t = models.LongField(default=0)
    u = models.LongField(default=0)
    d = models.LongField(default=0)
	plan = models.CharField(max_length=200)
	port = models.IntegerField(default=0)
	port_password = models.CharField(max_length=200)
    max_bytes = models.LongField(default=0)
	transfer_enable = models.LongField(default=0)
	enable = models.IntegerField(default=0)
	last_reset_plan = models.IntegerField(default=0)
	last_reset_passwd = models.IntegerField()
    created_at = models.DateField()
    
    class Meta:
        db_table = "ss_user"

    def __unicode__(self):              # __unicode__ on Python 2
        return "%d - %s - %s - %s" %(self.id, self.username , self.title, self.url)


