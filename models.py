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


class BaseModel(Model):
    class Meta:
        database = db


class Metadata(BaseModel):
    content = CharField()
    kind = CharField(null=True)
    url = BooleanField(null=True)
    url_name = CharField(null=True)


class Item(BaseModel):
    text = TextField()
    created_at = DateTimeField(null=True)
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    language = CharField(max_length=5, null=True)


class ItemMetadata(BaseModel):
    item = ForeignKeyField(Item)
    metadata = ForeignKeyField(Metadata)
