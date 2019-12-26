#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict
import arrow
from urllib.parse import urlparse
from langdetect import detect
import hashlib

from config import PLACES as PLACES_CONF
from config import TIMEZONES as TIMEZONES_CONF


# class Item:
#     def __init__(self, text, metadata=None, datetime=None, place=None):
#         self.text = text
#         self.datetime = datetime
#         self.place = place
#         self.metadata = metadata


PREDEFINED_PLACES = [key for key, value in PLACES_CONF.items()]
PREDEFINED_TIMEZONES = [key for key, value in TIMEZONES_CONF.items()]
datetime_strings = defaultdict(int)

date_and_place_regex = re.compile(
    r"""---\n*?
Saved on.*?((\d{2}\.\d{2}\.\d{4} \d{2}\:\d{2}.*?)
at (.*$))""",
    re.IGNORECASE | re.MULTILINE,
)
timezone_regex = re.compile(r"\((\S+?)\)")
metadata_regex = re.compile(r"(?:\n\- .+?){1,}$", re.IGNORECASE | re.MULTILINE)
metadata_item_regex = re.compile(r"^(\w+?):\s")
old_twitter_metadata_regex = re.compile(r"^(@\w+):")

is_tag_line_regex = re.compile(r"^#\w+")
match_tags_regex = re.compile(r"#(\w+)\b")

image_item_regex = re.compile(r"(?:\- image\:\s*?)(.{1,}?)$")


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
        datetime = arrow.get(datetime_string, "DD.MM.YYYY HH:mm:ss")
    except arrow.parser.ParserError:
        datetime = arrow.get(datetime_string, "DD.MM.YYYY HH:mm")

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
        returnValue = {"coordinates": tuple([float(coord) for coord in split_place])}
    except ValueError:
        return None

    if returnValue["coordinates"][0] == 0 and returnValue["coordinates"][0] == 0:
        return None

    return returnValue


def parse_metadata(original_string):
    match = metadata_regex.search(original_string)
    if not match:
        # special case for earliest saved tweets
        old_twitter_metadata = old_twitter_metadata_regex.search(original_string)
        if old_twitter_metadata:
            metadata = {
                "metadata": [
                    {
                        "kind": "source",
                        "content": "{}".format(old_twitter_metadata.group(1)),
                    }
                ],
                "modified": original_string.replace(old_twitter_metadata.group(0), ""),
            }
            return metadata

        return None

    metadata_string = match.group(0)
    modified_string = original_string.replace(metadata_string, "")

    metadata = metadata_string.splitlines()
    metadata = [x.strip("- ") for x in metadata if len(x)]
    metadata = organise_metadata(metadata)

    return {"metadata": metadata, "modified": modified_string}


def check_and_handle_url(metadata_item):
    parsed_url = urlparse(metadata_item["content"])

    if parsed_url.netloc and parsed_url.scheme:
        metadata_item["url"] = True

        if parsed_url.netloc == "twitter.com":
            metadata_item["url_name"] = "@{}".format(parsed_url.path.split("/")[1])
        else:
            metadata_item["url_name"] = parsed_url.netloc

    return metadata_item


def organise_metadata(metadata):
    organised_metadata = []
    has_source = False

    for _, item in enumerate(metadata):
        metadata_item = {}
        match = metadata_item_regex.search(item)
        if not match:
            is_tag_line = is_tag_line_regex.search(item)
            if is_tag_line:
                tags = match_tags_regex.findall(item)
                for tag in tags:
                    organised_metadata.append({"content": tag, "kind": "tag"})
                continue
            else:
                metadata_item["content"] = item

                if not has_source:
                    metadata_item["kind"] = "source"
                    has_source = True

                metadata_item = check_and_handle_url(metadata_item)

                organised_metadata.append(metadata_item)
                continue

        split_metadata = item.split(": ", 1)
        metadata_item = {
            "kind": split_metadata[0].strip(),
            "content": split_metadata[1].strip(),
        }
        metadata_item = check_and_handle_url(metadata_item)
        organised_metadata.append(metadata_item)

    return organised_metadata


def extract_image(original_string):
    match = image_item_regex.search(original_string)
    if match:
        image_url = match.group(1).strip()
        modified_string = original_string.replace(match.group(0), "").strip()
        return {"image_url": image_url, "modified": modified_string}

    return None


def get_id_for_item(item):
    hashable_content = ""
    if item["image"]:
        hashable_content = item["image"]
    elif item["text"]:
        hashable_content = item["text"]

    hashable_content = "{}{}".format(item["datetime"].isoformat(), hashable_content)

    return hashlib.sha1(hashable_content.encode("utf-8")).hexdigest()


def create_item(
    datetime, metadata=None, text=None, place=None, language=None, image=None
):
    item_arguments = {
        "text": text,
        "datetime": datetime,
        "place": place,
        "metadata": metadata,
        "language": language,
        "image": image,
    }

    hashid = get_id_for_item(item_arguments)
    item_arguments["hashid"] = hashid

    return item_arguments


def create_item_from_string(item_string):
    date_and_place = extract_date_and_place(item_string)
    if not date_and_place:
        return None

    metadata = parse_metadata(date_and_place["modified"])

    if metadata:
        text = metadata["modified"].strip()
        metadata = metadata["metadata"]
    else:
        text = date_and_place["modified"].strip()

    language = None
    image = extract_image(text)
    if image:
        text = image["modified"]
        image = image["image_url"]

    if text and len(text):
        language = detect(text)
    else:
        text = None

    item_arguments = {
        "text": text,
        "datetime": date_and_place["datetime"],
        "place": date_and_place["place"],
        "metadata": metadata,
        "language": language,
        "image": image,
    }

    hashid = get_id_for_item(item_arguments)
    item_arguments["hashid"] = hashid

    return item_arguments
