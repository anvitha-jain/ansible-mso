#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Anvitha Jain (@anvjain) <anvjain@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}

DOCUMENTATION = r"""
---
module: ndo_physical_interface
short_description: Manage physical interface on Cisco Nexus Dashboard Orchestrator (NDO).
description:
- Manage physical interface on Cisco Nexus Dashboard Orchestrator (NDO).
- This module is only supported on ND v3.1 (NDO v4.3) and later.
author:
- Anvitha Jain (@anvjain)
options:
  template:
    description:
    - The name of the template.
    - The template must be a fabric resource policy template.
    type: str
    required: true
  physical_interface:
    description:
    - The name of the physical interface.
    type: str
    aliases: [ name ]
  physical_interface_uuid:
    description:
    - The UUID of the physical interface.
    - This parameter is required when the O(physical_interface) needs to be updated.
    type: str
    aliases: [ uuid ]
  description:
    description:
    - The description of the physical interface.
    type: str
  nodes:
    description:
    - The node IDs where the physical interface policy will be deployed.
    type: list
    elements: int
  interfaces:
    description:
    - The interface names where the policy will be deployed.
    type: str
  interface_policy:  # interface_policy_properties or physical_interface_type
    description:
    - The type of the interface policy group.
    type: str
    choices: [ physical, breakout ]
  physical_policy:
    description:
    - The interface setting group policy required for physical interface setting.
    - This parameter is required when O(interface_policy) is C(physical).
    # It takes the UUID of the interface settings created in any template(it doesn't have to be local template).
    # so, check if i need template name to do a get?
    type: str
  breakout_mode:
    description:
    - The breakout mode enabled splitting of the ethernet ports.
    - This parameter is available only when O(interface_policy) is C(breakout).
    - The default value is C(4x10G).
    type: str
    choices: [ 4x10G, 4x25G, 4x100G ]
  interface_description:
    description:
    - The interface settings defined in the interface settings policy will be applied to the interfaces on the nodes you provided.
    type: list
    elements: dict
    suboptions:
      interface:
        description:
        - The interface ID.
        type: str
      # The API takes this value also mentioned in docs but not available on UI
      # node:
      #   description:
      #   - The node ID.
      #   type: int
      description:
        description:
        - The description of the interface.
        type: str
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
  Use M(cisco.mso.ndo_template) to create the Tenant template.
seealso:
- module: cisco.mso.ndo_template
extends_documentation_fragment: cisco.mso.modules
"""

EXAMPLES = r"""
- name: Create an physical interface interface_policy physical
  cisco.mso.ndo_physical_interface:
  host: mso_host
  username: admin
  password: SomeSecretPassword
  template: ansible_test_template
  physical_interface: ansible_test_physical_interface_physical
  description: "physical interface for Ansible Test"
  nodes: [101]
  interfaces: "1/1"
  interface_policy: physical
  physical_policy: ansible_test_interface_setting_policy_uuid
  state: present

- name: Query all physical interfaces
  cisco.mso.ndo_physical_interface:
  host: mso_host
  username: admin
  password: SomeSecretPassword
  template: ansible_test_template
  state: query
  register: query_all

- name: Query a specific physical interface with name
  cisco.mso.ndo_physical_interface:
  host: mso_host
  username: admin
  password: SomeSecretPassword
  template: ansible_test_template
  physical_interface: ansible_test_physical_interface_physical
  state: query
  register: query_one_name

- name: Query a specific physical interface with UUID
  cisco.mso.ndo_physical_interface:
  host: mso_host
  username: admin
  password: SomeSecretPassword
  template: ansible_test_template
  physical_interface_uuid: ansible_test_physical_interface_uuid
  state: query
  register: query_one_uuid

- name: Delete an physical interface with name
  cisco.mso.ndo_physical_interface:
  host: mso_host
  username: admin
  password: SomeSecretPassword
  template: ansible_test_template
  physical_interface: ansible_test_physical_interface_physical
  state: absent

- name: Delete an physical interface with UUID
  cisco.mso.ndo_physical_interface:
  host: mso_host
  username: admin
  password: SomeSecretPassword
  template: ansible_test_template
  physical_interface_uuid: ansible_test_physical_interface_uuid
  state: absent
"""

RETURN = r"""
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec
from ansible_collections.cisco.mso.plugins.module_utils.template import MSOTemplate, KVPair
import copy


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        dict(
            template=dict(type="str", required=True),
            physical_interface=dict(type="str", aliases=["name"]),
            physical_interface_uuid=dict(type="str", aliases=["uuid"]),
            description=dict(type="str"),
            nodes=dict(type="list", elements="int"),
            interfaces=dict(type="str"),
            interface_policy=dict(type="str", choices=["physical", "breakout"]),
            physical_policy=dict(type="str"),
            breakout_mode=dict(type="str", choices=["4x10G", "4x25G", "4x100G"]),
            interface_description=dict(
                type="list",
                elements="dict",
                options=dict(
                    interface=dict(type="str"),
                    description=dict(type="str"),
                ),
            ),
            state=dict(type="str", default="query", choices=["absent", "query", "present"]),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "present", ["physical_interface", "physical_interface_uuid", "nodes", "interfaces" ], True],
            ["state", "absent", ["physical_interface", "physical_interface_uuid"], True],
            ["interface_policy", "physical", ["physical_policy"]],
        ],

    )

    mso = MSOModule(module)

    template = module.params.get("template")
    physical_interface = module.params.get("physical_interface")
    physical_interface_uuid = module.params.get("physical_interface_uuid")
    description = module.params.get("description")
    nodes = module.params.get("nodes")
    interfaces = module.params.get("interfaces")
    interface_policy = module.params.get("interface_policy")
    physical_policy = module.params.get("physical_policy")
    breakout_mode = module.params.get("breakout_mode")
    interface_description = module.params.get("interface_description")
    state = module.params.get("state")

    ops = []
    match = None

    mso_template = MSOTemplate(mso, "fabric_resource", template)
    mso_template.validate_template("fabricResource")

    path = "/fabricResourceTemplate/template/interfaceProfiles"
    object_description = "Physical Interface Profile"

    template_info = mso_template.template.get("fabricResourceTemplate", {}).get("template", {})

    existing_interface_policies = mso_template.template.get("fabricResourceTemplate", {}).get("template", {}).get("interfaceProfiles", [])
    if physical_interface or physical_interface_uuid:
        match = mso_template.get_object_by_key_value_pairs(
            object_description,
            existing_interface_policies,
            [KVPair("uuid", physical_interface_uuid) if physical_interface_uuid else KVPair("name", physical_interface)],
        )
        if match:
            mso.existing = mso.previous = copy.deepcopy(match.details)
    else:
        mso.existing = mso.previous = existing_interface_policies

    if state == "present":
        if match:
            if physical_interface and match.details.get("name") != physical_interface:
                ops.append(dict(op="replace", path="{0}/{1}/name".format(path, match.index), value=physical_interface))
                match.details["name"] = physical_interface

            if description is not None and match.details.get("description") != description:
                ops.append(dict(op="replace", path="{0}/{1}/description".format(path, match.index), value=description))
                match.details["description"] = description

            mso.sanitize(match.details)
        else:
            payload = {
                "name": physical_interface,
                "templateId": mso_template.template.get("templateId"),
                "schemaId": mso_template.template.get("schemaId"),
                "nodes": nodes,
                "interfaces": interfaces,
            }

            if description:
                payload["description"] = description
            if interface_policy:
                payload["policyGroupType"] = interface_policy

            if interface_policy == "physical":
                if physical_policy:
                    payload["policy"] = physical_policy
                else:
                    mso.fail("The physical_policy parameter is required when interface_policy is physical.")

            # if interface_policy == "breakout":
            if breakout_mode:
                payload["breakoutMode"] = breakout_mode

            if interface_description:
                interface_list = []
                for interface in interface_description:
                    interface_dict = {
                        "interfaceId": interface.get("interface"),
                    }
                    if interface.get("description"):
                        interface_dict["description"] = interface.get("description")
                    interface_list.append(interface_dict)
                payload["interfaceDescriptions"] = interface_list
                    

            ops.append(dict(op="add", path="{0}/-".format(path), value=copy.deepcopy(payload)))

            mso.sanitize(payload)

        mso.existing = mso.proposed

    elif state == "absent":
        if match:
            ops.append(dict(op="remove", path="{0}/{1}".format(path, match.index)))

    if not module.check_mode and ops:
        response = mso.request(mso_template.template_path, method="PATCH", data=ops)
        interface_policies = response.get("fabricResourceTemplate", {}).get("template", {}).get("interfaceProfiles", [])
        match = mso_template.get_object_by_key_value_pairs(
            object_description,
            interface_policies,
            [KVPair("uuid", physical_interface_uuid) if physical_interface_uuid else KVPair("name", physical_interface)],
        )
        if match:
            mso.existing = match.details
        else:
            mso.existing = {}
    elif module.check_mode and state != "query":
        mso.existing = mso.proposed if state == "present" else {}

    mso.exit_json()


if __name__ == "__main__":
    main()

