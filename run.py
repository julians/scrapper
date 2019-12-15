#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import importer
import json
import datetime
from itertools import chain
from models import Item, Metadata, ItemMetadata
from config import db

date_handler = lambda obj: (
    obj.isoformat() if isinstance(obj, (datetime.datetime, datetime.date)) else None
)


@db.atomic()
def save_item_to_db(item, bucket=None):
    lat = None
    lng = None
    if item["place"] and item["place"]["coordinates"]:
        lat = item["place"]["coordinates"][0]
        lng = item["place"]["coordinates"][1]

    saved_item = Item.create(
        text=item["text"],
        image=item["image"],
        created_at=item["datetime"],
        lat=lat,
        lng=lng,
        language=item["language"],
        hashid=item["hashid"],
        bucket=bucket,
    )

    if item["metadata"]:
        for metadata in item["metadata"]:
            saved_metadata = Metadata.create(**metadata)
            ItemMetadata.create(item=saved_item, metadata=saved_metadata)


@click.command()
@click.argument("directory_name")
def file_import(directory_name):
    buckets = importer.import_files(directory_name)

    # with open("test_out.json", "w") as test_output_file:
    #     json.dump(buckets, test_output_file, default=date_handler, indent=4)

    # all_items = list(chain.from_iterable([x["items"] for x in buckets.values()]))

    db.connect()
    db.drop_tables([Item, Metadata, ItemMetadata])
    db.create_tables([Item, Metadata, ItemMetadata])

    for bucket in buckets.values():
        bucket_id = bucket["id"][:-1]
        for item in bucket["items"]:
            # print(item["datetime"], item["text"], item["image"])
            save_item_to_db(item, bucket=bucket_id)

    db.close()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    file_import()
