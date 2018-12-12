import click as click
import inject
import python_freeipa
import requests

from migrate import reader


def my_config(binder):
    hostname = 'localhost'
    client = python_freeipa.Client(hostname, verify_ssl=False)
    creds = ('login', 'password')
    client.login(*creds)

    binder.bind(python_freeipa.Client, client)
    requests.packages.urllib3.disable_warnings()


@click.group()
def main():
    inject.configure(my_config)


@main.command()
def read():
    reader.store_ipa_db()


if __name__ == '__main__':
    main()
