#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Kevin Breit (@kbreit) <kevin.breit@kevinbreit.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: meraki_vlan
short_description: Manage MX appliance traffic shaping in the Meraki cloud
version_added: "2.9"
description:
- Create, edit, query, or delete traffic shaping policies in the Meraki cloud.
notes:
- Some of the options are likely only used for developers within Meraki.
options:
    state:
      description:
      - Specifies whether object should be queried, created/modified, or removed.
      choices: [absent, present, query]
      default: query
    net_name:
      description:
      - Name of network which VLAN is in or should be in.
      aliases: [network]
    net_id:
      description:
      - ID of network which VLAN is in or should be in.
    vlan_id:
      description:
      - ID number of VLAN.
      - ID should be between 1-4096.
    name:
      description:
      - Name of VLAN.
      aliases: [vlan_name]
    subnet:
      description:
      - CIDR notation of network subnet.
    appliance_ip:
      description:
      - IP address of appliance.
      - Address must be within subnet specified in C(subnet) parameter.
    dns_nameservers:
      description:
      - Semi-colon delimited list of DNS IP addresses.
      - Specify one of the following options for preprogrammed DNS entries opendns, google_dns, upstream_dns
    reserved_ip_range:
      description:
      - IP address ranges which should be reserve and not distributed via DHCP.
    vpn_nat_subnet:
      description:
      - The translated VPN subnet if VPN and VPN subnet translation are enabled on the VLAN.
    fixed_ip_assignments:
      description:
      - Static IP address assignements to be distributed via DHCP by MAC address.
author:
- Kevin Breit (@kbreit)
extends_documentation_fragment: meraki
'''

EXAMPLES = r'''
'''

RETURN = r'''


'''

import os
from ansible.module_utils.basic import AnsibleModule, json, env_fallback
from ansible.module_utils._text import to_native
from ansible.module_utils.network.meraki.meraki import MerakiModule, meraki_argument_spec


def main():
    # define the available arguments/parameters that a user can pass to
    # the module

    fixed_ip_arg_spec = dict(mac=dict(type='str'),
                             ip=dict(type='str'),
                             name=dict(type='str'),
                             )

    reserved_ip_arg_spec = dict(start=dict(type='str'),
                                end=dict(type='str'),
                                comment=dict(type='str'),
                                )

    argument_spec = meraki_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present', 'query'], default='query'),
                         net_name=dict(type='str', aliases=['network']),
                         net_id=dict(type='str'),
                         vlan_id=dict(type='int'),
                         name=dict(type='str', aliases=['vlan_name']),
                         subnet=dict(type='str'),
                         appliance_ip=dict(type='str'),
                         fixed_ip_assignments=dict(type='list', default=None, elements='dict', options=fixed_ip_arg_spec),
                         reserved_ip_range=dict(type='list', default=None, elements='dict', options=reserved_ip_arg_spec),
                         vpn_nat_subnet=dict(type='str'),
                         dns_nameservers=dict(type='str'),
                         subset=dict(type='str', choices=['dscp', 'application_categories', 'mx', 'mr']),
                         number=dict(type='int'),
                         )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )
    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )
    meraki = MerakiModule(module, function='traffic_shaping')

    meraki.params['follow_redirects'] = 'all'

    query_dscp_urls = {'traffic_shaping': '/networks/{net_id}/trafficShaping/dscpTaggingOptions'}
    query_app_cat_urls = {'traffic_shaping': '/networks/{net_id}/trafficShaping/applicationCategories'}
    query_mx_urls = {'traffic_shaping': '/networks/{net_id}/trafficShaping'}
    query_mr_urls = {'traffic_shaping': '/networks/{net_id}/ssids/{ssid_number}/trafficShaping'}
    query_urls = {'traffic_shaping': '/networks/{net_id}/vlans'}
    query_url = {'traffic_shaping': '/networks/{net_id}/vlans/{vlan_id}'}
    create_url = {'traffic_shaping': '/networks/{net_id}/vlans'}
    update_url = {'traffic_shaping': '/networks/{net_id}/vlans/'}
    delete_url = {'traffic_shaping': '/networks/{net_id}/vlans/'}

    meraki.url_catalog['get_app_cat'] = query_app_cat_urls
    meraki.url_catalog['get_dscp'] = query_dscp_urls
    meraki.url_catalog['get_mx'] = query_mx_urls
    meraki.url_catalog['get_mr'] = query_mr_urls

    payload = None

    org_id = meraki.params['org_id']
    if org_id is None:
        org_id = meraki.get_org_id(meraki.params['org_name'])
    net_id = meraki.params['net_id']
    if net_id is None:
        nets = meraki.get_nets(org_id=org_id)
        net_id = meraki.get_net_id(net_name=meraki.params['net_name'], data=nets)

    if meraki.params['state'] == 'query':
        if meraki.params['subset'] == 'dscp':
            path = meraki.construct_path('get_dscp', net_id=net_id)
        elif meraki.params['subset'] == 'application_categories':
            path = meraki.construct_path('get_app_cat', net_id=net_id)
        elif meraki.params['subset'] == 'mr':
            path = meraki.construct_path('get_mr', net_id=net_id, custom={'ssid_number': meraki.params['number']})
        elif meraki.params['subset'] == 'mx':
            path = meraki.construct_path('get_mx', net_id=net_id)
        response = meraki.request(path, method='GET')
        if meraki.status == 200:
            meraki.result['data'] = response
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    meraki.exit_json(**meraki.result)


if __name__ == '__main__':
    main()
