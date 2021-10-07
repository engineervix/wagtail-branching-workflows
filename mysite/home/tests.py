import pytest
from django.apps import apps
from wagtail.core.models import Page

from mysite.home.apps import HomeConfig


@pytest.mark.django_db
def test_homepage(client):
    """Tests the rendering of the custom homepage."""
    live_pages = Page.objects.live()
    home_page = live_pages.get(title="Home")
    response = client.get(home_page.get_url())
    assert response.status_code == 200
    assert home_page.get_url() == "/"
    assert "home/home_page.html" in [t.name for t in response.templates]
    assert b"Beverly Hills, CA 90210" in response.content


@pytest.mark.django_db
def test_home_app():
    assert HomeConfig.name == "mysite.home"
    assert apps.get_app_config("home").name == "mysite.home"
