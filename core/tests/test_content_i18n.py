"""Tahririy kontent va mijoz maʼlumotlarining ru/en koʻrinishi."""
import re

import pytest
from django.utils import translation
from django.utils.translation import gettext

from core.management.commands import seed_content
from core.models import Credential, Instrument, TeamMember


def _missing_translations(obj, path=""):
    """seed_content maʼlumotida uz qiymati bor, lekin ru/en boʻsh yoki uz ga teng joylar."""
    problems = []
    if isinstance(obj, dict):
        if set(obj) == {"uz", "ru", "en"}:
            return [path] if obj["ru"] == obj["uz"] or obj["en"] == obj["uz"] else []
        for key, value in obj.items():
            if key.endswith("_uz") and isinstance(value, str) and value:
                base = key[:-3]
                problems += [f"{path}.{base}_{lang}" for lang in ("ru", "en") if not obj.get(f"{base}_{lang}")]
            problems += _missing_translations(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            problems += _missing_translations(value, f"{path}[{index}]")
    return problems


def test_seed_content_has_ru_and_en_for_every_editorial_text():
    for name in ("DIRECTIONS", "SERVICES", "ACTS", "POSTS", "SITE"):
        assert _missing_translations(getattr(seed_content, name), name) == []


@pytest.mark.django_db
def test_en_post_and_service_are_english(client):
    post = client.get("/en/yangiliklar/energoaudit-kimga-majburiy/").content.decode()
    title = re.search(r"<title>([^<]+)</title>", post).group(1)
    assert title.startswith("Who is required to carry out an energy audit"), title

    service = client.get("/en/xizmatlar/energoaudit/majburiy/").content.decode()
    assert "Under ZRU-940, a periodic energy audit is mandatory" in service
    assert "besh yilda kamida bir marta" not in service


@pytest.mark.django_db
def test_zru_940_is_latin_on_en_and_formal_on_ru(client):
    en_home = client.get("/en/").content.decode()
    assert "<b>Basis:</b> ZRU-940 «" in en_home
    assert "ЗРУ-940" not in en_home

    params = {"object_kind": "industrial", "annual_kwh": "5000000"}
    en = client.get("/en/api/compliance/", params).json()["requirements"][0]["basis"]
    ru = client.get("/ru/api/compliance/", params).json()["requirements"][0]["basis"]
    uz = client.get("/uz/api/compliance/", params).json()["requirements"][0]["basis"]
    assert en == "ZRU-940 · CM Resolution No. 690"
    assert ru == "Закон № ЗРУ-940 · Постановление КМ № 690"
    assert uz == "ЗРУ-940 · VM № 690"


@pytest.mark.django_db
def test_instruments_translated_on_en_and_ru(client):
    en = client.get("/en/tashkilot/asboblar/").content.decode()
    assert "Laser distance meter SNOWAY SW-M100" in en and "up to 50 m, error ±2 mm" in en
    assert "Electronic micrometer MKU" in en and "0–25 mm, error ±0.001 mm" in en
    assert "Temperature and humidity data logger Enkor 4127" in en
    assert "masofaoʻlchagich" not in en and "xatolik" not in en
    ru = client.get("/ru/tashkilot/asboblar/").content.decode()
    assert "Лазерный дальномер SW-50G" in ru and "до 50 м, погрешность ±2 мм" in ru
    assert Instrument.objects.filter(name_en="").count() == 0


@pytest.mark.django_db
def test_registry_credential_number_and_ranking():
    registry = Credential.objects.get(kind="registry")
    assert registry.number == "VM qarori № 673"
    assert registry.scope_uz.endswith("(10-oʻrin, reyting 14.5)")
    assert registry.scope_ru.endswith("(10-е место, рейтинг 14,5)")
    assert registry.scope_en.endswith("(10th place, rating 14.5)")


@pytest.mark.django_db
def test_staff_without_latin_name_get_transliteration(client):
    assert not TeamMember.objects.filter(full_name__regex=r"[А-Яа-яЁёЎўҚқҒғҲҳ]").exists()
    en = client.get("/en/tashkilot/mutaxassislar/").content.decode()
    assert "Ergashev Shavkat Rashitovich" in en and "Zuhriddinov Temurjon Doniyorjon oʻgʻli" in en
    assert "ЭРГАШЕВ" not in en
    ru = client.get("/ru/tashkilot/mutaxassislar/").content.decode()
    assert "ЭРГАШЕВ ШАВКАТ РАШИТОВИЧ" in ru


@pytest.mark.django_db
def test_translation_nits(client):
    with translation.override("en"):
        assert gettext("Metrologik tekshiruv") == "Metrological verification"
    ru = client.get("/ru/api/compliance/", {"object_kind": "construction", "funding": "budget"}).json()
    assert ru["requirements"][0]["basis"] == "Порядок контрольного обмера на бюджетных объектах"
