from django.contrib import admin

from .models import (
    Branch, Client, Credential, Direction, Instrument, Lead, LegalAct, Post, Project,
    Service, SiteSettings, Stat, TeamMember,
)


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ["order", "slug", "title_uz", "summary_uz"]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Rekvizitlar", {"fields": [
            "brand_name", "brand_descriptor", "org_name_uz", "org_name_ru", "org_name_en",
            "tin", "founded_year", "phone", "phone_second", "email", "telegram",
            "address_uz", "address_ru", "address_en",
            "work_hours_uz", "work_hours_ru", "work_hours_en",
            "bank_details_uz", "bank_details_ru", "bank_details_en", "map_embed",
            "director_uz", "director_ru", "director_en",
            "office_tashkent_uz", "office_tashkent_ru", "office_tashkent_en",
            "map_lat", "map_lng", "experience_years", "staff_total", "staff_energy", "staff_supervision",
        ]}),
        ("Geroy bloki", {"fields": [
            "hero_kicker_uz", "hero_kicker_ru", "hero_kicker_en",
            "hero_title_uz", "hero_title_ru", "hero_title_en",
            "hero_accent_uz", "hero_accent_ru", "hero_accent_en",
            "seo_title_uz", "seo_title_ru", "seo_title_en",
            "hero_text_uz", "hero_text_ru", "hero_text_en",
            "hero_image", "report_turnaround_days",
        ]}),
        ("Kompaniya sahifasi", {"fields": [
            "about_uz", "about_ru", "about_en",
            "quality_policy_uz", "quality_policy_ru", "quality_policy_en",
        ]}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "slug", "accent", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["title_uz"]}
    inlines = [ServiceInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "direction", "order"]
    list_filter = ["direction"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["title_uz"]}


@admin.register(LegalAct)
class LegalActAdmin(admin.ModelAdmin):
    list_display = ["number", "title_uz", "verified_on", "effective_on", "order"]
    list_filter = ["verified_on"]
    list_editable = ["order"]
    filter_horizontal = ["directions"]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name_uz", "sector", "featured", "order"]
    list_filter = ["sector", "featured"]
    list_editable = ["featured", "order"]
    search_fields = ["name_uz", "name_ru"]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["city_uz", "head", "phone", "is_head_office", "order"]
    list_editable = ["order"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "client", "direction", "year", "order"]
    list_filter = ["direction", "year"]
    list_editable = ["order"]
    search_fields = ["title_uz", "title_ru", "client"]
    prepopulated_fields = {"slug": ["title_uz"]}


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ["name_uz", "serial", "certificate_no", "verified_on", "valid_until", "order"]
    list_filter = ["direction"]
    list_editable = ["order"]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["full_name", "role_uz", "dept", "is_leadership", "order"]
    list_filter = ["dept", "is_leadership"]
    list_editable = ["is_leadership", "order"]


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ["kind", "number", "issuer_uz", "valid_until", "show_in_hero", "order"]
    list_filter = ["kind", "show_in_hero"]
    list_editable = ["show_in_hero", "order"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title_uz", "published_on", "legal_act", "is_published"]
    list_filter = ["is_published", "published_on"]
    prepopulated_fields = {"slug": ["title_uz"]}
    date_hierarchy = "published_on"


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ["value", "label_uz", "highlight", "order"]
    list_editable = ["highlight", "order"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["created_at", "name", "phone", "direction", "urgency", "status"]
    list_filter = ["status", "urgency", "direction", "language"]
    search_fields = ["name", "phone", "email", "object_type", "note"]
    list_editable = ["status"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "source", "language"]
