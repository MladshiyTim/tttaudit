"""So'rov formasi — React vidjeti shu forma orqali validatsiyadan o'tadi."""
import os

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "direction",
            "object_type",
            "region",
            "area_m2",
            "annual_kwh",
            "estimate_value",
            "urgency",
            "name",
            "phone",
            "email",
            "note",
            "attachment",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # JS o'chiq holatdagi oddiy forma bu maydonni yubormaydi —
        # model defaultiga tayanamiz.
        self.fields["urgency"].required = False

    def clean_urgency(self):
        return self.cleaned_data.get("urgency") or Lead.URGENCY_PLANNED

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        digits = [ch for ch in phone if ch.isdigit()]
        if len(digits) < 9:
            raise forms.ValidationError(_("Telefon raqami toʻliq emas."))
        return phone

    def clean_attachment(self):
        upload = self.cleaned_data.get("attachment")
        if not upload:
            return upload

        max_bytes = settings.LEAD_MAX_UPLOAD_BYTES
        if upload.size > max_bytes:
            raise forms.ValidationError(
                _("Fayl hajmi %(mb)d MB dan oshmasligi kerak.")
                % {"mb": max_bytes // (1024 * 1024)}
            )

        extension = os.path.splitext(upload.name)[1].lower()
        if extension not in settings.LEAD_ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                _("Bu fayl turi qabul qilinmaydi. Ruxsat etilgan: %(list)s")
                % {"list": ", ".join(settings.LEAD_ALLOWED_EXTENSIONS)}
            )
        return upload
