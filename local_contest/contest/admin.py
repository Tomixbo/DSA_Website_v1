from django.contrib import admin
from .models import Competition

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_time', 'end_time', 'created_at')
    list_filter = ('start_time', 'end_time')
    search_fields = ('name', 'description')
    ordering = ('name',)

admin.site.register(Competition, CompetitionAdmin)
