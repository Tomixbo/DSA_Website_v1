from django.contrib import admin
from .models import DefinedFile, Challenge, Level, Performance
from .forms import DefinedFileAdminForm


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'published')
    list_filter = ('published','author')

class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'challenge_name')
    list_filter = ('challenge__name',)

    def challenge_name(self, obj):
        return obj.challenge.name

class DefinedFileAdmin(admin.ModelAdmin):
    form = DefinedFileAdminForm
    list_display = ('name', 'level_name', 'challenge_name')
    list_filter = ('level__name', 'level__challenge__name')

    def level_name(self, obj):
        return obj.level.name

    def challenge_name(self, obj):
        return obj.level.challenge.name
    
    # Optionally, add short descriptions for these methods
    level_name.short_description = 'Level Name'
    challenge_name.short_description = 'Challenge Name'

class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'definedfile', 'solved', 'description', 'created_at')
    list_filter = ('user', 'definedfile__level__challenge', 'definedfile__level', 'definedfile')
    search_fields = ('user__username', 'definedfile__name', 'description')

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(DefinedFile, DefinedFileAdmin)
admin.site.register(Performance, PerformanceAdmin)