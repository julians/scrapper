#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from peewee import SqliteDatabase

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
    },
]

PLACES = {"WG": [52.396301, 13.032333]}

TIMEZONES = {"CDT": "CST6CDT", "MESZ": "CEST", "MEZ": "CET"}

db = SqliteDatabase("scraps.db")
