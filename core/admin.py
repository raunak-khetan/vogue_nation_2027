from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import HCDTeam, HCDTeamLeader, HCDMember


@admin.register(HCDTeam)
class HCDTeamAdmin(admin.ModelAdmin):
    list_display = ("id", "teamName", "submitPerformances")
    search_fields = ("teamName",)
    list_per_page = 25


@admin.register(HCDTeamLeader)
class HCDTeamLeaderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fullName",
        "team",
        "contactNumber",
        "email",
        "gender",
        "cityName",
    )

    search_fields = (
        "fullName",
        "email",
        "contactNumber",
        "team__teamName",
    )

    list_filter = ("gender", "cityName")
    list_per_page = 25


@admin.register(HCDMember)
class HCDMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "team",
        "email",
        "contactNumber",
        "gender",
        "cityName",
    )

    search_fields = (
        "name",
        "email",
        "contactNumber",
        "team__teamName",
    )

    list_filter = ("gender", "cityName")
    list_per_page = 25
