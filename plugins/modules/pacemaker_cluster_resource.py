#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024,John Berninger <john.berninger@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_cluster_resource
short_description: Manage pacemaker cluster resources
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
      type: str
    state:
      description:
        - The desired state of the resource. If V(present) and the resource already exists, it will not be updated. 
      choices: [ present, updated, absent, relocated ]
      type: str
    node:
      description:
        - The node (location) the resource should be active on. Only
          used when state == relocated.
      type: str
    timeout:
      description:
        - Timeout when the module should considered that the action has failed.
      default: 300
      type: int
    force:
      description:
        - Force the change of the resource state.
      type: bool
      default: true
    resource:
      description:
        - Resource(s) to add / update. Ignored when state is V(absent) or V(relocated).
      type: list
      elements: dict
      suboptions:
        standard:
        provider:
        type:
        operations:
        meta:
        clone:
        promotable:
        group:
        disabled:
        agent_validation:
        reource_options:
'''
EXAMPLES = '''
---
- name: Ensure a resource named "localVIP" exists
  community.general.pacemaker_cluster_resource:
    state: present
    name: localVIP

- name: Ensure resource floatingVIP exists
  comunity.general.pacemaker_cluster_resource:
    state: present
    name: floatingVIP
    resources:
      - standard: ocf
        provider: heartbeat
        type: IPaddr2
        resource_options: "ip=172.31.40.87 cidr_netmask=255.255.255.0"
        group: "webservergroup"
  
'''

RETURN = '''
changed:
    description: true if the cluster state has changed
    type: bool
    returned: always
rc:
    description: exit code of the module
    type: bool
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

def update_resource(module, name, resource):
    result = {}
    cmd = "pcs resource update %s %s:%s:%s" % (name, resource['standard'], resource['provider'], resource['type'])
    cmd = "%s %s", (cmd, resource['resource_options')
    if resource['operations'] != '':
        cmd = "%s op %s", (cmd, resource['operations'])
    if resource['meta'] != '':
        cmd = "%s meta %s", (cmd, resource['meta'])
    if resource['clone'] != '':
        cmd = "%s clone %s", (cmd, resource['clone'])
    if resource['promotable'] != '':
        cmd = "%s promotable %s", (cmd, resource['promotable'])
    if resource['group'] != '':
        cmd = "%s group %s", (cmd, resource['group'])
    if resource['disabled']:
        cmd = "%s %s", (cmd, '--disabled')
    if resource['agent_validation']:
        cmd = "%s %s", (cmd, '--agent-validation')
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        result['failed'] = True
        result['changed'] = False
        result['output'] = out
        result['error'] = err
        module.fail_json(**result)
    else:
        result['changed'] = True
        result['failed'] = False
        result['resource'] = get_resource(module, name)
        return result


def create_resource(module, name, resource):
    result = {}
    cmd = "pcs resource create %s %s:%s:%s" % (name, resource['standard'], resource['provider'], resource['type'])
    cmd = "%s %s", (cmd, resource['resource_options')
    if resource['operations'] != '':
        cmd = "%s op %s", (cmd, resource['operations'])
    if resource['meta'] != '':
        cmd = "%s meta %s", (cmd, resource['meta'])
    if resource['clone'] != '':
        cmd = "%s clone %s", (cmd, resource['clone'])
    if resource['promotable'] != '':
        cmd = "%s promotable %s", (cmd, resource['promotable'])
    if resource['group'] != '':
        cmd = "%s group %s", (cmd, resource['group'])
    if resource['disabled']:
        cmd = "%s %s", (cmd, '--disabled')
    if resource['agent_validation']:
        cmd = "%s %s", (cmd, '--agent-validation')
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        result['failed'] = True
        result['changed'] = False
        result['output'] = out
        result['error'] = err
        module.fail_json(**result)
    else:
        result['changed'] = True
        result['failed'] = False
        result['resource'] = get_resource(module, name)
        return result

def main():
    result = dict(
        changed=False,
        msg='',
    )
    argument_spec = dict(
        name=dict(type='str'),
        node=dict(type='str'),
        state=dict(default='present', type='str', choices=['present', 'absent', 'relocated', 'updated']),
        timeout=dict(type='int', default=300),
        force=dict(type='bool', default=True),
        resources=dict(
            type='list',
            elements='dict',
            suboptions=dict(
               standard=dict(type='str', default='ocf'),
               provider=dict(type='str', default='heartbeat'),
               type=dict(type='str'),
               operations=dict(type='str'),
               meta=dict(type='str'),
               clone=dict(type='str'),
               promotable=dict(type='str'),
               group=dict(type='str'),
               disabled=dict(type='bool', default=False),
               agent_validation=dict(type='bool', default=False),
               resource_options=dict(type='str', aliases=['options']),
            ),
        ),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    changed = False
    name = module.params['name']
    state = module.params['state']
    node = module.params['node']
    force = module.params['force']
    timeout = module.params['timeout']
    resource = module.params['resource_options']

    if state == 'present':
        if name == None:
            result['msg'] = "Must specify a resource name"
            module.fail_json(**result)
        else:
            rsrc = get_resource(module, name)
            if rsrc['msg'] != '':
                result['resource'] = rsrc['msg']
                module.exit_json(**result)
            else:
                result = create_resource(module, name, resources)
                module.exit_json(**result)
    if state == 'updated':
        if name == None:
            result['msg'] = "Must specify a resource name"
            module.fail_json(**result)
        else:
            rsrc = get_resource(module, name)
            if rsrc['msg'] == '':
                result['error'] = rsrc['Resource does not exist to update.']
                module.fail_json(**result)
            else:
                result = update_resource(module, name, resources)
                module.exit_json(**result)
    if state == 'absent':
        if name == None:
            result['msg'] = "Must specify a resource name"
            module.fail_json(**result)
        else:
            rsrc = get_resource(module, name)
            if rsrc['msg'] == '':
                result['changed'] = False
                module.exit_json(**result)
            else:
                cmd = "pcs resource delete %s" % name
                rc, out, err = module.run_command(cmd)
                if rc != 0:
                    result['output'] = out
                    result['error'] = err
                    module.fail_json(**result)
                else:
                    result['changed'] = True
                    module.exit_json(**result)

if __name__ == '__main__':
    main()
