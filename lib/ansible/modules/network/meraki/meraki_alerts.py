#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Kevin Breit (@kbreit) <kevin.breit@kevinbreit.net>
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
module: meraki_alerts
short_description: Manage event alert settings in the Meraki cloud.
version_added: "2.10"
description:
- Allows for management of event alerts within Meraki environments.
options:
    auth_key:
        description:
        - Authentication key provided by the dashboard. Required if environmental variable MERAKI_KEY is not set.
        type: str
    state:
        description:
        - Query or edit syslog servers
        - To delete a syslog server, do not include server in list of servers
        choices: [present, query]
        default: present
        type: str
    net_name:
        description:
        - Name of a network.
        aliases: [name, network]
        type: str
    net_id:
        description:
        - ID number of a network.
        type: str
    servers:
        description:
        - List of syslog server settings
        suboptions:
            host:
                description:
                - IP address or hostname of Syslog server.
            port:
                description:
                - Port number Syslog server is listening on.
                default: "514"
            roles:
                description:
                - List of applicable Syslog server roles.
                choices: ['Wireless event log',
                          'Appliance event log',
                          'Switch event log',
                          'Air Marshal events',
                          'Flows',
                          'URLs',
                          'IDS alerts',
                          'Security events']

author:
    - Kevin Breit (@kbreit)
extends_documentation_fragment: meraki
'''

EXAMPLES = r'''
- name: Query syslog configurations on network named MyNet in the YourOrg organization
  meraki_syslog:
    auth_key: abc12345
    status: query
    org_name: YourOrg
    net_name: MyNet
  delegate_to: localhost

- name: Add single syslog server with Appliance event log role
  meraki_syslog:
    auth_key: abc12345
    status: query
    org_name: YourOrg
    net_name: MyNet
    servers:
      - host: 192.0.1.2
        port: 514
        roles:
          - Appliance event log
  delegate_to: localhost

- name: Add multiple syslog servers
  meraki_syslog:
    auth_key: abc12345
    status: query
    org_name: YourOrg
    net_name: MyNet
    servers:
      - host: 192.0.1.2
        port: 514
        roles:
          - Appliance event log
      - host: 192.0.1.3
        port: 514
        roles:
          - Appliance event log
          - Flows
  delegate_to: localhost
'''

RETURN = r'''
data:
    description: Information about the created or manipulated object.
    returned: info
    type: complex
    contains:
      host:
        description: Hostname or IP address of syslog server.
        returned: success
        type: string
        sample: 192.0.1.1
      port:
        description: Port number for syslog communication.
        returned: success
        type: string
        sample: 443
      roles:
        description: List of roles assigned to syslog server.
        returned: success
        type: list
        sample: "Wireless event log, URLs"
'''

import os
from ansible.module_utils.basic import AnsibleModule, json, env_fallback
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_native
from ansible.module_utils.common.dict_transformations import recursive_diff
from ansible.module_utils.network.meraki.meraki import MerakiModule, meraki_argument_spec


def construct_payload(meraki):
    payload = dict()

    if meraki.params['default_destinations']:
        payload = {'defaultDestinations': {'emails': None,
                                           'allAdmins': None,
                                           'snmp': None},
                                           }
        payload['defaultDestinations']['emails'] = meraki.params['default_destinations']['emails']
        payload['defaultDestinations']['allAdmins'] = meraki.params['default_destinations']['all_admins']
        payload['defaultDestinations']['snmp'] = meraki.params['default_destinations']['snmp']
    return payload


def main():

    # define the available arguments/parameters that a user can pass to
    # the module

    destinations_arg_spec = dict(emails=dict(type='list', element=str),
                                 all_admins=dict(type='bool'),
                                 snmp=dict(type='bool'),
                                 )

    alert_arg_spec = dict(type=dict(element=str),
                          enabled=dict(type='bool'),
                          alert_destinations=dict(type='dict', options=destinations_arg_spec),
                          filters=dict(type='dict'),
                          )

    argument_spec = meraki_argument_spec()
    argument_spec.update(net_id=dict(type='str'),
                         net_name=dict(type='str', aliases=['name', 'network']),
                         default_destinations=dict(type='dict', options=destinations_arg_spec),
                         alerts=dict(type='list', element=dict, options=alert_arg_spec),
                         state=dict(type='str', choices=['present', 'query'], default='present'),
                         )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )

    meraki = MerakiModule(module, function='alert')
    module.params['follow_redirects'] = 'all'
    payload = None

    query_urls = {'alert': '/networks/{net_id}/alertSettings'}
    meraki.url_catalog['query'] = query_urls

    org_id = meraki.params['org_id']
    if not org_id:
        org_id = meraki.get_org_id(meraki.params['org_name'])
    net_id = meraki.params['net_id']
    if net_id is None:
        nets = meraki.get_nets(org_id=org_id)
        net_id = meraki.get_net_id(net_name=meraki.params['net_name'], data=nets)

    if meraki.params['state'] == 'query':
        path = meraki.construct_path('query', net_id=net_id)
        response = meraki.request(path, method='GET')
        meraki.result['data'] = response
    elif meraki.params['state'] == 'present':
        # meraki.fail_json(construct_payload(meraki))
        path = meraki.construct_path('query', net_id=net_id)
        original = meraki.request(path, method='GET')
        payload = construct_payload(meraki)
        # meraki.fail_json(msg="Compare", original=original, payload=payload)
        if meraki.is_update_required(original, payload) is True:
            response = meraki.request(path, method='PUT', payload=json.dumps(payload))
            meraki.result['data'] = response
            meraki.result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    meraki.exit_json(**meraki.result)


if __name__ == '__main__':
    main()
