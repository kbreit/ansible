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
- Networks allow for up to 8 rules.
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

DEFINTION_TYPE_GENERIC = ('host', 'port', 'ip_range', 'local_net')
DEFINTION_TYPE_APP = ('application', 'application_category')

def main():
    # define the available arguments/parameters that a user can pass to
    # the module

    defintions_arg_spec = dict(application=dict(type='str', default=None),
                                  application_category=dict(type='str', default=None),
                                  host=dict(type='str', default=None),
                                  port=dict(type='str', default=None),
                                  ip_range=dict(type='str', default=None),
                                  local_net=dict(type='str', default=None),
                                  )

    limits_arg_spec = dict(limit_up=dict(type='int'),
                              limit_down=dict(type='int'),
                              )

    pcbw_arg_spec = dict(settings=dict(type='str', choices=['network default',
                                                               'ignore',
                                                               'custom']),
                            bandwidth_limits=dict(type='dict', default=None, options=limits_arg_spec),
                            )

    mx_rules_arg_spec = dict(definitions=dict(type='list', default=None, elements=dict, options=defintions_arg_spec),
                             per_client_bandwidth_limits=dict(type='dict', default=None, options=pcbw_arg_spec),
                             dscp_tag=dict(type='str'),
                             priority=dict(type='str', choices=['low', 'normal', 'high']),
                             )

    mr_rules_arg_spec = dict(definitions=dict(type='list', default=None, elements=dict, options=defintions_arg_spec),
                             per_client_bandwidth_limits=dict(type='dict', default=None, options=pcbw_arg_spec),
                             dscp_tag=dict(type='str'),
                             priority=dict(type='str', choices=['low', 'normal', 'high']),
                             pcp_tag=dict(type='int'),
                             )

    mx_rule_arg_spec = dict(default_rules_enabled=dict(type='bool'),
                            rules=dict(type='list', default=None, elements=dict, options=mx_rules_arg_spec),
                            )

    reserved_ip_arg_spec = dict(start=dict(type='str'),
                                end=dict(type='str'),
                                comment=dict(type='str'),
                                )

    argument_spec = meraki_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present', 'query'], default='query'),
                         net_name=dict(type='str', aliases=['network']),
                         net_id=dict(type='str'),
                         reserved_ip_range=dict(type='list', default=None, elements='dict', options=reserved_ip_arg_spec),
                         subset=dict(type='str', choices=['dscp', 'application_categories', 'mx', 'mr']),
                         number=dict(type='int'),
                         mx_rules=dict(type='dict', default=None, options=mx_rule_arg_spec),
                         mr_rules=dict(type='dict', default=None, options=mr_rule_arg_spec),
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
    update_mx_urls = {'traffic_shaping': '/networks/{net_id}/trafficShaping'}

    meraki.url_catalog['get_app_cat'] = query_app_cat_urls
    meraki.url_catalog['get_dscp'] = query_dscp_urls
    meraki.url_catalog['get_mx'] = query_mx_urls
    meraki.url_catalog['update_mx'] = update_mx_urls
    meraki.url_catalog['get_mr'] = query_mr_urls

    org_id = meraki.params['org_id']
    if org_id is None:
        org_id = meraki.get_org_id(meraki.params['org_name'])
    net_id = meraki.params['net_id']
    if net_id is None:
        nets = meraki.get_nets(org_id=org_id)
        net_id = meraki.get_net_id(net_name=meraki.params['net_name'], data=nets)

    # Assemble payload data structure
    # Yes it's ugly. The data structure isn't trivial
    if meraki.params['state'] == 'present':
        payload = dict()
        if meraki.params['mx_rules']['default_rules_enabled'] is not None:
            payload['defaultRulesEnabled'] = meraki.params['mx_rules']['default_rules_enabled']
        rule_list = []
        for rule in meraki.params['mx_rules']['rules']:
            rule_dict = dict()
            if rule['definitions']:
                definitions = []
                meraki.fail_json(msg=rule['definitions'])
                for definition in rule['definitions']:
                    if definition['host']:
                        item = {'type': 'host',
                                'value': definition['host']}
                    elif definition['port']:
                        item = {'type': 'port',
                                'value': definition['port']}
                    elif definition['ip_range']:
                        item = {'type': 'ipRange',
                                'value': definition['ip_range']}
                    elif definition['local_net']:
                        item = {'type': 'localNet',
                                'value': definition['local_net']}
                    elif definition['application']:
                        item = {'type': 'application',
                                'value': {'id': definition['application']}}
                    elif definition['application_category']:
                        item = {'type': 'applicationCategory',
                                'value': {'id': definition['application_category']}}
                    definitions.append(item)
                rule_dict['definitions'] = definitions
            if rule['per_client_bandwidth_limits'] is not None:
                limit = {'settings': rule['per_client_bandwidth_limits']['settings']}
                if rule['per_client_bandwidth_limits']['settings'] == 'custom':
                    limit['bandwidthLimits'] = {'limitUp': rule['per_client_bandwidth_limits']['bandwidth_limits']['limit_up'],
                                                'limitDown': rule['per_client_bandwidth_limits']['bandwidth_limits']['limit_down']}
                rule_dict['perClientBandwidthLimits'] = limit
            if rule['dscp_tag'] is not None:
                rule_dict['dscpTagValue'] = rule['dscp_tag']
            if rule['priority'] is not None:
                rule_dict['priority'] = rule['priority']
            rule_list.append(rule_dict)
        payload['rules'] = rule_list

    meraki.fail_json(msg="mx_rule_payload", payload=payload)

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
    elif meraki.params['state'] == 'present':
        if meraki.params['mx_rules']:
            path = meraki.construct_path('update_mx', net_id=net_id)
            response = meraki.request(path, method='PUT')

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    meraki.exit_json(**meraki.result)


if __name__ == '__main__':
    main()
