"""Talab tekshiruvi — obyektga qaysi majburiyat tegishli ekanini aniqlaydi.

Bu saytning asosiy foydali asbobi. Mijoz uch-to'rt savolga javob beradi va
o'ziga qaysi talab tegishli ekanini, muddatini va qanday hujjat olishini
ko'radi. Shablon saytlarda bunday narsa bo'lmaydi — u soha qoidalarini
bilishni talab qiladi.

Qoidalar bitta joyda: server ham, React vidjeti ham shu manbadan ishlaydi.

DIQQAT: chegaralar va sanalar amaldagi me'yoriy hujjatdan tasdiqlanishi
shart. Quyidagilar tadqiqot asosidagi ishchi qiymatlar.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from django.utils.translation import gettext_lazy as _

# --- chegaralar --------------------------------------------------------------
PASSPORT_AREA_M2 = 200          # energopasport majburiy bo'ladigan foydali maydon
REGISTRY_KWH = 4_000_000        # davlat energetika reestri: yillik elektr
REGISTRY_GAS_M3 = 375_000       # davlat energetika reestri: yillik tabiiy gaz
PERIODIC_YEARS = 5              # davriy energoaudit oralig'i
MEASUREMENT_FEE_CAP = 0.003     # nazorat o'lchovi xizmat haqi chegarasi (0,3%)

OBJECT_KINDS = ["building", "industrial", "construction"]
FUNDING_KINDS = ["budget", "credit", "own"]


@dataclass
class Requirement:
    key: str
    title: str
    basis: str                    # me'yoriy hujjat raqami
    deadline: str
    note: str
    service_slug: str = ""
    direction_slug: str = ""
    severity: str = "required"    # required | likely | optional

    def as_dict(self):
        return {
            "key": self.key,
            "title": str(self.title),
            "basis": str(self.basis),
            "deadline": str(self.deadline),
            "note": str(self.note),
            "service_slug": self.service_slug,
            "direction_slug": self.direction_slug,
            "severity": self.severity,
        }


@dataclass
class Result:
    requirements: List[Requirement] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    specific_kwh: Optional[float] = None
    energy_category: Optional[str] = None
    estimated_fee: Optional[str] = None

    def as_dict(self):
        return {
            "requirements": [r.as_dict() for r in self.requirements],
            "notes": [str(n) for n in self.notes],
            "specific_kwh": self.specific_kwh,
            "energy_category": self.energy_category,
            "estimated_fee": self.estimated_fee,
        }


def _num(value):
    try:
        return float(str(value).replace(" ", "").replace(",", ".")) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def evaluate(object_kind="", area_m2=None, annual_kwh=None, annual_gas_m3=None,
             estimate_value=None, funding="", has_dispute=False) -> Result:
    """Kirish javoblariga qarab tegishli talablarni qaytaradi."""
    from . import energy

    result = Result()
    area = _num(area_m2)
    kwh = _num(annual_kwh)
    gas = _num(annual_gas_m3)
    estimate = _num(estimate_value)

    # ---------------------------------------------------------- energoaudit
    in_registry = (kwh is not None and kwh > REGISTRY_KWH) or (
        gas is not None and gas > REGISTRY_GAS_M3
    )
    if in_registry:
        result.requirements.append(Requirement(
            key="mandatory_energy_audit",
            title=_("Majburiy davriy energoaudit"),
            basis="ЗРУ-940 · VM № 690",
            deadline=_("Besh yilda kamida bir marta"),
            note=_(
                "Yillik isteʼmol boʻyicha obyekt Davlat energetika reestri "
                "mezonlaridan oshadi. Davriy audit majburiy, muddat oxirgi "
                "audit sanasidan hisoblanadi."
            ),
            service_slug="majburiy", direction_slug="energoaudit",
        ))
    elif kwh is not None or gas is not None:
        result.notes.append(_(
            "Isteʼmol koʻrsatkichlari reestr mezonidan past. Majburiy audit "
            "talab qilinmasligi mumkin, lekin reestrdagi holatni rasmiy "
            "tekshirish kerak."
        ))

    if area is not None and area >= PASSPORT_AREA_M2:
        result.requirements.append(Requirement(
            key="energy_passport",
            title=_("Bino energopasporti va A–G toifasi"),
            basis="ЗРУ-940",
            deadline=_("Foydalanishga topshirishdan oldin yoki audit natijasida"),
            note=_(
                "Foydali maydon chegaradan katta — binoga energosamaradorlik "
                "toifasi belgilanadi va energopasport rasmiylashtiriladi."
            ),
            service_slug="energopasport", direction_slug="energoaudit",
        ))

    if area and kwh:
        specific = energy.specific_consumption(kwh, area)
        if specific is not None:
            result.specific_kwh = round(specific, 1)
            result.energy_category = energy.category_for(specific)

    # ------------------------------------------------------ nazorat oʻlchovi
    if object_kind == "construction":
        if funding == "budget":
            fee = f"{estimate * MEASUREMENT_FEE_CAP:,.0f}".replace(",", " ") if estimate else ""
            result.requirements.append(Requirement(
                key="control_measurement",
                title=_("Nazorat oʻlchovi tartibga solingan"),
                basis=_("Byudjet obyektlarida oʻlchov tartibi"),
                deadline=_("Hisob-kitobdan oldin"),
                note=_(
                    "Byudjet mablagʻlari hisobiga moliyalashtiriladigan obyektda "
                    "oʻlchovni litsenziya va akkreditatsiyaga ega tashkilot "
                    "oʻtkazadi. Xizmat haqi qurilish qiymatining 0,3% dan oshmaydi."
                ),
                service_slug="nazorat-olchovi", direction_slug="olchov-auditi",
            ))
            if fee:
                result.estimated_fee = fee
        elif funding == "credit":
            result.requirements.append(Requirement(
                key="bank_measurement",
                title=_("Transh oldidan hajm tekshiruvi"),
                basis=_("Bank talabi"),
                deadline=_("Har bir transhdan oldin"),
                note=_(
                    "Kredit mablagʻi hisobiga qurilishda bank odatda bajarilgan "
                    "hajmning mustaqil tasdigʻini talab qiladi."
                ),
                service_slug="nazorat-olchovi", direction_slug="olchov-auditi",
                severity="likely",
            ))
        else:
            result.requirements.append(Requirement(
                key="voluntary_measurement",
                title=_("Ixtiyoriy nazorat oʻlchovi"),
                basis=_("Shartnoma asosida"),
                deadline=_("Dalolatnomani imzolashdan oldin"),
                note=_(
                    "Majburiy emas, lekin f-2 dalolatnomasiga imzo qoʻyishdan "
                    "oldin hajmni tasdiqlash — eng arzon nazorat."
                ),
                service_slug="nazorat-olchovi", direction_slug="olchov-auditi",
                severity="optional",
            ))

    if has_dispute:
        result.requirements.append(Requirement(
            key="dispute_opinion",
            title=_("Nizoda mustaqil ekspert xulosasi"),
            basis=_("Sud yoki tomonlar talabi"),
            deadline=_("Nizo koʻrib chiqilgunga qadar"),
            note=_(
                "Xulosa dalil kuchiga ega boʻlishi uchun oʻlchov tomonlar "
                "ishtirokida va bayonnoma bilan rasmiylashtiriladi."
            ),
            service_slug="nizo", direction_slug="olchov-auditi",
        ))

    if not result.requirements:
        result.notes.append(_(
            "Kiritilgan maʼlumot boʻyicha aniq majburiyat koʻrinmadi. "
            "Obyekt tafsilotlarini yuboring — muhandis rasmiy javob beradi."
        ))

    return result
