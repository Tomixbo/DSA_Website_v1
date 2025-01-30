from django.contrib import admin
from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'get_members_count', 'get_contests')
    search_fields = ('name', 'owner__username')
    list_filter = ('contests',)

    def get_members_count(self, obj):
        return obj.members.count()
    get_members_count.short_description = "Number of Members"

    def get_contests(self, obj):
        return ", ".join([contest.name for contest in obj.contests.all()])
    get_contests.short_description = "Contests"

