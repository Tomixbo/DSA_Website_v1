from django.contrib import admin
from .models import AttendanceCode, UserAttendance

@admin.register(AttendanceCode)
class AttendanceCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'generated_at')  # Colonnes affichées dans la liste
    search_fields = ('code',)  # Ajout de la recherche par code
    list_filter = ('generated_at',)  # Filtre par date de génération

@admin.register(UserAttendance)
class UserAttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'code_used', 'presence_validated')  # Colonnes affichées dans la liste
    search_fields = ('user__username', 'code_used')  # Recherche par utilisateur ou code utilisé
    list_filter = ('date', 'presence_validated')  # Filtres par date et validation
    ordering = ('-date',)  # Tri par date décroissante
