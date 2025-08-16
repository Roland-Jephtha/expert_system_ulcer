from django.contrib import admin
from .models import Report

admin.site.register(Report)


# Change Admin site headers and titles
admin.site.site_header = "Ulcer Expert System Administration"
admin.site.site_title = "Ulcer Expert System Admin Portal"
admin.site.index_title = "Welcome to Ulcer Expert System Dashboard"
# Register your models here.
