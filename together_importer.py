import os
import glob
from urlparser import parse_urls_from_string
import json
from urllib.parse import unquote, urlparse
from collections import defaultdict
import unicodedata
import datetime
from PIL import Image

from hash_file import get_hash_for_file
from config import BUCKETS as BUCKET_CONF, STATIC_FILE_PATH
from item import create_item

VALID_FILE_EXTENSIONS = ("png", "gif", "jpeg", "jpg")

BUCKET_IDS = {}
for bucket in BUCKET_CONF:
    BUCKET_IDS[unicodedata.normalize("NFD", bucket["id"])] = bucket["id"]

    if "aliases" in bucket:
        for alias in bucket["aliases"]:
            BUCKET_IDS[unicodedata.normalize("NFD", alias)] = bucket["id"]


def match_folder_to_bucket(folder_name):
    folder = unicodedata.normalize("NFD", unquote(folder_name).split("/")[-1].lower())

    return BUCKET_IDS[folder] if folder in BUCKET_IDS else None


def parse_item(possible_item):
    file_path = unquote(possible_item["fileURL"].replace("file://", ""))
    basename = os.path.basename(file_path)
    filename, extension = os.path.splitext(basename)
    extension = extension.replace(".", "")

    if (
        extension in VALID_FILE_EXTENSIONS
        and os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        mod_seconds = os.path.getmtime(file_path)
        modification_date = datetime.datetime.utcfromtimestamp(mod_seconds)

        hash_appendix = get_hash_for_file(file_path)
        new_file_name = "{}.{}".format(hash_appendix, extension)

        im = Image.open(file_path)
        im.thumbnail((1024, 2048))
        im.save(os.path.join(STATIC_FILE_PATH, new_file_name))

        metadata = None
        if "comments" in possible_item:
            urls = parse_urls_from_string(possible_item["comments"])
            parsed_url = urlparse(urls[0])

            metadata = [
                {
                    "kind": "source",
                    "content": urls[0],
                    "url": True,
                    "url_name": parsed_url.netloc,
                }
            ]

        item = {
            "metadata": metadata,
            "datetime": modification_date,
            "timezone": "UTC",
            "image": new_file_name,
        }

        return create_item(
            metadata=item["metadata"],
            datetime=item["datetime"],
            timezone=item["timezone"],
            image=item["image"],
        )

    return None


def parse_bucket(possible_bucket):
    bucket = match_folder_to_bucket(possible_bucket["folderURL"])
    if bucket:
        print(possible_bucket["folderURL"])
        print(bucket)
        items = []
        for item in possible_bucket["items"]:
            parsed_item = parse_item(item)
            if parsed_item:
                items.append(parsed_item)

        return {"bucket": bucket, "items": items}

    return None


def import_files(directory_name):
    together_file = os.path.join(directory_name, "Together.json")
    if os.path.exists(together_file):
        if not os.path.exists(STATIC_FILE_PATH):
            os.makedirs(STATIC_FILE_PATH)

        buckets = {
            bucket["id"]: {"id": bucket["id"], "items": []} for bucket in BUCKET_CONF
        }

        with open(together_file, "r") as input_file:
            content = json.load(input_file)
            folders = content["Files"]["folders"]

            for folder in folders:
                result = parse_bucket(folder)
                if result and result["items"] and len(result["items"]):
                    buckets[result["bucket"]]["items"] += result["items"]

        return buckets

