"""Mijoz faktlarini data/tttaudit/*.json dan bazaga yuklaydi.

    python manage.py import_tttaudit           # boʻsh jadvallarni toʻldiradi
    python manage.py import_tttaudit --force   # jadvallarni fayldagi holatga qaytaradi

Oldin `seed_content` ishga tushirilgan boʻlishi shart (yoʻnalishlar kerak).

Manba fayllar:
    facts.json     kompaniya rekvizitlari, hujjatlar (skan bilan), asboblar, raqamlar
    staff.json     39 mutaxassis (byulleten), suratlar img/staff/
    projects.json  143 loyiha (byulleten), buyurtmachi nomi bilan
    clients.json   eski saytdagi mijozlar roʻyxati (soha bilan)

Egalik qilinadigan jadvallar: Branch, Credential, Instrument, Stat, TeamMember,
Project, Client. --force ularni qayta yaratadi — admin paneldagi tahrirlar yoʻqoladi.
SiteSettings da faqat rekvizit maydonlari yangilanadi (matnlar seed_content'da).
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Branch, Client, Credential, Direction, Instrument, Project, SiteSettings, Stat, TeamMember,
)

DATA_DIR = Path(settings.BASE_DIR) / "data" / "tttaudit"
DEPT_TO_DIRECTION = {"energy": "energoaudit", "construction": "olchov-auditi"}
LEADERSHIP_WORDS = ("директор", "начальник", "руководител")


def load_json(name: str) -> dict:
    path = DATA_DIR / name
    if not path.exists():
        raise CommandError(f"{path} topilmadi")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_date(value: str | None) -> dt.date | None:
    return dt.date.fromisoformat(value) if value else None


def attach(field, rel_path: str | None) -> None:
    """data/tttaudit/<rel_path> faylini ImageField/FileField ga nusxalaydi."""
    if not rel_path:
        return
    source = DATA_DIR / rel_path
    if not source.exists():
        raise CommandError(f"Fayl topilmadi: {source}")
    with source.open("rb") as handle:
        field.save(source.name, File(handle), save=False)


class Command(BaseCommand):
    help = "data/tttaudit/*.json dagi mijoz faktlarini bazaga yuklaydi."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Jadvallarni qayta yaratish.")

    def handle(self, *args, **options):
        facts = load_json("facts.json")
        staff = load_json("staff.json")
        projects = load_json("projects.json")
        clients = load_json("clients.json")
        force = options["force"]

        directions = {d.slug: d for d in Direction.objects.all()}
        missing = set(DEPT_TO_DIRECTION.values()) - set(directions)
        if missing:
            raise CommandError(f"Yonalish topilmadi: {sorted(missing)}. Avval: python manage.py seed_content")

        with transaction.atomic():
            self._site(facts["company"])
            self._table(Branch, force, lambda: self._branches(facts["company"]))
            self._table(Credential, force, lambda: self._credentials(facts["credentials"]))
            self._table(Instrument, force, lambda: self._instruments(facts["instruments"], directions))
            self._table(Stat, force, lambda: self._stats(facts["stats"]))
            self._table(TeamMember, force, lambda: self._team(staff["staff"]))
            self._table(Project, force, lambda: self._projects(projects["projects"], directions))
            self._table(Client, force, lambda: self._clients(clients))

        # Konsol xabari ASCII: Windows konsoli oʻ/gʻ ni chiqara olmaydi
        self.stdout.write(self.style.SUCCESS(
            f"Yuklandi: {Branch.objects.count()} ofis / {Credential.objects.count()} hujjat / "
            f"{Instrument.objects.count()} asbob / {Stat.objects.count()} raqam / "
            f"{TeamMember.objects.count()} mutaxassis / {Project.objects.count()} loyiha / "
            f"{Client.objects.count()} mijoz"
        ))

    def _table(self, model, force: bool, fill) -> None:
        if model.objects.exists() and not force:
            self.stdout.write(f"{model.__name__}: malumot bor - otkazib yuborildi (--force).")
            return
        for obj in model.objects.all():
            for field in obj._meta.fields:
                if field.get_internal_type() in ("FileField", "ImageField"):
                    getattr(obj, field.name).delete(save=False)
        model.objects.all().delete()
        fill()

    def _site(self, company: dict) -> None:
        site = SiteSettings.load()
        site.brand_name = "TTT AUDIT"
        site.org_name_uz = company["legal_name_uz"]
        site.org_name_ru = company["legal_name_ru"]
        site.org_name_en = company["legal_name_en"]
        site.tin = company["tin"]
        site.founded_year = company["founded_year"]
        site.experience_years = company["experience_years"]
        site.staff_total = company["staff_total"]
        site.staff_energy = company["staff_energy"]
        site.staff_supervision = company["staff_supervision"]
        site.phone = company["phone"]
        site.phone_second = company["phone_second"]
        site.email = company["email"]
        site.director_uz = company["director"]
        site.director_ru = company["director_ru"]
        site.director_en = company["director"]
        site.map_lat = company["map_lat"]
        site.map_lng = company["map_lng"]
        for lang in ("uz", "ru", "en"):
            setattr(site, f"address_{lang}", company[f"address_{lang}"])
            setattr(site, f"office_tashkent_{lang}",
                    company.get(f"office_tashkent_{lang}") or company["office_tashkent_uz"])
        site.report_turnaround_days = None
        site.work_hours_uz = site.work_hours_ru = site.work_hours_en = ""
        site.save()

    def _branches(self, company: dict) -> None:
        Branch.objects.bulk_create([
            Branch(city_uz="Fargʻona", city_ru="Фергана", city_en="Fergana",
                   address_uz=company["address_uz"], address_ru=company["address_ru"],
                   address_en=company["address_en"], head=company["director"],
                   phone=company["phone"], is_head_office=True, order=0),
            Branch(city_uz="Toshkent", city_ru="Ташкент", city_en="Tashkent",
                   address_uz=company["office_tashkent_uz"], address_ru=company["office_tashkent_ru"],
                   address_en=company.get("office_tashkent_en") or company["office_tashkent_uz"],
                   head="", phone=company["phone_second"], is_head_office=False, order=1),
        ])

    def _credentials(self, credentials: list[dict]) -> None:
        valid = {key for key, _ in Credential.KIND_CHOICES}
        for order, c in enumerate(c for c in credentials if c.get("show")):
            if c["kind"] not in valid:
                raise CommandError(f"facts.json: nomalum hujjat turi {c['kind']!r}, ruxsat: {sorted(valid)}")
            obj = Credential(
                kind=c["kind"], number=c["number"],
                issuer_uz=c["issuer_uz"], issuer_ru=c["issuer_ru"], issuer_en=c["issuer_en"],
                scope_uz=c["scope_uz"], scope_ru=c["scope_ru"], scope_en=c["scope_en"],
                issued_on=parse_date(c.get("issued_on")), valid_until=parse_date(c.get("valid_until")),
                show_in_hero=order < 3, order=order,
            )
            attach(obj.scan, c.get("scan"))
            obj.save()

    def _instruments(self, instruments: list[dict], directions: dict) -> None:
        construction = directions["olchov-auditi"]
        Instrument.objects.bulk_create([
            Instrument(
                name_uz=i["name_uz"], name_ru=i.get("name_ru", ""), name_en=i.get("name_en", ""),
                serial=i.get("serial", ""), certificate_no=i.get("cert", ""),
                verified_on=parse_date(i.get("verified_on")), valid_until=parse_date(i.get("valid_until")),
                range_uz=i.get("range_uz", ""), direction=construction, order=order,
            )
            for order, i in enumerate(instruments)
        ])

    def _stats(self, stats: list[dict]) -> None:
        Stat.objects.bulk_create([
            Stat(value=s["value"], label_uz=s["label_uz"], label_ru=s["label_ru"],
                 label_en=s["label_en"], order=order)
            for order, s in enumerate(stats)
        ])

    def _team(self, staff: list[dict]) -> None:
        for order, row in enumerate(staff):
            role_ru = (row.get("role_ru") or "").lower()
            obj = TeamMember(
                full_name=row["name_uz"] or row["name_ru"], full_name_ru=row["name_ru"],
                role_uz=row["role_uz"], role_ru=row["role_ru"], role_en=row["role_en"],
                certificates_uz=row.get("cert_uz", ""), dept=row["dept"],
                is_leadership=any(word in role_ru for word in LEADERSHIP_WORDS), order=order,
            )
            if row.get("photo"):
                attach(obj.photo, row["photo"])
            obj.save()

    def _projects(self, projects: list[dict], directions: dict) -> None:
        rows = []
        for index, p in enumerate(projects, start=1):
            rows.append(Project(
                slug=f"{p['dept']}-{index:03d}", direction=directions[DEPT_TO_DIRECTION[p["dept"]]],
                order=index, year=p.get("year"), client=p.get("client", ""),
                title_uz=p["title_uz"][:200], title_ru=p["title_ru"][:200], title_en="",
            ))
        Project.objects.bulk_create(rows)

    def _clients(self, data: dict) -> None:
        valid = {key for key, _ in Client.SECTOR_CHOICES}
        unknown = {c["sector"] for c in data["clients"]} - valid
        if unknown:
            raise CommandError(f"clients.json da nomalum soha: {sorted(unknown)}")
        Client.objects.bulk_create([
            Client(name_uz=c["name_uz"], name_ru=c.get("name_ru", ""), name_en=c.get("name_en", ""),
                   sector=c["sector"], featured=c.get("featured", False), order=order)
            for order, c in enumerate(data["clients"])
        ])
