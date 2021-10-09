import random

import factory
import wagtail_factories
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock

from mysite.home.models import HomePage
from mysite.users.models import User

# from factory import fuzzy
# from mysite.base.blocks import HeadingBlock, ImageBlock, BlockQuote


# from django.utils.timezone import now


class HomePageFactory(wagtail_factories.PageFactory):
    """HomePage Factory"""

    class Meta:
        model = HomePage


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating Django User objects"""

    # username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")
    # is_staff = True
    # is_superuser = True

    class Meta:
        model = User


class SimpleDocFactory(wagtail_factories.DocumentFactory):
    """Factory for creating Wagtail Documents"""

    # file = factory.django.FileField(filename=f'{factory.Faker("slug")}.pdf')


# class HeadingBlockFactory(wagtail_factories.StructBlockFactory):
#     heading_text = factory.Faker(
#         "text", max_nb_chars=200
#     ).generate(extra_kwargs={})
#     size = random.choice(['h2', 'h3', 'h4'])

#     class Meta:
#         model = HeadingBlock


# class ImageBlockFactory(wagtail_factories.StructBlockFactory):
#     image = factory.SubFactory(wagtail_factories.ImageChooserBlockFactory)
#     caption = random.choice([factory.Faker("text"), ""])
#     attribution = random.choice([factory.Faker("text", max_nb_chars=200).generate(extra_kwargs={}), ""])

#     class Meta:
#         model = ImageBlock


# class BlockQuoteFactory(wagtail_factories.StructBlockFactory):
#     text = factory.Faker("text")
#     attribute_name = attribution = random.choice([factory.Faker("text", max_nb_chars=200).generate(extra_kwargs={}), ""])

#     class Meta:
#         model = BlockQuote


# class ChoiceBlockFactory(wagtail_factories.blocks.BlockFactory):

#     class Meta:
#         model = blocks.ChoiceBlock


# class TextBlockFactory(wagtail_factories.blocks.BlockFactory):

#     class Meta:
#         model = blocks.TextBlock


# class EmbedBlockFactory(wagtail_factories.blocks.BlockFactory):

#     class Meta:
#         model = EmbedBlock


# class RichTextBlockFactory(wagtail_factories.blocks.BlockFactory):

#     class Meta:
#         model = blocks.RichTextBlock


# class TableBlockFactory(wagtail_factories.blocks.BlockFactory):

#     class Meta:
#         model = TableBlock
