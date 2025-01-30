from django.contrib import admin
from .models import Team, Invitation

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'get_members_count', 'get_contests')
    search_fields = ('name', 'owner__username')
    list_filter = ('contests',)
    filter_horizontal = ('members',)  # ✅ Permet de gérer les membres dans Django Admin

    def get_members_count(self, obj):
        return obj.members.count()
    get_members_count.short_description = "Number of Members"

    def get_contests(self, obj):
        return ", ".join([contest.name for contest in obj.contests.all()])
    get_contests.short_description = "Contests"


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'status')  # ✅ Affichage des colonnes principales
    list_filter = ('status', 'team')  # ✅ Filtres pour mieux naviguer
    search_fields = ('user__username', 'team__name')  # ✅ Recherche par nom d'utilisateur et nom d'équipe
    ordering = ('status',)  # ✅ Trie par statut d'invitation

    # ✅ Ajout de la modification du statut en mode liste
    list_editable = ('status',)
    
    # ✅ Méthode pour voir les membres invités et leurs équipes
    def get_team_name(self, obj):
        return obj.team.name
    get_team_name.short_description = "Nom de l'équipe"

    def get_user_name(self, obj):
        return obj.user.username
    get_user_name.short_description = "Utilisateur"

