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

from django.contrib import admin
from .models import JoinRequest

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "status", "created_at")  # ✅ Show these fields in the admin panel
    list_filter = ("status", "team")  # ✅ Filter by status and team
    search_fields = ("user__username", "team__name")  # ✅ Search by username or team name
    ordering = ("-created_at",)  # ✅ Sort by newest requests first
    actions = ["accept_requests", "reject_requests"]  # ✅ Bulk actions

    # ✅ Custom Admin Actions for Bulk Approving or Rejecting
    @admin.action(description="Accept selected join requests")
    def accept_requests(self, request, queryset):
        for join_request in queryset.filter(status="pending"):
            join_request.accept()
        self.message_user(request, "Selected requests have been accepted.")

    @admin.action(description="Reject selected join requests")
    def reject_requests(self, request, queryset):
        for join_request in queryset.filter(status="pending"):
            join_request.reject()
        self.message_user(request, "Selected requests have been rejected.")

