import shelve
from itertools import chain

import click
import inject

from python_freeipa import Client


class MissingCalls:

    api_params = {
        'automember_find': {'all': True, 'raw': False},
        'automember_show': {'all': True, 'raw': False},

        'caacl_find': {'all': True, 'raw': False},
        'caacl_show': {'rights': True, 'all': True, 'raw': False},

        'cert_find': {'all': True, 'raw': False, 'no_members': False},
        'cert_show': {},  # serial_number
        'certprofile_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'certprofile_show': {'all': True, 'raw': False, 'rights': True},  # cn

        'config_show': {'all': True, 'raw': False, 'rights': True},

        'cosentry_find': {'all': True, 'raw': False},
        'cosentry_show': {'all': True, 'raw': False, 'rights': True},

        'delegation_find': {'all': True, 'raw': False},
        'delegation_show': {'all': True, 'raw': False},  # aciname
        # DNS
        'dnsconfig_show': {'all': True, 'raw': False, 'rights': True},
        'dnsforwardzone_find': {'all': True, 'raw': False},
        'dnsforwardzone_show': {'all': True, 'raw': False, 'rights': True},
        'dnsrecord_find': {'all': True, 'raw': False},
        'dnsrecord_show': {'all': True, 'raw': False, 'rights': True, 'structured': True},
        'dnszone_find': {'forward_only': False, 'sizelimit': 0, 'all': True, 'raw': False},
        'dnszone_show': {'all': True, 'raw': False, 'rights': True},

        'env': {'all': True},

        'group_find': {'all': True, 'sizelimit': 0},
        'group_show': {'all': True, 'raw': False},

        'hbacrule_find': {
            'all': True,
            'no_members': False,  # Suppress processing of membership attributes.
            'sizelimit': 0,  # Maximum number of entries returned (0 is unlimited)
            'raw': False
        },
        'hbacrule_show': {'all': True, 'raw': False, 'rights': True},

        'hbacsvc_find': {'no_members': True, 'all': True, 'raw': False, },
        'hbacsvc_show': {'no_members': True, 'all': True, 'raw': False, 'rights': True},  # cn

        'hbacsvcgroup_find': {'no_members': True, 'all': True, 'raw': False, },
        'hbacsvcgroup_show': {'no_members': True, 'all': True, 'raw': False, 'rights': True},  # cn

        'host_find': {'all': True, 'raw': False, 'sizelimit': 0, 'timelimit': 0},
        'host_show': {'all': True, 'raw': False, 'rights': True},

        'hostgroup_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'hostgroup_show': {'all': True, 'raw': False, 'rights': True},

        'idrange_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'idrange_show': {'all': True, 'raw': False, 'rights': True},  # cn

        'krbtpolicy_show': {'rights': True, 'all': True, 'raw': False},

        'netgroup_find': {'all': True, 'raw': False, 'sizelimit': 0,
                          'no_members': True,
                          'managed': True,
                          'private': True},
        'netgroup_show': {'rights': True, 'all': True, 'raw': False, 'no_members': False},  # cn

        'otpconfig_show': {'rights': True, 'all': True, 'raw': False},

        'pwpolicy_show': {'all': True, 'raw': False, 'rights': True},

        'permission_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': False},
        'permission_show': {'rights': True, 'all': True, 'raw': False},  # cn

        'privilege_find': {'all': True, 'raw': False, 'no_members': False},
        'privilege_show': {'all': True, 'raw': False, 'no_members': False, 'rights': True},  # cn

        'realmdomains_show': {'all': True, 'raw': False, 'rights': True},

        'role_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': False},
        'role_show': {'rights': True, 'all': True, 'raw': False, 'no_members': False},  # cn

        'selfservice_find': {'all': True, 'raw': False},
        'selfservice_show': {'all': True, 'raw': False},  # aciname

        'servicedelegationrule_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': False},
        'servicedelegationrule_show': {'rights': True, 'all': True, 'raw': False, 'no_members': False},  # cn
        'servicedelegationtarget_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'servicedelegationtarget_show': {'rights': True, 'all': True, 'raw': False},  # cn

        'stageuser_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': False},
        'stageuser_show': {'rights': True, 'all': True, 'raw': False, 'no_members': False},  # uid

        'sudocmdgroup_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': False},
        'sudocmdgroup_show': {'rights': True, 'all': True, 'raw': False, 'no_members': False},  # cn
        'sudorule_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': False},
        'sudorule_show': {'rights': True, 'all': True, 'raw': False, 'no_members': False},  # cn

        'user_find': {
            'all': True,
            'no_members': False,  # Suppress processing of membership attributes.
            'sizelimit': 0,  # Maximum number of entries returned (0 is unlimited)
            'whoami': False  # Display user record for current Kerberos principal.
        },
        'user_show': {'all': True, 'raw': False},

    }

    def __init__(self, client):
        self.client = client

    def __getattr__(self, item):
        if item not in self.api_params:
            raise AttributeError()

        def closure(criteria=None, params=None):
            default_params = self.api_params.get(item, {}).copy()
            if params:
                default_params.update(params)
            resp = self.client._request(item, criteria, params=params)
            return resp['result']

        return closure


@inject.params(client=Client)
def store_ipa_db(database_file, client: Client = None):
    api_reader = MissingCalls(client)

    with shelve.open(database_file) as storage:

        dns_zones = [
            api_reader.dnszone_show(zone['idnsname'])
            for zone in api_reader.dnszone_find()
        ]
        dns_records = [api_reader.dnsrecord_find(zone['idnsname']) for zone in dns_zones]

        storage['automembers'] = [
                api_reader.automember_show(am['cn'], params={'type': 'hostgroup'})
                for am in api_reader.automember_find(params={'type': 'hostgroup'})]
        click.secho("Saved automembers", fg="green")

        # storage['ca_acls'] =  [
        #         api_reader.caacl_show(ca_acl['cn'])
        #         for ca_acl in api_reader.caacl_find()]
        # click.secho("Saved ca_acls", fg="green")
        #
        # storage['certprofiles'] = [
        #         api_reader.certprofile_show(cert_p['cn'])
        #         for cert_p in api_reader.certprofile_find()]
        # click.secho("Saved certprofiles", fg="green")

        storage['dns_zones'] = dns_zones
        click.secho("Saved dns_zones", fg="green")

        storage['dns_records'] = list(chain.from_iterable(dns_records))
        click.secho("Saved dns_records", fg="green")

        storage['groups'] = [
                api_reader.group_show(group['cn'])
                for group in api_reader.group_find()]
        click.secho("Saved groups", fg="green")

        storage['hostgroups'] = [
                api_reader.hostgroup_show(hg['cn'])
                for hg in api_reader.hostgroup_find()]
        click.secho("Saved hostgroups", fg="green")

        storage['hosts'] = [
                api_reader.host_show(h['fqdn'][0])
                for h in api_reader.host_find()]
        click.secho("Saved hosts", fg="green")

        storage['hbacrules'] = [
                api_reader.hbacrule_show(rule['cn'])
                for rule in api_reader.hbacrule_find()]
        click.secho("Saved hbacrules", fg="green")

        storage['users'] = [
                api_reader.user_show(user['uid'])
                for user in api_reader.user_find()]
        click.secho("Saved users", fg="green")

        storage['netgroups'] = [
                api_reader.netgroup_show(g['cn'], params={})
                for g in api_reader.netgroup_find()]
        click.secho("Saved netgroups", fg="green")

        storage['roles'] = [
                api_reader.role_show(role['cn'])
                for role in api_reader.role_find()]
        click.secho("Saved roles", fg="green")

        storage['privileges'] = [
                api_reader.privilege_show(priv['cn'])
                for priv in api_reader.privilege_find()]
        click.secho("Saved privileges", fg="green")

        storage['realmdomains'] = api_reader.realmdomains_show([])
        click.secho("Saved realmdomains", fg="green")

        storage.sync()
