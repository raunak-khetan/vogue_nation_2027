from django.contrib import admin

from .models import SOD_Member_detail, SOD_Team

# Inline members inside team detail
class SOD_MemberInline(admin.TabularInline):
    model         = SOD_Member_detail
    extra         = 0           # no blank rows by default
    can_delete    = True
    show_change_link = True
    fields        = ('name', 'gender', 'email', 'phone', 'city', 'postal_code')
    readonly_fields = ('email',)   # email is unique

# SOD Team admin
@admin.register(SOD_Team)
class SOD_TeamAdmin(admin.ModelAdmin):
    # List view
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

    # Detail view
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

    # Member count column
    @admin.display(description='Members')
    def member_count(self, obj):
        return obj.members.count()


@admin.register(SOD_Member_detail)
class SOD_MemberAdmin(admin.ModelAdmin):
    # List view
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

    # Detail view
    fieldsets = (
        (None, {
            'fields': ('team', 'name', 'gender'),
        }),
        ('Contact', {
            'fields': ('email', 'phone', ('city', 'postal_code')),
        }),
    )
    readonly_fields = ('email',)
