from django.contrib import admin

# Register your models here.
from models import News, NewsSite

class NewsSiteAdmin(admin.ModelAdmin):
	pass

admin.site.register(News)
admin.site.register(NewsSite, NewsSiteAdmin)

