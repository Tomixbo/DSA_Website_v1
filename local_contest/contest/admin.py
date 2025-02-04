from django.contrib import admin
from .models import Contest, ContestChallenge

class ContestChallengeInline(admin.TabularInline):
    model = ContestChallenge
    extra = 1  # ✅ Adds an empty field to select a challenge
    autocomplete_fields = ['challenge']  # ✅ Enables search for existing challenges

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'is_finished', 'team_members_max')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)
    inlines = [ContestChallengeInline]  # ✅ Allows adding/removing challenges
    filter_horizontal = ('teams',)  # ✅ Allows easy selection/removal of participants

@admin.register(ContestChallenge)
class ContestChallengeAdmin(admin.ModelAdmin):
    list_display = ('contest', 'challenge')
    search_fields = ('contest__name', 'challenge__name')
