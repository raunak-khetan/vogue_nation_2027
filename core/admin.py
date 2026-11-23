from django.contrib import admin

from .models import (
    SOD_Team,
    SOD_Member_detail,
    HCDTeam,
    HCDTeamLeader,
    HCDMember,
    GN_MTeam,
    GN_MTeamLeader,
    GN_MMember,
)


# Glamour Nova Team admin
@admin.register(GN_MTeam)
class GN_MTeamAdmin(admin.ModelAdmin):
    list_display = ("teamName", "submitPerformances")
    search_fields = ("teamName",)


# Glamour Nova Team Leader admin
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


# Glamour Nova Member admin
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


# Inline members inside SOD team detail
class SOD_MemberInline(admin.TabularInline):
    model         = SOD_Member_detail
    extra         = 0
    can_delete    = True
    show_change_link = True
    fields        = ('name', 'gender', 'email', 'phone', 'city', 'postal_code')
    readonly_fields = ('email',)


# SOD Team admin
@admin.register(SOD_Team)
class SOD_TeamAdmin(admin.ModelAdmin):
    list_display  = (
        'team_name',
        'lead_name',
        'lead_gender',
        'lead_email',
        'lead_phone',
        'lead_city',
        'member_count',
    )
    list_filter   = ('lead_gender', 'lead_city')
    search_fields = ('team_name', 'lead_name', 'lead_email', 'lead_phone', 'lead_city')
    ordering      = ('team_name',)
    list_per_page = 25

    fieldsets = (
        ('Team Info', {
            'fields': ('team_name', 'prev_performance'),
        }),
        ('Leader Details', {
            'fields': (
                'lead_name',
                'lead_gender',
                'lead_email',
                'lead_phone',
                ('lead_city', 'lead_postal_code'),
            ),
        }),
    )
    readonly_fields = ('lead_email',)
    inlines        = [SOD_MemberInline]

    @admin.display(description='Members')
    def member_count(self, obj):
        return obj.members.count()


# SOD Member admin
@admin.register(SOD_Member_detail)
class SOD_MemberAdmin(admin.ModelAdmin):
    list_display  = (
        'name',
        'team',
        'gender',
        'email',
        'phone',
        'city',
    )
    list_filter   = ('gender', 'city', 'team')
    search_fields = ('name', 'email', 'phone', 'team__team_name', 'city')
    ordering      = ('team__team_name', 'name')
    list_per_page = 50
    list_select_related = ('team',)

    fieldsets = (
        (None, {
            'fields': ('team', 'name', 'gender'),
        }),
        ('Contact', {
            'fields': ('email', 'phone', ('city', 'postal_code')),
        }),
    )
    readonly_fields = ('email',)


# Haute Couture Team admin
@admin.register(HCDTeam)
class HCDTeamAdmin(admin.ModelAdmin):
    list_display = ("id", "teamName", "submitPerformances")
    search_fields = ("teamName",)
    list_per_page = 25


# Haute Couture Team Leader admin
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


# Haute Couture Member admin
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
