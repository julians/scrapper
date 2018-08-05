#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import importer
import json
import datetime

date_handler = lambda obj: (
    obj.isoformat() if isinstance(obj, (datetime.datetime, datetime.date)) else None
)


@click.command()
@click.argument("directory_name")
def file_import(directory_name):
    buckets = importer.import_files(directory_name)
    print(json.dumps(buckets, default=date_handler, indent=4))
    # for _, bucket in buckets.items():
    #     if len(bucket["items"]):
    #         # click.echo(bucket_id)
    #         click.echo(bucket["items"][0].text)
    #         # click.echo(bucket["items"][0].datetime)
    #         click.echo(bucket["items"][0].metadata)
    #         click.echo(bucket["items"][0].place)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    file_import()
