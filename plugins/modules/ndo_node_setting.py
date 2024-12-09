#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Sabari Jaganathan (@sajagana) <sajagana@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}

DOCUMENTATION = r"""
---
module: ndo_node_setting
short_description: Manage Fabric Policy Node Settings on Cisco Nexus Dashboard Orchestrator (NDO).
description:
- Manage Fabric Policy Node Settings on Cisco Nexus Dashboard Orchestrator (NDO).
- This module is only supported on ND v3.1 (NDO v4.3) and later.
author:
- Sabari Jaganathan (@sajagana)
options:
  template:
    description:
    - The name of the template.
    - The template must be a Fabric Policy template.
    type: str
    required: true
    aliases: [ fabric_template ]
  name:
    description:
    - The name of the Fabric Policy Node Settings.
    type: str
    aliases: [ node_setting ]
  uuid:
    description:
    - The UUID of the Fabric Policy Node Settings.
    - This parameter is required when the O(name) needs to be updated.
    type: str
    aliases: [ node_setting_uuid ]
  description:
    description:
    - The description of the Fabric Policy Node Settings.
    type: str
  synce:
    description:
    - The Synchronous Ethernet (SyncE) Interface Policy of the Fabric Policy Node Settings.
    type: dict
    suboptions:
      state:
        description:
        - Use C(enabled) to configure the SyncE Interface Policy.
        - Both O(synce.admin_state) and O(synce.quality_level) are required when the state is C(enabled).
        - Use C(disabled) to remove the SyncE Interface Policy.
        type: str
        choices: [ enabled, disabled ]
      admin_state:
        description:
        - The administrative state of the SyncE Interface Policy.
        type: str
        choices: [ enabled, disabled ]
      quality_level:
        description:
        - The quality level option of the SyncE Interface Policy.
        type: str
        choices: [ option_1, option_2_generation_1, option_2_generation_2 ]
  ptp:
    description:
    - The Precision Time Protocol (PTP) of the Fabric Policy Node Settings.
    type: dict
    suboptions:
      state:
        description:
        - Use C(enabled) to configure the PTP Settings.
        - Both O(ptp.node_domain) and O(ptp.priority_2) are required when the state is C(enabled).
        - Use C(disabled) to remove the PTP Settings.
        type: str
        choices: [ enabled, disabled ]
      node_domain:
        description:
        - The node domain number of the PTP Settings.
        - The value must be between 24 and 43.
        type: int
      priority_2:
        description:
        - The value that is used when advertising this clock.
        - The value must be between 0 and 255, lower values are prioritized.
        - The PTP priority 1 is set to a fixed value of 128.
        type: int
  state:
    description:
    - Use C(absent) for removing.
    - Use C(query) for listing an object or multiple objects.
    - Use C(present) for creating or updating.
    type: str
    choices: [ absent, query, present ]
    default: query
notes:
- The O(template) must exist before using this module in your playbook.
  Use M(cisco.mso.ndo_template) to create the Fabric Policy template.
extends_documentation_fragment: cisco.mso.modules
"""

EXAMPLES = r"""
- name: Create a new Fabric Policy Node Setting
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    name: ns1
    state: present
  register: create_ns1

- name: Add SyncE config to the existing Fabric Policy Node Setting using Name
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    name: ns1
    synce:
      admin_state: enabled
      quality_level: option_2_generation_1
    state: present

- name: Add PTP config to the existing Fabric Policy Node Setting using UUID
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    uuid: "{{ create_ns1.current.uuid }}"
    name: ns1_updated
    ptp:
      node_domain: 25
      priority_2: 100
    state: present

- name: Query an existing Fabric Policy Node Setting using UUID
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    uuid: "{{ create_ns1.current.uuid }}"
    state: query
  register: query_with_uuid

- name: Query an existing Fabric Policy Node Setting using Name
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    name: ns1_updated
    state: query
  register: query_with_name

- name: Query all Fabric Policy Node Setting
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    state: query
  register: query_all

- name: Delete an existing Fabric Policy Node Setting using UUID
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    uuid: "{{ create_ns1.current.uuid }}"
    state: absent

- name: Delete an existing Fabric Policy Node Setting using Name
  cisco.mso.ndo_node_setting:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: fabric_template
    name: ns1_updated
    state: absent
"""

RETURN = r"""
"""


import copy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec
from ansible_collections.cisco.mso.plugins.module_utils.template import MSOTemplate
from ansible_collections.cisco.mso.plugins.module_utils.constants import SYNC_E_QUALITY_LEVEL_OPTION
from ansible_collections.cisco.mso.plugins.module_utils.utils import append_update_ops_data


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        template=dict(type="str", required=True, aliases=["fabric_template"]),
        name=dict(type="str", aliases=["node_setting"]),
        uuid=dict(type="str", aliases=["node_setting_uuid"]),
        description=dict(type="str"),
        synce=dict(
            type="dict",
            options=dict(
                state=dict(type="str", choices=["enabled", "disabled"]),
                admin_state=dict(type="str", choices=["enabled", "disabled"]),
                quality_level=dict(type="str", choices=list(SYNC_E_QUALITY_LEVEL_OPTION)),
            ),
        ),
        ptp=dict(
            type="dict",
            options=dict(
                state=dict(type="str", choices=["enabled", "disabled"]),
                node_domain=dict(type="int"),
                priority_2=dict(type="int"),
            ),
        ),
        state=dict(type="str", default="query", choices=["absent", "query", "present"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "absent", ["name", "uuid"], True],
            ["state", "present", ["name", "uuid"], True],
        ],
    )

    mso = MSOModule(module)

    template = module.params.get("template")
    name = module.params.get("name")
    uuid = module.params.get("uuid")
    description = module.params.get("description")
    synce = module.params.get("synce")
    ptp = module.params.get("ptp")
    state = module.params.get("state")

    mso_template = MSOTemplate(mso, "fabric_policy", template)
    mso_template.validate_template("fabricPolicy")

    node_setting = mso_template.get_node_settings_object(uuid, name)

    if (uuid or name) and node_setting:
        mso.existing = mso.previous = copy.deepcopy(node_setting.details)  # Query a specific object
    elif node_setting:
        mso.existing = node_setting  # Query all objects

    if state != "query":
        node_setting_path = "/fabricPolicyTemplate/template/nodePolicyGroups/{0}".format(node_setting.index if node_setting else "-")

    ops = []
    if state == "present":
        if mso.existing:
            proposed_payload = copy.deepcopy(mso.existing)
            replace_data = dict()
            remove_data = list()

            replace_data["name"] = name
            replace_data["description"] = description

            if synce is not None:
                if synce.get("state") == "disabled" and proposed_payload.get("synce"):
                    remove_data.append("synce")
                else:
                    replace_data["synce"] = dict()
                    replace_data[("synce", "adminState")] = synce.get("admin_state")
                    replace_data[("synce", "qlOption")] = SYNC_E_QUALITY_LEVEL_OPTION.get(synce.get("quality_level"))

            if ptp is not None:
                if ptp.get("state") == "disabled" and proposed_payload.get("ptp"):
                    remove_data.append("ptp")
                else:
                    replace_data["ptp"] = dict()

                    # Add the Priority 1 fixed value 128 to the PTP settings during initialization
                    replace_data[("ptp", "prio1")] = 128
                    replace_data[("ptp", "domain")] = ptp.get("node_domain")
                    replace_data[("ptp", "prio2")] = ptp.get("priority_2")

            append_update_ops_data(ops, proposed_payload, node_setting_path, replace_data, remove_data)
            mso.sanitize(proposed_payload)
        else:
            payload = dict(name=name)

            if description:
                payload["description"] = description

            if synce is not None:
                synce_map = dict()
                if synce.get("admin_state"):
                    synce_map["adminState"] = synce.get("admin_state")

                if synce.get("quality_level"):
                    synce_map["qlOption"] = SYNC_E_QUALITY_LEVEL_OPTION.get(synce.get("quality_level"))

                if synce_map:
                    payload["synce"] = synce_map

            if ptp is not None:
                ptp_map = dict()
                if ptp.get("node_domain"):
                    ptp_map["domain"] = ptp.get("node_domain")

                if ptp.get("priority_2") is not None:
                    ptp_map["prio2"] = ptp.get("priority_2")

                if ptp_map:
                    # Add the Priority 1 fixed value 128 to the PTP settings during initialization
                    ptp_map["prio1"] = 128
                    payload["ptp"] = ptp_map

            ops.append(dict(op="add", path=node_setting_path, value=copy.deepcopy(payload)))

            mso.sanitize(payload)
    elif state == "absent":
        if mso.existing:
            ops.append(dict(op="remove", path=node_setting_path))

    if not module.check_mode and ops:
        mso_template.template = mso.request(mso_template.template_path, method="PATCH", data=ops)
        node_setting = mso_template.get_node_settings_object(uuid, name)
        if node_setting:
            mso.existing = node_setting.details  # When the state is present
        else:
            mso.existing = {}  # When the state is absent
    elif module.check_mode and state != "query":  # When the state is present/absent with check mode
        mso.existing = mso.proposed if state == "present" else {}

    mso.exit_json()


if __name__ == "__main__":
    main()
