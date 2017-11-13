#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import hashlib
import re
import arrow
from collections import defaultdict

from config import BUCKETS as BUCKET_CONF
from config import PLACES as PLACES_CONF
from config import TIMEZONES as TIMEZONES_CONF

PREDEFINED_PLACES = [key for key, value in PLACES_CONF.items()]
PREDEFINED_TIMEZONES = [key for key, value in TIMEZONES_CONF.items()]
datetime_strings = defaultdict(int)


date_and_place_regex = re.compile("""---
Saved on.*?((\d{2}\.\d{2}\.\d{4} \d{2}\:\d{2}.*?)
at (.*$))""", re.IGNORECASE | re.MULTILINE)
timezone_regex = re.compile("\((\S+?)\)")
metadata_regex = re.compile("""---(\n\- .+?)""", re.IGNORECASE | re.MULTILINE)


def match_to_bucket(filepath):
    for bucket in BUCKET_CONF:
        if bucket["filename_pattern"].search(os.path.basename(filepath)):
            return bucket["id"]
            break
    return False


def get_id_for_item(item):
    hashlib.sha1(item["date"]).hexdigest()[:12]


def split_file_into_chunks(filepath):
    with open(filepath, "r") as input_file:
         content = input_file.read()
         return content.split("------")


def get_files_by_bucket(directory_name):
    buckets = {bucket["id"]: {"id": bucket["id"], "filepaths": []} for bucket in BUCKET_CONF}
    for filepath in glob.iglob(os.path.join(directory_name, '**/*.txt'), recursive=True):
        bucket = match_to_bucket(filepath)
        if bucket:
            buckets[bucket]["filepaths"].append(filepath)

    return buckets


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
        "original_chunk": original_chunk,
        "modified_chunk": modified_chunk,
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


def parse_chunks_into_items(chunks):
    modified_chunks = []
    for chunk in chunks:
        date_and_place = extract_date_and_place(chunk)
        if date_and_place:
            modified_chunks.append({
                "datetime": date_and_place["datetime"],
                "place": date_and_place["place"],
                "text": date_and_place["modified_chunk"],
            })
    return modified_chunks


def import_files(directory_name):
    buckets = get_files_by_bucket(directory_name)
    for bucket_id, bucket in buckets.items():
        bucket["items"] = []
        for filepath in bucket["filepaths"]:
            chunks = split_file_into_chunks(filepath)
            items = parse_chunks_into_items(chunks)
            bucket["items"] += items

    return buckets
