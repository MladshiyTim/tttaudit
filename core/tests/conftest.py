import pytest
from django.core.cache import cache
from django.core.management import call_command


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
