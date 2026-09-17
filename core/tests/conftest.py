from pathlib import Path

import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings


@pytest.fixture(scope="session", autouse=True)
def static_root_dir():
    """WhiteNoise STATIC_ROOT yoʻq deb ogohlantirmasin — papka git-ignored."""
    Path(settings.STATIC_ROOT).mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def media_root(tmp_path_factory):
    """Testlar lokal media/ papkasiga yozmasin: MEDIA_ROOT sessiya uchun vaqtinchalik papka.

    `override_settings` `setting_changed` signalini yuboradi — default_storage joylashuvi yangilanadi.
    """
    root = tmp_path_factory.mktemp("media")
    override = override_settings(MEDIA_ROOT=str(root))
    override.enable()
    yield root
    override.disable()


@pytest.fixture(scope="session")
def django_db_setup(media_root, django_db_setup, django_db_blocker):
    """Bazani bir marta toʻldiradi: tahririy kontent + mijoz faktlari."""
    with django_db_blocker.unblock():
        call_command("seed_content")
        call_command("import_tttaudit")


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()
