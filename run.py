#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import importer


@click.command()
@click.argument('directory_name')
def file_import(directory_name):
    buckets = importer.import_files(directory_name)
    for bucket_id, bucket in buckets.items():
        click.echo(bucket_id)
        click.echo(bucket["items"][0])


if __name__ == '__main__':
    file_import()
