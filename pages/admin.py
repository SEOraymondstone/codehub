from django.contrib import admin

from .models import (
    Advantage,
    ContactMessage,
    FAQItem,
    PricingPlan,
    SiteSettings,
    StatItem,
    Teacher,
    Testimonial,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Синглтон: тексты и контакты сайта, правятся без кода."""

    fieldsets = (
        ("Основное", {"fields": ("name", "tagline", "price_from")}),
        ("Первый экран", {"fields": ("hero_title", "hero_accent", "hero_subtitle")}),
        ("Контакты", {"fields": ("phone", "phone_secondary", "email")}),
        ("Соцсети", {"fields": ("telegram", "whatsapp", "instagram", "youtube", "github")}),
        ("Служебное", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        from django.shortcuts import redirect

        return redirect("admin:pages_sitesettings_change", obj.pk)


class OrderedPublishedAdmin(admin.ModelAdmin):
    list_filter = ("is_published",)
    list_editable = ("order", "is_published")
    ordering = ("order", "id")
    save_on_top = True


@admin.register(StatItem)
class StatItemAdmin(OrderedPublishedAdmin):
    list_display = ("value", "label", "order", "is_published")
    search_fields = ("value", "label")


@admin.register(Advantage)
class AdvantageAdmin(OrderedPublishedAdmin):
    list_display = ("title", "icon", "order", "is_published")
    search_fields = ("title", "text")


@admin.register(PricingPlan)
class PricingPlanAdmin(OrderedPublishedAdmin):
    list_display = ("name", "price", "period", "is_featured", "order", "is_published")
    list_editable = ("order", "is_published", "is_featured")
    search_fields = ("name", "price", "features")


@admin.register(Teacher)
class TeacherAdmin(OrderedPublishedAdmin):
    list_display = ("name", "title", "order", "is_published")
    search_fields = ("name", "title", "bio")


@admin.register(Testimonial)
class TestimonialAdmin(OrderedPublishedAdmin):
    list_display = ("author", "role", "order", "is_published")
    search_fields = ("author", "role", "text")


@admin.register(FAQItem)
class FAQItemAdmin(OrderedPublishedAdmin):
    list_display = ("question", "order", "is_published")
    search_fields = ("question", "answer")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_processed", "created_at")
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("is_processed",)
    date_hierarchy = "created_at"
