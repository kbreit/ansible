# -*- coding: utf-8 -*-

# Copyright 2019 Kevin Breit <kevin.breit@kevinbreit.net>

# This file is part of Ansible by Red Hat
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import pytest

from units.compat import unittest
from unittest import mock
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.meraki.meraki import MerakiModule, meraki_argument_spec
from ansible.module_utils.six import PY2, PY3
from ansible.module_utils._text import to_native, to_bytes
from units.modules.utils import set_module_args

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}
testcase_data = {
    "params": {'orgs': ['orgs.json'],
               }
}

def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    # try:
    data = json.loads(data)
    # except Exception:
    #     pass

    fixture_data[path] = data
    return data

@pytest.fixture(scope="module")
def module():
    argument_spec = meraki_argument_spec()
    set_module_args({'auth_key': 'abc123',
                     })
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)
    return MerakiModule(module)


def mocked_fetch_url():
    response_mock = Mock()
    if args[0] == 'https://api.meraki.com/404':
        info = {'status': 404,
                'body': "404 - Page is missing",
                }
    return (None, info)

def test_fetch_url_404(module, mocker):
    mocker.patch('ansible.module_utils.urls.fetch_url')
    mocker.side_effect = mocked_fetch_url
    
    url = 'https://api.meraki.com/404'
    data = module.request(url, method='GET')
    print(data)
    assert module.status == 404


def test_define_protocol_https(module):
    module.params['use_https'] = True
    module.define_protocol()
    testdata = module.params['protocol']
    assert testdata == 'https'


def test_define_protocol_http(module):
    module.params['use_https'] = False
    module.define_protocol()
    testdata = module.params['protocol']
    assert testdata == 'http'


def test_is_org_valid_org_name(module):
    data = load_fixture('orgs.json')
    org_count = module.is_org_valid(data, org_name="My organization")
    assert org_count == 1


def test_is_org_valid_org_id(module):
    data = load_fixture('orgs.json')
    org_count = module.is_org_valid(data, org_id=2930418)
    assert org_count == 1
