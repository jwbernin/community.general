#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024,John Berninger <john.berninger@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.packemaker_helper import (
    ansiblize_resource,
)

DOCUMENTATION = '''
---
module: pacemaker_cluster_resource_info
short_description: Get information about pacemaker cluster resources
author:
  - John Berninger (@jwbernin)
description:
  - This module can manage pacemaker cluster resources using the pacemaker cli.
extends_documentation_fragment:
  - community.general.attributes
attributes:
    check_mode:
      support: full
    diff_mode:
      support: none
options:
    name:
      description:
        - the name of the cluster resource.
'''
EXAMPLES = '''
---
- name: Get localVIP resource
  hosts: localhost
  gather_facts: false
  become: true
  tasks:
  - name: Get resource named "localVIP" exists
    community.general.pacemaker_cluster_resource_info:
      name: localVIP
'''

RETURN = '''
resource:
    description: The Ansibilized JSON object representing the Pacemaker resource.
    type: str
    returned: always
'''

import time

from ansible.module_utils.basic import AnsibleModule


_PCS_CLUSTER_DOWN = "Error: cluster is not currently running on this node"
_PCS_NO_RESOURCE = "Error: No resource found"
_PCS_MISSING_RESOURCE = "Warning: Unable to find resource"

def get_resource(module, resource):
    cmd = "pcs resource config %s" % resource
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        return {'resource':None,'msg':out,'failed':True}
    else:
        return {'resource':resource,'msg':out,'failed':False}

def main():
    result = dict(
        changed=False,
        msg='',
    )
    argument_spec = dict(
        name=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    changed = False
    name = module.params['name']

    result['data'] = get_resource(module, name)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
