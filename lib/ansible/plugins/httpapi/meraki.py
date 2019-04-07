# -*- coding: utf-8 -*-

# This code is part of Ansible, but is an independent component

# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.

# Copyright: (c) 2019, Kevin Breit <kevin.breit@kevinbreit.net>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
author: Kevin Breit
httpapi: meraki
short_description: Use Meraki's Dashboard API to run commands
description:
  - This Meraki plugin provides low level abstraction API's for
    sending and receiving commands against Meraki's Dashboard.
version_added: "2.9"
"""

import time
from random import uniform
from ansible.module_utils.connection import ConnectionError
from ansible.plugins.httpapi import HttpApiBase

BASE_HEADERS = {'Content-Type': 'application/json',
                'X-Cisco-Meraki-API-Key': None}
RATE_LIMIT_CODE = 429
URL_PREFIX = 'api.meraki.com/api/v0'

class HttpApi(HttpApiBase):
    def __init__(self, connection):
        super(HttpApi, self).__init__(connection)
        self.connection = connection
        BASE_HEADERS['X-Cisco-Meraki-API-Key'] = self.connection.get_option('password')
        self.path = None
        self.data = None
        self.retry_count = 0

    def send_request(self, path, data, **message_kwargs):
        try:
            response, response_content = self.connection.send(path, data, method=method, headers=headers)
        except HTTPError as exc:
            return exc.code(), exc.read()

    def handle_httperror(self, exc):
        if exc.code == RATE_LIMIT_CODE:
            if self.retry_count == 10:
                return False
            time.sleep(uniform(0.5, 5.0))
            self.send_request(self.path, self.data)
            return True
        if exc.code == 404:
            return False
