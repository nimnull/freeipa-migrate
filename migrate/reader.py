import shelve
import inject

from python_freeipa import Client


class MissingCalls:

    api_params = {
        'automember_find': {'all': True, 'raw': False},
        'automember_show': {'all': True, 'raw': False},

        'caacl_find': {'all': True, 'raw': False},
        'caacl_show': {'rights': True, 'all': True, 'raw': False},

        'cert_find': {},
        'cert_show': {},
        'certprofile_find': {},
        'certprofile_show': {},

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
        'dnszone_find': {},
        'dnszone_show': {},
        'domainlevel_get': {},
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

        'hbacsvc_find': {},
        'hbacsvc_show': {},

        'hbacsvcgroup_find': {},
        'hbacsvcgroup_show': {},

        'user_find': {
            'all': True,
            'no_members': False,  # Suppress processing of membership attributes.
            'sizelimit': 0,  # Maximum number of entries returned (0 is unlimited)
            'whoami': False  # Display user record for current Kerberos principal.
        },
        'user_show': {'all': True, 'raw': False},

        'hostgroup_find': {'all': True, 'raw': False, 'sizelimit': 0},
        'hostgroup_show': {'all': True, 'raw': False, 'rights': True},

        'host_find': {'all': True, 'raw': False, 'sizelimit': 0, 'timelimit': 0},
        'host_show': {'all': True, 'raw': False, 'rights': True},
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

    ca_acl_srv = cl.caacl_find()
    ca_acls = [cl.caacl_show(ca_acl['cn']) for ca_acl in ca_acl_srv]

    automember_serv = cl.automember_find(params={'type': 'hostgroup'})
    automembers = [cl.automember_show(am['cn'], {'type': 'hostgroup'}) for am in automember_serv]

    usergroups_srv = cl.group_find()
    usergroups = [cl.group_show(group['cn']) for group in usergroups_srv]

    users_srv = cl.user_find()
    users = [cl.user_show(user['uid']) for user in users_srv]

    hostgroups_srv = cl.hostgroup_find()
    hostgroups = [cl.hostgroup_show(hg['cn']) for hg in hostgroups_srv]

    hbacrules_srv = cl.hbacrule_find()
    hbacrules = [cl.hbacrule_show(rule['cn']) for rule in hbacrules_srv]

    hosts_srv = cl.host_find()
    hosts = [cl.host_show(h['fqdn'][0]) for h in hosts_srv]

    with shelve.open('ipa_dump.db') as storage:
        storage['automembers'] = automembers
        storage['ca_acls'] = ca_acls
        storage['hostgroups'] = hostgroups
        storage['hosts'] = hosts
        storage['hbacrules'] = hbacrules
        storage['usergroups'] = usergroups
        storage['users'] = users
        storage.sync()


"""
Group:
member_user: [<user>, <user>],
memberof_hbacrule: []


"""
