#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import arrow

from config import PLACES as PLACES_CONF
from config import TIMEZONES as TIMEZONES_CONF

class Item:
    def __init__(self, text, metadata=None, datetime=None, place=None):
        self.text = text
        self.datetime = datetime
        self.place = place
        self.metadata = metadata


PREDEFINED_PLACES = [key for key, value in PLACES_CONF.items()]
PREDEFINED_TIMEZONES = [key for key, value in TIMEZONES_CONF.items()]
datetime_strings = defaultdict(int)

date_and_place_regex = re.compile("""---
Saved on.*?((\d{2}\.\d{2}\.\d{4} \d{2}\:\d{2}.*?)
at (.*$))""", re.IGNORECASE | re.MULTILINE)
timezone_regex = re.compile("\((\S+?)\)")
metadata_regex = re.compile("(?:\n\- .+?){1,}$", re.IGNORECASE | re.MULTILINE)


def extract_date_and_place(original_chunk):
    date_and_place_match = date_and_place_regex.search(original_chunk)
    if not date_and_place_match:
        return None

    datetime_string = date_and_place_match.group(2)
    place_string = date_and_place_match.group(3)

    place = parse_place(place_string)
    datetime = parse_datetime(datetime_string)

    modified_chunk = original_chunk.replace(date_and_place_match.group(0), "").strip()

    return {
        "datetime": datetime,
        "place": place,
        "original": original_chunk,
        "modified": modified_chunk,
    }


def parse_datetime(datetime_string):
    timezone_match = timezone_regex.search(datetime_string)
    if timezone_match:
        timezone_string = timezone_match.group(1).strip()
        datetime_string = datetime_string.replace(timezone_match.group(0), "").strip()
        if timezone_string in PREDEFINED_TIMEZONES:
            timezone_string = TIMEZONES_CONF[timezone_string]

    try:
        datetime = arrow.get(datetime_string, 'DD.MM.YYYY HH:mm:ss')
    except arrow.parser.ParserError:
        datetime = arrow.get(datetime_string, 'DD.MM.YYYY HH:mm')
    datetime = datetime.replace(tzinfo=timezone_string)

    return datetime.datetime


def parse_place(place_string):
    trimmed_place_string = place_string.strip()

    if trimmed_place_string in PREDEFINED_PLACES:
        return {
            "coordinates": PLACES_CONF[trimmed_place_string],
            "name": trimmed_place_string,
        }

    split_place = place_string.split(",")
    try:
        return {
            "coordinates": [float(coord) for coord in split_place]
        }
    except ValueError:
        return None


def parse_metadata(original_string):
    match = metadata_regex.search(original_string)
    if not match:
        return None

    metadata_string = match.group(0)
    modified_string = original_string.replace(metadata_string, "")

    return {
        "metadata": metadata_string,
        "modified": modified_string,
    }


def create_item_from_string(item_string):
    date_and_place = extract_date_and_place(item_string)
    if not date_and_place:
        return None

    metadata = parse_metadata(date_and_place["modified"])
    if not metadata:
        return None

    item_arguments = {
        "text": metadata["modified"],
        "datetime": date_and_place["datetime"],
        "place": date_and_place["place"],
        "metadata": metadata["metadata"],
    }
    return Item(**item_arguments)
