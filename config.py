#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from peewee import SqliteDatabase
import sys
from os import path, environ

env = environ.get("ENVIRONMENT", "development")

IS_PRODUCTION = env == "production"

BUCKETS = [
    {
        "filename_pattern": re.compile("snippets? \d{4}-\d{2}", re.IGNORECASE),
        "id": "snippets",
    },
    {
        "filename_pattern": re.compile("quotes? \d{4}-\d{2}", re.IGNORECASE),
        "id": "quotes",
    },
    {
        "filename_pattern": re.compile("poems? \d{4}-\d{2}", re.IGNORECASE),
        "id": "poems",
    },
    {
        "filename_pattern": re.compile("facts? \d{4}-\d{2}", re.IGNORECASE),
        "id": "facts",
    },
    {
        "filename_pattern": re.compile("design notes? \d{4}-\d{2}", re.IGNORECASE),
        "id": "design-notes",
    },
    {"filename_pattern": re.compile("arts? \d{4}-\d{2}", re.IGNORECASE), "id": "arts"},
    {
        "filename_pattern": re.compile("photos? \d{4}-\d{2}", re.IGNORECASE),
        "id": "photos",
        "aliases": ["fotos", "schöne bilder"],
    },
    {
        "filename_pattern": re.compile("comics? \d{4}-\d{2}", re.IGNORECASE),
        "id": "comics",
    },
    {
        "filename_pattern": re.compile("art? \d{4}-\d{2}", re.IGNORECASE),
        "id": "arts",
        "aliases": ["art"],
    },
]

PLACES = {"WG": [52.396301, 13.032333]}

TIMEZONES = {"CDT": "CST6CDT", "MESZ": "CEST", "MEZ": "CET"}

db = SqliteDatabase("scraps.db")

RELATIVE_STATIC_FILE_PATH = "static-scrapper" if IS_PRODUCTION else "static"
STATIC_FILE_PATH = path.join(sys.path[0], RELATIVE_STATIC_FILE_PATH)
