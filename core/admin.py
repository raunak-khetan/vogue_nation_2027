
from django.contrib import admin
from .models import GN_MTeam, GN_MTeamLeader, GN_MMember


@admin.register(GN_MTeam)
class GN_MTeamAdmin(admin.ModelAdmin):
    list_display = ("teamName", "submitPerformances")
    search_fields = ("teamName",)


@admin.register(GN_MTeamLeader)
class GN_MTeamLeaderAdmin(admin.ModelAdmin):
    list_display = (
        "fullName",
        "contactNumber",
        "email",
        "team",
    )
    search_fields = (
        "fullName",
        "email",
        "contactNumber",
        "team__teamName",
    )
    list_filter = ("gender",)


@admin.register(GN_MMember)
class GN_MMemberAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "contactNumber",
        "gender",
        "team",
    )
    search_fields = (
        "name",
        "email",
        "contactNumber",
        "team__teamName",
    )
    list_filter = ("gender",)

# Register your models here.
