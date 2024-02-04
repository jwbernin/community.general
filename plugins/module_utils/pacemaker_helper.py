# -*- coding: utf-8 -*-
# Copyright (c) 2024, John Berninger <john.berninger@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import re

from ansible.module_utils.parsing.convert_bool import boolean
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt as fmt


@fmt.unpack_args
def _values_fmt(values, value_types):
    result = []
    for value, value_type in zip(values, value_types):
        if value_type == 'bool':
            value = 'true' if boolean(value) else 'false'
        result.extend(['--type', '{0}'.format(value_type), '--set', '{0}'.format(value)])
    return result

def _count_indentation(line):
    match = re.search(r"^\s*", s)
    return 0 if not match else match.end()

def _add_ansibilized_section(resource_string_array, current_depth):
    line = resource_string_array[0]
    remainder = resource_string_array[1:]
    next_depth = _count_indentation(resource_string_array[1])

    assert line.startswith(' '*current_depth)
    name, value = line.split(':')
    if len(value) == 0:
        return {name: _add_ansibilized_section(remainder, next_depth) }
    else:
        return {name: {'name':value,'value': _add_ansibilized_section(remainder, next_depth) }

def ansibilize_resource(resource_string):
    return _add_ansibilized_section(resource_string.split('\n'), 0)


