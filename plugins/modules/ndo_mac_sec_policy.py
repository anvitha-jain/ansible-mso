#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Anvitha Jain (@anvjain) <anvjain@cisco.com>

# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import copy

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}

DOCUMENTATION = r"""
---
module: ndo_mac_sec_policy
short_description: Manage MACSec Policies on Cisco Nexus Dashboard Orchestrator (NDO).
description:
- Manage MACSec Policies on Cisco Nexus Dashboard Orchestrator (NDO).
- This module is only supported on ND v3.1 (NDO v4.3) and later.
author:
- Anvitha Jain (@anvjain)
options:
  template:
    description:
    - The name of the template.
    - The template must be a fabric policy template.
    type: str
    required: true
  mac_sec_policy:
    description:
    - The name of the MACSec Policy.
    type: str
    aliases: [ name ]
  mac_sec_policy_uuid:
    description:
    - The uuid of the MACSec Policy.
    - This parameter is required when the O(mac_sec_policy) needs to be updated.
    type: str
    aliases: [ uuid ]
  description:
    description:
    - The description of the MACSec Policy.
    type: str
  admin_state:
    description:
    - The administrative state of the MACSec Policy. (Enables or disables the policy)
    - The default value is enabled.
    type: str
    choices: [ enabled, disabled ]
  type:
    description:
    - The type of the interfaces this policy will be applied to.
    type: str
    choices: [ fabric, access ]
    default: fabric
  cipher_suite:
    description:
    - The cipher suite to be used for encryption.
    - The default value is 256_gcm_aes_xpn.
    type: str
    choices: [ 128_gcm_aes, 128_gcm_aes_xpn, 256_gcm_aes, 256_gcm_aes_xpn ]
  window_size:
    description:
    - The window size for the MACSec Policy.
    - The value must be between 0 and 4294967295.
    - The default value is 0.
    type: int
  security_policy:
    description:
    - The security policy to allow trafic on the link for the MACSec Policy.
    - The default value is should_secure.
    type: str
    choices: [ should_secure, must_secure ]
  sak_expiry_time:
    description:
    - The expiry time for the Security Association Key (SAK) for the MACSec Policy.
    - The value must be 0 or between 60 and 2592000.
    - The default value is 0.
    type: int
  confidentiality_offset:
    description:
    - The confidentiality offset for the MACSec Policy.
    type: int
    choices: [0, 30, 50]
    default: 0
  key_server_priority:
    description:
    - The key server priority for the MACSec Policy.
    - The value must be between 0 and 255.
    - The default value is 0.
    type: int
  mac_sec_key:
    description:
    - List of the MACSec Keys.
    type: list
    elements: dict
    suboptions:
      key_name:
        description:
        - The name of the MACSec Key.
        - Key Name has to be Hex chars [0-9a-fA-F]
        type: str
        required: true
      psk:
        description:
        - The Pre-Shared Key (PSK) for the MACSec Key.
        - PSK has to be 64 chars long.
        - PSK has to be Hex chars [0-9a-fA-F]
        type: str
        required: true
      start_time:
        description:
        - The start time for the MACSec Key.
        - The date time format - YYYY-MM-DD HH:MM:SS or 'now'
        - The default value is now.
        type: str
      end_time:
        description:
        - The end time for the MACSec Key.
        - The date time format - YYYY-MM-DD HH:MM:SS or 'infinite'
        - The default value is infinite.
        type: str
  state:
    description:
    - Use C(absent) for removing.
    - Use C(query) for listing an object or multiple objects.
    - Use C(present) for creating or updating.
    type: str
    choices: [ absent, query, present ]
    default: query
extends_documentation_fragment: cisco.mso.modules
"""

EXAMPLES = r"""
- name: Create a new MACSec Policy
  cisco.mso.ndo_mac_sec_policy:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: ansible_test_template
    mac_sec_policy: ansible_test_mac_sec_policy
    description: "Ansible Test MACSec Policy"
    state: present

- name: Query a MACSec Policy
  cisco.mso.ndo_mac_sec_policy:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: ansible_test_template
    mac_sec_policy: ansible_test_mac_sec_policy
    state: query
  register: query_one

- name: Query all MACSec Policies
  cisco.mso.ndo_mac_sec_policy:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    state: query
  register: query_all

- name: Delete a MACSec Policy
  cisco.mso.ndo_mac_sec_policy:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    template: ansible_test_template
    mac_sec_policy: ansible_test_mac_sec_policy
    state: absent
"""

RETURN = r"""
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec
from ansible_collections.cisco.mso.plugins.module_utils.template import MSOTemplate, KVPair
from ansible_collections.cisco.mso.plugins.module_utils.constants import NDO_CIPHER_SUITE_MAP, NDO_SECURITY_POLICY_MAP


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        dict(
            template=dict(type="str", required=True),
            mac_sec_policy=dict(type="str", aliases=["name"]),
            mac_sec_policy_uuid=dict(type="str", aliases=["uuid"]),
            description=dict(type="str"),
            admin_state=dict(type="str", choices=["enabled", "disabled"]),
            type=dict(type="str", choices=["fabric", "access"], default="fabric"),
            cipher_suite=dict(type="str", choices=["128_gcm_aes", "128_gcm_aes_xpn", "256_gcm_aes", "256_gcm_aes_xpn"]),
            window_size=dict(type="int"),
            security_policy=dict(type="str", choices=["should_secure", "must_secure"]),
            sak_expiry_time=dict(type="int"),
            confidentiality_offset=dict(type="int", choices=[0, 30, 50], default=0),
            key_server_priority=dict(type="int"),
            mac_sec_key=dict(
                type="list",
                elements="dict",
                options=dict(
                    key_name=dict(type="str", required=True),
                    psk=dict(type="str", required=True),
                    start_time=dict(type="str"),
                    end_time=dict(type="str"),
                ),
            ),
            state=dict(type="str", choices=["absent", "query", "present"], default="query"),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "present", ["mac_sec_policy"]],
            ["state", "absent", ["mac_sec_policy"]],
        ]
    )

    mso = MSOModule(module)
    mso.stdout = str(" ANVITHA ")

    template = module.params.get("template")
    mac_sec_policy = module.params.get("mac_sec_policy")
    mac_sec_policy_uuid = module.params.get("mac_sec_policy_uuid")
    description = module.params.get("description")
    admin_state = module.params.get("admin_state")
    type = module.params.get("type")
    cipher_suite = module.params.get("cipher_suite")
    window_size = module.params.get("window_size")
    security_policy = module.params.get("security_policy")
    sak_expiry_time = module.params.get("sak_expiry_time")
    confidentiality_offset = "offset" + str(module.params.get("confidentiality_offset"))
    key_server_priority = module.params.get("key_server_priority")
    mac_sec_keys = module.params.get("mac_sec_key")
    state = module.params.get("state")

    ops = []
    match = None

    mso_template = MSOTemplate(mso, "fabric_policy", template)
    mso_template.validate_template("fabricPolicy")

    path = "/fabricPolicyTemplate/template/macsecPolicies"

    existing_mac_sec_policies = mso_template.template.get("fabricPolicyTemplate", {}).get("template", {}).get("macsecPolicies", [])
    mso.stdout += str("\n existing_mac_sec_policies ") + str(existing_mac_sec_policies)
    if mac_sec_policy:
        object_description = "MACSec Policy"
        if mac_sec_policy_uuid:
            match = mso_template.get_object_by_uuid(object_description, existing_mac_sec_policies, mac_sec_policy_uuid)
        else:
            kv_list = [KVPair("name", mac_sec_policy)]
            match = mso_template.get_object_by_key_value_pairs(object_description, existing_mac_sec_policies, kv_list)
        if match:
            mso.existing = mso.previous = copy.deepcopy(match.details)
    else:
        mso.existing = mso.previous = existing_mac_sec_policies

    if state == "present":

        mso.existing = {}
        mso.stdout += str("\n match ") + str(match)

        if match:

            if mac_sec_policy and match.details.get("name") != mac_sec_policy:
                ops.append(dict(op="replace", path="{0}/{1}/name".format(path, match.index), value=mac_sec_policy))
                match.details["name"] = mac_sec_policy

            if description and match.details.get("description") != description:
                ops.append(dict(op="replace", path="{0}/{1}/description".format(path, match.index), value=description))
                match.details["description"] = description

            if admin_state and match.details.get("adminState") != admin_state:
                ops.append(dict(op="replace", path="{0}/{1}/adminState".format(path, match.index), value=admin_state))
                match.details["adminState"] = admin_state

            if type and match.details.get("type") != type:
                ops.append(dict(op="replace", path="{0}/{1}/type".format(path, match.index), value=type))
                match.details["type"] = type

            if cipher_suite and match.details.get("macsecParams")["cipherSuite"] != cipher_suite:
                ops.append(dict(op="replace", path="{0}/{1}/macsecParams/cipherSuite".format(path, match.index), value=NDO_CIPHER_SUITE_MAP.get(cipher_suite)))
                match.details["macsecParams"]["cipherSuite"] = NDO_CIPHER_SUITE_MAP.get(cipher_suite)

            if window_size and match.details.get("macsecParams")["windowSize"] != window_size:
                ops.append(dict(op="replace", path="{0}/{1}/macsecParams/windowSize".format(path, match.index), value=window_size))
                match.details["macsecParams"]["windowSize"] = window_size

            if security_policy and match.details.get("macsecParams")["securityPol"] != security_policy:
                ops.append(dict(op="replace", path="{0}/{1}/macsecParams/securityPol".format(path, match.index), value=NDO_SECURITY_POLICY_MAP.get(security_policy)))
                match.details["macsecParams"]["securityPol"] = NDO_SECURITY_POLICY_MAP.get(security_policy)

            if sak_expiry_time and match.details.get("macsecParams")["sakExpiryTime"] != sak_expiry_time:
                ops.append(dict(op="replace", path="{0}/{1}/macsecParams/sakExpiryTime".format(path, match.index), value=sak_expiry_time))
                match.details["macsecParams"]["sakExpiryTime"] = sak_expiry_time

            if type == "access":
                mso.stdout += ("\n IN IF access")
                if confidentiality_offset and match.details.get("macsecParams")["confOffSet"] != confidentiality_offset:
                    ops.append(dict(op="replace", path="{0}/{1}/macsecParams/confOffSet".format(path, match.index), value=confidentiality_offset))
                    match.details["macsecParams"]["confOffSet"] = confidentiality_offset

                if key_server_priority and match.details.get("macsecParams")["keyServerPrio"] != key_server_priority:
                    ops.append(dict(op="replace", path="{0}/{1}/macsecParams/keyServerPrio".format(path, match.index), value=key_server_priority))
                    match.details["macsecParams"]["keyServerPrio"] = key_server_priority

                # if mac_sec_keys:
                #     mac_sec_keys_list = []
                #     for mac_sec_key in mac_sec_keys:
                #         # if mac_sec_key.get("key_name") and match.details.get("macsecParams")["macsecKeys"]:

                #         keyname = mac_sec_key.get("key_name")
                #         psk = mac_sec_key.get("psk")
                #         start = mac_sec_key.get("start_time")
                #         end = mac_sec_key.get("end_time")

                #         mac_sec_keys_list.append(
                #             dict(
                #                 keyname=keyname,
                #                 psk=psk,
                #                 start=start,
                #                 end=end,
                #             )
                #         )
                #     ops.append(dict(op="replace", path="{0}/{1}/macsecKeys".format(path, match.index), value=mac_sec_keys_list))
                #     match.details["macsecParams"]["macsecKeys"] = mac_sec_keys_list
                

            mso.sanitize(match.details)

        else:
            mac_sec_param_map ={}

            payload = {"name": mac_sec_policy, "templateId": mso_template.template.get("templateId"), "schemaId": mso_template.template.get("schemaId")}
            payload["adminState"] = admin_state
            payload["type"] = type

            if description:
                payload["description"] = description

            if cipher_suite:
                mac_sec_param_map["cipherSuite"] = NDO_CIPHER_SUITE_MAP.get(cipher_suite)
            if window_size:
                mac_sec_param_map["windowSize"] = window_size
            if security_policy:
                mac_sec_param_map["securityPol"] = NDO_SECURITY_POLICY_MAP.get(security_policy)
            if sak_expiry_time:
                mac_sec_param_map["sakExpiryTime"] = sak_expiry_time

            if type == "access":
                if confidentiality_offset:
                    mac_sec_param_map["confOffSet"] = confidentiality_offset
                if key_server_priority:
                    mac_sec_param_map["keyServerPrio"] = key_server_priority

            payload["macsecParams"] = mac_sec_param_map

            mac_sec_keys_list = []
            if mac_sec_keys:
                for mac_sec_key in mac_sec_keys:
                    keyname = mac_sec_key.get("key_name")
                    psk = mac_sec_key.get("psk")
                    start = mac_sec_key.get("start_time")
                    end = mac_sec_key.get("end_time")

                    mac_sec_keys_list.append(
                        dict(
                            keyname=keyname,
                            psk=psk,
                            start=start,
                            end=end,
                        )
                    )
                payload["macsecKeys"] = mac_sec_keys_list


            ops.append(dict(op="add", path="{0}/-".format(path), value=copy.deepcopy(payload)))

            mso.sanitize(payload)

        mso.existing = mso.proposed

    elif state == "absent":
        if match:
            ops.append(dict(op="remove", path="{0}/{1}".format(path, match.index)))
        mso.existing = {}

    if not module.check_mode and ops:
        mso.request(mso_template.template_path, method="PATCH", data=ops)
        mso.stdout += str("\n\n ops ") + str(ops) + str("\n request ") + str(mso_template.template_path)

    mso.exit_json()


if __name__ == "__main__":
    main()
