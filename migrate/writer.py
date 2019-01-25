import click
import inject
import python_freeipa.exceptions

from python_freeipa import Client


class WriterAPI:

    def __init__(self, client):
        self.client = client

    def test(self):
        item = None
        criteria = None
        params = None
        resp = self.client._request(item, criteria, params=params)

    def user_add(self):
        pass

    def group_add(self):
        pass

    def group_add_member(self):
        pass

    def dnszone_add(self, dns_zone: dict):
        required_params = [
            'idnssoarname',
            'idnssoaserial',
            'idnssoarefresh',
            'idnssoaretry',
            'idnssoaexpire',
            'idnssoaminimum'
        ]
        optional_params = [
            'idnsallowquery',
            'idnsallowtransfer',
            'idnsforwarders',
            'idnssoamname'
        ]

        params = dict((parameter, dns_zone[parameter][0])
                      for parameter in required_params)
        params_opt = dict((parameter, dns_zone[parameter][0])
                          for parameter in optional_params
                          if parameter in dns_zone)
        params.update(params_opt)

        idnsname = dns_zone['idnsname'][0]

        click.secho(f"Processing {idnsname}", fg='green')
        return self.client._request('dnszone_add',
                                    args=[idnsname],
                                    params=params)


@inject.params(client=Client)
def write_data(stored_data, client: Client = None):
    writer = WriterAPI(client)

    errors = []
    for zone in stored_data['dns_zones']:
        try:
            resp = writer.dnszone_add(zone)
            import ipdb; ipdb.set_trace()
        except python_freeipa.exceptions.BadRequest as err:
            click.secho(f"{err}, {zone}", fg='red')
            errors.append((zone, err))

    click.secho(f"Restored {len(stored_data['dns_zones'])} zones", fg='green')


"""
group 
    memberof_hbacrule
    memberof_role
    memberof_sudorule
    memberof_group
    
hbacrule
   servicecategory 
   usercategory
   hostcategory

dnszone
    idnsname - arg
    
    idnssoarname
    idnssoaserial
    idnssoarefresh
    idnssoaretry
    idnssoaexpire
    idnssoaminimum
    
    idnsallowquery
    idnsallowtransfer
    idnsforwarders
    idnssoamname
    

dnsrecord


dnsforwardzone
    idnszoneactive
    idnsname
    idnsforwarders
    idnsforwardpolicy

"""
