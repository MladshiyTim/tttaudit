"""Admin paneldan tahrirlanadigan sayt matnlari (interfeys va vidjetlar) va bosh sahifa slaydlari."""
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import TranslatableMixin, validate_image_size


class SiteText(models.Model):
    """Shablon/vidjet matnining admin qayta yozuvi. Boʻsh maydon — standart tarjima ishlatiladi."""

    KIND_UI = "ui"
    KIND_WIDGET = "widget"
    KIND_CHOICES = [
        (KIND_UI, _("Sahifa matni")),
        (KIND_WIDGET, _("Vidjet matni (forma, kalkulyator)")),
    ]

    kind = models.CharField(_("Turi"), max_length=8, choices=KIND_CHOICES, default=KIND_UI)
    # UI: oʻzbekcha asl matn (gettext msgid); vidjet: i18n.json kaliti
    key = models.TextField(_("Kalit"), unique=True)
    text_uz = models.TextField(_("Oʻzbekcha"), blank=True)
    text_ru = models.TextField(_("Ruscha"), blank=True)
    text_en = models.TextField(_("Inglizcha"), blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "key"]
        verbose_name = _("Sayt matni")
        verbose_name_plural = _("Sayt matnlari")

    def __str__(self):
        return self.key[:80]

    def value(self, lang: str) -> str:
        return getattr(self, f"text_{lang}", "") or ""


@receiver([post_save, post_delete], sender=SiteText)
def _site_text_changed(**kwargs) -> None:
    from .sitetext import bump_version

    bump_version()


class Slide(TranslatableMixin, models.Model):
    """Bosh sahifadagi slayd-shou kadri."""

    image = models.ImageField(
        _("Surat"), upload_to="slides/", validators=[validate_image_size],
        help_text=_("Vertikal 4:5 nisbat, kamida 1280×1600 px, JPG."),
    )
    kicker_uz = models.CharField(_("Yorliq"), max_length=60, help_text=_("Masalan: «Energoaudit»"))
    kicker_ru = models.CharField(max_length=60, blank=True)
    kicker_en = models.CharField(max_length=60, blank=True)
    text_uz = models.CharField(_("Izoh"), max_length=200)
    text_ru = models.CharField(max_length=200, blank=True)
    text_en = models.CharField(max_length=200, blank=True)
    alt_uz = models.CharField(
        _("Surat tavsifi (alt)"), max_length=200, blank=True,
        help_text=_("Koʻzi ojizlar uchun: suratda nima tasvirlangan."),
    )
    alt_ru = models.CharField(max_length=200, blank=True)
    alt_en = models.CharField(max_length=200, blank=True)
    focus_y = models.PositiveSmallIntegerField(
        _("Kadr markazi (vertikal, %)"), default=50, validators=[MaxValueValidator(100)],
        help_text=_("Mobil ekranda surat kesilganda qaysi qism koʻrinsin: 0 — yuqori, 100 — past."),
    )
    is_active = models.BooleanField(_("Koʻrsatilsin"), default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = _("Slayd")
        verbose_name_plural = _("Bosh sahifa slaydlari")

    def __str__(self):
        return f"{self.order}. {self.kicker_uz} — {self.text_uz[:50]}"
