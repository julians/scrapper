#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

BUCKETS = [
    {
        "filename_pattern": re.compile('snippets \d{4}-\d{2}', re.IGNORECASE),
        "id": "snippets",
    },
    {
        "filename_pattern": re.compile('quotes \d{4}-\d{2}', re.IGNORECASE),
        "id": "quotes",
    },
    {
        "filename_pattern": re.compile('poems \d{4}-\d{2}', re.IGNORECASE),
        "id": "poems",
    },
]

PLACES = {
    "WG": [52.396301, 13.032333]
}

TIMEZONES = {
    "CDT": "CST6CDT"
}
