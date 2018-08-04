#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import importer


@click.command()
@click.argument("directory_name")
def file_import(directory_name):
    buckets = importer.import_files(directory_name)
    for bucket_id, bucket in buckets.items():
        if len(bucket["items"]):
            # click.echo(bucket_id)
            click.echo(bucket["items"][0].text)
            # click.echo(bucket["items"][0].datetime)
            click.echo(bucket["items"][0].metadata)
            # click.echo(bucket["items"][0].place)


if __name__ == "__main__":
    file_import()
