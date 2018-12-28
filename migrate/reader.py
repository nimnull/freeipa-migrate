import shelve
import inject

from python_freeipa import Client


class MissingCalls:

    api_params = {
        'automember_find': {'all': True, 'raw': False},
        'automember_show': {'all': True, 'raw': False},

        'caacl_find': {'all': True, 'raw': False},
        'caacl_show': {'rights': True, 'all': True, 'raw': False},

        'cert_find': {'all': True, 'raw': False},
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

        'netgroup_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'netgroup_show': {'rights': True, 'all': True, 'raw': False},  # cn

        'otpconfig_show': {'rights': True, 'all': True, 'raw': False},

        'pwpolicy_show': {'all': True, 'raw': False, 'rights': True},

        'permission_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': True},
        'permission_show': {'rights': True, 'all': True, 'raw': False},  # cn

        'realmdomains_show': {'all': True, 'raw': False, 'rights': True},

        'role_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': True},
        'role_show': {'rights': True, 'all': True, 'raw': False, 'no_members': True},  # cn

        'selfservice_find': {'all': True, 'raw': False},
        'selfservice_show': {'all': True, 'raw': False},  # aciname

        'servicedelegationrule_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': True},
        'servicedelegationrule_show': {'rights': True, 'all': True, 'raw': False, 'no_members': True},  # cn
        'servicedelegationtarget_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'servicedelegationtarget_show': {'rights': True, 'all': True, 'raw': False},  # cn

        'stageuser_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': True},
        'stageuser_show': {'rights': True, 'all': True, 'raw': False, 'no_members': True},  # uid

        'sudocmdgroup_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': True},
        'sudocmdgroup_show': {'rights': True, 'all': True, 'raw': False, 'no_members': True},  # cn
        'sudorule_find': {'sizelimit': 0, 'all': True, 'raw': False, 'no_members': True},
        'sudorule_show': {'rights': True, 'all': True, 'raw': False, 'no_members': True},  # cn

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
def store_ipa_db(client: Client = None):
    cl = MissingCalls(client)

    with shelve.open('ipa_dump.db') as storage:
        storage['automembers'] = [
            cl.automember_show(am['cn'], {'type': 'hostgroup'})
            for am in cl.automember_find(params={'type': 'hostgroup'})
        ]
        storage['ca_acls'] = [
            cl.caacl_show(ca_acl['cn'])
            for ca_acl in cl.caacl_find()
        ]
        storage['certs'] = [
            cl.cert_show(crt['serial_number'])
            for crt in cl.cert_find()
        ]

        storage['certprofiles'] = [
            cl.certprofile_show(cert_p['cn'])
            for cert_p in cl.certprofile_find()
        ]

        storage['hostgroups'] = [
            cl.hostgroup_show(hg['cn'])
            for hg in cl.hostgroup_find()
        ]
        storage['hosts'] = [
            cl.host_show(h['fqdn'][0])
            for h in cl.host_find()
        ]
        storage['hbacrules'] = [
            cl.hbacrule_show(rule['cn'])
            for rule in cl.hbacrule_find()
        ]
        storage['dns_zones'] = [
            cl.dnszone_show(zone['idnsname'])
            for zone in cl.dnszone_find()
        ]
        storage['netgroups'] = [
            cl.netgroup_show(g['cn'], params={'no_members': True})
            for g in cl.netgroup_find(params={'no_members': True, 'managed': True, 'private': True})
        ]
        storage['users'] = [
            cl.user_show(user['uid'])
            for user in cl.user_find()
        ]
        storage['usergroups'] = [
            cl.group_show(group['cn'])
            for group in cl.group_find()
        ]

        storage['realmdomains'] = cl.realmdomains_show([])
        storage.sync()
