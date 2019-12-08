#!/usr/bin/python
# -*- coding: utf-8 -*-

from peewee import (
    Model,
    ForeignKeyField,
    CharField,
    DateTimeField,
    TextField,
    FloatField,
    BooleanField,
)
from config import db
import datetime
import re
from smartquotes import smartyPants


apostrophe_regex = re.compile(r"(\S)'(\S)")
dash_regex = re.compile(r" - ")
typographic_languages = {"de": "de-x-altquot"}


def fix_typography(string_to_format, language):
    formatted_string = dash_regex.sub(r" – ", string_to_format)
    formatted_string = apostrophe_regex.sub(r"\1’\2", formatted_string)
    formatted_string = smartyPants(formatted_string, language=language)
    return formatted_string


class BaseModel(Model):
    class Meta:
        database = db


class Metadata(BaseModel):
    content = CharField()
    kind = CharField(null=True)
    url = BooleanField(null=True)
    url_name = CharField(null=True)


class Item(BaseModel):
    text = TextField(null=True)
    image = CharField(null=True)
    created_at = DateTimeField(null=True)
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    language = CharField(max_length=5, null=True)
    bucket = CharField(max_length=16, null=True)

    def get_typographic_text(self):
        if self.text and len(self.text):
            typographic_language = typographic_languages.get(
                self.language, self.language
            )
            text = fix_typography(self.text, language=typographic_language)
            return text
        return None


class ItemMetadata(BaseModel):
    item = ForeignKeyField(Item)
    metadata = ForeignKeyField(Metadata)
