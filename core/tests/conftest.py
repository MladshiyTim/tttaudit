from pathlib import Path

import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def static_root_dir():
    """WhiteNoise STATIC_ROOT yoʻq deb ogohlantirmasin — papka git-ignored."""
    Path(settings.STATIC_ROOT).mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Bazani bir marta toʻldiradi: tahririy kontent + mijoz faktlari."""
    with django_db_blocker.unblock():
        call_command("seed_content")
        call_command("import_tttaudit")


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()
