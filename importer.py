#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import hashlib
import re
from collections import defaultdict

from config import BUCKETS as BUCKET_CONF
from item import create_item_from_string


def match_to_bucket(filepath):
    for bucket in BUCKET_CONF:
        if bucket["filename_pattern"].search(os.path.basename(filepath)):
            return bucket["id"]

    return False


def get_id_for_item(item):
    hashlib.sha1(item["date"]).hexdigest()[:12]


def split_file_into_chunks(filepath):
    with open(filepath, "r") as input_file:
        content = input_file.read()
        return content.split("------")


def get_files_by_bucket(directory_name):
    buckets = {
        bucket["id"]: {"id": bucket["id"], "filepaths": []} for bucket in BUCKET_CONF
    }
    for filepath in glob.iglob(
        os.path.join(directory_name, "**/*.txt"), recursive=True
    ):
        bucket = match_to_bucket(filepath)
        if bucket:
            buckets[bucket]["filepaths"].append(filepath)

    return buckets


def parse_chunks_into_items(chunks):
    items = []
    for chunk in chunks:
        item = create_item_from_string(chunk)
        if item:
            items.append(item)
    return items


def import_files(directory_name):
    buckets = get_files_by_bucket(directory_name)
    for _, bucket in buckets.items():
        bucket["items"] = []
        for filepath in bucket["filepaths"]:
            chunks = split_file_into_chunks(filepath)
            items = parse_chunks_into_items(chunks)
            bucket["items"] += items

    return buckets
