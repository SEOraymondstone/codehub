import logging

from django.contrib import messages
from django.shortcuts import redirect, render

from courses.forms import LeadForm
from courses.models import CourseModule, Lead

from .forms import ContactForm
from .models import (
    Advantage,
    FAQItem,
    PricingPlan,
    StatItem,
    Teacher,
    Testimonial,
)

logger = logging.getLogger(__name__)


def landing(request):
    """Public one-page website: hero, programme, pricing, contacts and forms."""
    modules = CourseModule.objects.filter(is_published=True)
    lead_form = LeadForm(prefix="lead")
    contact_form = ContactForm(prefix="contact")

    if request.method == "POST":
        if "lead_submit" in request.POST:
            lead_form = LeadForm(request.POST, prefix="lead")
            if lead_form.is_valid():
                lead = lead_form.save(commit=False)
                source = request.POST.get("source") or Lead.Source.HERO
                lead.source = source if source in Lead.Source.values else Lead.Source.OTHER
                lead.utm_source = request.GET.get("utm_source", request.POST.get("utm_source", ""))[:120]
                lead.utm_campaign = request.GET.get("utm_campaign", request.POST.get("utm_campaign", ""))[:120]
                lead.save()
                messages.success(
                    request, "Заявка принята! Организатор свяжется с вами в ближайшее время."
                )
                return redirect("pages:landing")
            messages.error(request, "Не удалось отправить заявку. Проверьте поля формы.")

        elif "contact_submit" in request.POST:
            contact_form = ContactForm(request.POST, prefix="contact")
            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, "Сообщение отправлено. Ответим на указанный email.")
                return redirect("pages:landing")
            messages.error(request, "Не удалось отправить сообщение. Проверьте поля формы.")

    context = {
        "modules": modules,
        "lead_form": lead_form,
        "contact_form": contact_form,
        "stats": StatItem.objects.filter(is_published=True),
        "advantages": Advantage.objects.filter(is_published=True),
        "plans": PricingPlan.objects.filter(is_published=True),
        "testimonials": Testimonial.objects.filter(is_published=True),
        "faqs": FAQItem.objects.filter(is_published=True),
        "teachers": Teacher.objects.filter(is_published=True),
    }
    return render(request, "pages/landing.html", context)


def guide(request):
    """Тёмная страница ознакомления: как устроено обучение в CodeHub."""
    return render(request, "pages/guide.html")


def robots_txt(request):
    """robots.txt с указанием карты сайта и закрытых разделов."""
    from django.http import HttpResponse
    from django.urls import reverse

    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /homework/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {sitemap_url}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def privacy(request):
    """Политика конфиденциальности — обязательна для доверия к курсу."""
    return render(request, "pages/privacy.html")


def healthz(request):
    """Lightweight health-check endpoint for the deployment reverse proxy."""
    from django.db import connection
    from django.http import JsonResponse

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # pragma: no cover - defensive
        logger.exception("CodeHub health check failed")
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})
