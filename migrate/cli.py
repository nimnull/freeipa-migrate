import os
import shelve

import click as click
import inject
import python_freeipa
import requests

from migrate import reader, writer


def my_config(binder):
    hostname = os.getenv('IPA_HOST')
    client = python_freeipa.Client(hostname, verify_ssl=False)

    client.login(os.getenv('IPA_LOGIN'), os.getenv('IPA_PASSWORD'))

    binder.bind(python_freeipa.Client, client)
    requests.packages.urllib3.disable_warnings()


@click.group()
def main():
    inject.configure(my_config)


@main.command()
@click.argument('database_file', nargs=1, type=click.Path())
def dump(database_file):
    reader.store_ipa_db(database_file)


@main.command()
@click.argument('database_file', nargs=1, type=click.Path(exists=True))
def restore(database_file):

    with shelve.open(database_file) as storage:
        writer.write_data(storage)


if __name__ == '__main__':
    main()
