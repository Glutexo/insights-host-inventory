from unittest import TestCase

from test_fixtures import _assert_keys_overridable
from test_fixtures import _merge_dict
from test_fixtures import _merge_key
from test_fixtures import _merge_list
from test_fixtures import _merge_value
from test_fixtures import SYSTEM_PROFILE
from test_fixtures import system_profile


class MergeValueTestCase(TestCase):
    def test_simple_value(self):
        original = "eth0"
        override = "eth1"
        merged = _merge_value(original, override)
        self.assertEqual(override, merged)

    def test_wrong_type(self):
        original = 0
        override = "0"
        with self.assertRaises(TypeError):
            _merge_value(original, override)

    def test_merge_dict(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2}
        override = {"number_of_cpus": 2}
        merged = _merge_value(original, override)
        expected = {**original, **override}
        self.assertEqual(expected, merged)

    def test_merge_list(self):
        original = ["eth0", "eth1"]
        override = {0: "eth2"}
        merged = _merge_value(original, override)
        expected = ["eth2", "eth1"]
        self.assertEqual(expected, merged)

    def test_replace_list(self):
        original = ["eth0", "eth1"]
        override = ["eth2"]
        merged = _merge_value(original, override)
        self.assertEqual(override, merged)


class MergeKeyTestCase(TestCase):
    def test_dict_not_overridden(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2}
        override = {"number_of_sockets": 3}
        merged = _merge_key(original, override, "number_of_cpus")
        self.assertEqual(original["number_of_cpus"], merged)

    def test_list_not_overriden(self):
        original = ["eth0", "eth1"]
        override = {1: "eth2"}
        merged = _merge_key(original, override, 0)
        self.assertEqual(original[0], merged)

    def test_dict_overridden(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2}
        override = {"number_of_sockets": 3}
        merged = _merge_key(original, override, "number_of_sockets")
        self.assertEqual(override["number_of_sockets"], merged)

    def test_list_overridden(self):
        original = ["eth0", "eth1"]
        override = {1: "eth2"}
        merged = _merge_key(original, override, 1)
        self.assertEqual(override[1], merged)


class AssertKeysOverridable(TestCase):
    def test_all_overridable(self):
        keys = ("number_of_cpus", "number_of_sockets")
        _assert_keys_overridable(keys, keys)
        self.assertTrue(True)

    def test_some_overridable(self):
        original = ("number_of_cpus", "number_of_sockets")
        override = ("number_of_sockets",)
        _assert_keys_overridable(original, override)
        self.assertTrue(True)

    def test_not_overridable(self):
        original = ("number_of_cpus", "number_of_sockets")
        override = ("cores_per_socket",)
        with self.assertRaises(KeyError):
            _assert_keys_overridable(original, override)


class MergeDictTestCase(TestCase):
    def test_single__value(self):
        original = {"number_of_cpus": 1}
        override = {"number_of_cpus": 2}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_one_value(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2}
        override = {"number_of_cpus": 2}
        merged = _merge_dict(original, override)
        expected = {**original, **override}
        self.assertEqual(expected, merged)

    def test_more_values(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2, "cores_per_socket": 4}
        override = {"number_of_cpus": 2, "number_of_sockets": 3}
        merged = _merge_dict(original, override)
        expected = {**original, **override}
        self.assertEqual(expected, merged)

    def test_wrong_key(self):
        original = {"number_of_cpus": 1}
        override = {"number_of_sockets": 3}
        with self.assertRaises(KeyError):
            _merge_dict(original, override)

    def test_wrong_type(self):
        original = {"number_of_cpus": 1}
        override = {"number_of_cpus": "2"}
        with self.assertRaises(TypeError):
            _merge_dict(original, override)

    def test_nested_dict_single_value(self):
        original = {"network_interface": {"state": "UP"}}
        override = {"network_interface": {"state": "DOWN"}}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_nested_dict_one_value(self):
        original = {"network_interface": {"state": "UP", "name": "eth0"}}
        override = {"network_interface": {"state": "DOWN"}}
        merged = _merge_dict(original, override)
        expected = {"network_interface": {**original["network_interface"], **override["network_interface"]}}
        self.assertEqual(expected, merged)

    def test_nested_dict_more_values(self):
        original = {
            "network_interface": {"state": "UP", "type": "loopback", "name": "eth0"},
            "disk_device": {"device": "/dev/sdb1", "type": "ext3"},
        }
        override = {"network_interface": {"state": "DOWN", "name": "eth1"}, "disk_device": {"device": "/dev/sdb2"}}
        merged = _merge_dict(original, override)
        expected = {
            "network_interface": {**original["network_interface"], **override["network_interface"]},
            "disk_device": {**original["disk_device"], **override["disk_device"]},
        }
        self.assertEqual(expected, merged)

    def test_nested_dict_wrong_key(self):
        original = {"network_interface": {"state": "UP"}}
        override = {"network_interface": {"name": "eth0"}}
        with self.assertRaises(KeyError):
            _merge_dict(original, override)

    def test_nested_dict_wrong_type(self):
        original = {"network_interface": {"mtu": 1500}}
        override = {"network_interface": {"mtu": "1500"}}
        with self.assertRaises(TypeError):
            _merge_dict(original, override)

    def test_deep_nested_dict_single_key(self):
        original = {"network_interfaces": {"eth0": {"state": "UP"}}}
        override = {"network_interfaces": {"eth0": {"state": "DOWN"}}}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_deep_nested_dict_more_keys(self):
        original = {"network_interfaces": {"eth0": {"state": "UP"}, "eth1": {"state": "UP"}}}
        override = {"network_interfaces": {"eth0": {"state": "DOWN"}}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": {**original["network_interfaces"], **override["network_interfaces"]}}
        self.assertEqual(expected, merged)

    def test_nested_list_single_value_by_list(self):
        original = {"network_interfaces": ["eth0"]}
        override = {"network_interfaces": ["eth1"]}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_nested_list_single_value_by_dict(self):
        original = {"network_interfaces": ["eth0"]}
        override = {"network_interfaces": {0: "eth1"}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": ["eth1"]}
        self.assertEqual(expected, merged)

    def test_nested_list_one_value(self):
        original = {"network_interfaces": ["eth0", "eth1"]}
        override = {"network_interfaces": {0: "eth2"}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": ["eth2", "eth1"]}
        self.assertEqual(expected, merged)

    def test_nested_list_more_values(self):
        original = {"network_interfaces": ["eth0", "eth1"], "disk_devices": ["/dev/sdb1"]}
        override = {"network_interfaces": {0: "eth2", 1: "eth3"}, "disk_devices": {0: "/dev/sdb2"}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": ["eth2", "eth3"], "disk_devices": ["/dev/sdb2"]}
        self.assertEqual(expected, merged)

    def test_nested_list_wrong_key(self):
        original = {"network_interfaces": ["eth0"]}
        override = {"network_interfaces": {1: "eth1"}}
        with self.assertRaises(KeyError):
            _merge_dict(original, override)

    def test_nested_list_wrong_type(self):
        original = {"network_interfaces": [0, 1]}
        override = {"network_interfaces": {0: "0"}}
        with self.assertRaises(TypeError):
            _merge_dict(original, override)

    def test_nested_dict_in_list(self):
        original = {"network_interfaces": [{"state": "UP", "name": "eth0"}, {"state": "UP", "name": "eth1"}]}
        override = {"network_interfaces": {0: {"state": "DOWN"}}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": [{"state": "DOWN", "name": "eth0"}, {"state": "UP", "name": "eth1"}]}
        self.assertEqual(expected, merged)

    def test_nested_list_in_dict(self):
        original = {"network_interfaces": {"UP": ["eth0", "eth1"], "DOWN": ["eth2", "eth3"]}}
        override = {"network_interfaces": {"UP": {0: "eth4"}}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": {"UP": ["eth4", "eth1"], "DOWN": ["eth2", "eth3"]}}
        self.assertEqual(expected, merged)


class MergeListTestCase(TestCase):
    def test_wrong_key_type(self):
        original = ["eth0"]
        override = {"0": "eth1"}
        with self.assertRaises(KeyError):
            _merge_list(original, override)

    def test_single_simple_value(self):
        original = ["eth0"]
        override = {0: "eth1"}
        merged = _merge_list(original, override)
        expected = ["eth1"]
        self.assertEqual(expected, merged)

    def test_one_value(self):
        original = ["eth0", "eth1"]
        override = {0: "eth2"}
        merged = _merge_list(original, override)
        expected = ["eth2", "eth1"]
        self.assertEqual(expected, merged)

    def test_more_values(self):
        original = ["eth0", "eth1", "eth2"]
        override = {0: "eth3", 1: "eth4"}
        merged = _merge_list(original, override)
        expected = ["eth3", "eth4", "eth2"]
        self.assertEqual(expected, merged)

    def test_wrong_key(self):
        original = ["eth0"]
        override = {1: "eth4"}
        with self.assertRaises(KeyError):
            _merge_list(original, override)

    def test_wrong_type(self):
        original = [0]
        override = {0: "0"}
        with self.assertRaises(TypeError):
            _merge_list(original, override)

    def test_nested_list_single_value_by_list(self):
        original = [["eth0"]]
        override = {0: ["eth1"]}
        merged = _merge_list(original, override)
        expected = [["eth1"]]
        self.assertEqual(expected, merged)

    def test_nested_list_single_value_by_dict(self):
        original = [["eth0"]]
        override = {0: {0: "eth1"}}
        merged = _merge_list(original, override)
        expected = [["eth1"]]
        self.assertEqual(expected, merged)

    def test_nested_list_one_value(self):
        original = [["eth0", "eth1"]]
        override = {0: {0: "eth2"}}
        merged = _merge_list(original, override)
        expected = [["eth2", "eth1"]]
        self.assertEqual(expected, merged)

    def test_nested_list_more_values(self):
        original = [["eth0", "eth1", "eth2"], ["wlan0", "wlan1"]]
        override = {0: {0: "eth3"}, 1: {0: "wlan2"}}
        merged = _merge_list(original, override)
        expected = [["eth3", "eth1", "eth2"], ["wlan2", "wlan1"]]
        self.assertEqual(expected, merged)

    def test_nested_list_wrong_key(self):
        original = [[0]]
        override = {0: {1: 1}}
        with self.assertRaises(KeyError):
            _merge_list(original, override)

    def test_nested_list_wrong_type(self):
        original = [[0]]
        override = {0: {0: "0"}}
        with self.assertRaises(TypeError):
            _merge_list(original, override)

    def test_nested_dict_single_value(self):
        original = [{"state": "UP"}]
        override = {0: {"state": "DOWN"}}
        merged = _merge_list(original, override)
        expected = [{"state": "DOWN"}]
        self.assertEqual(expected, merged)

    def test_nested_dict_one_value(self):
        original = [{"state": "UP", "name": "eth0"}]
        override = {0: {"state": "DOWN"}}
        merged = _merge_list(original, override)
        expected = [{"state": "DOWN", "name": "eth0"}]
        self.assertEqual(expected, merged)

    def test_nested_dict_more_values(self):
        original = [{"state": "UP", "name": "eth0"}, {"state": "UP", "name": "eth1"}]
        override = {0: {"state": "DOWN"}, 1: {"name": "eth2"}}
        merged = _merge_list(original, override)
        expected = [{"state": "DOWN", "name": "eth0"}, {"state": "UP", "name": "eth2"}]
        self.assertEqual(expected, merged)

    def test_nested_dict_wrong_key(self):
        original = [{"state": "UP"}]
        override = {0: {"name": "eth0"}}
        with self.assertRaises(KeyError):
            _merge_list(original, override)

    def test_nested_dict_wrong_type(self):
        original = [{"mtu": 1500}]
        override = {0: {"mtu": "1500"}}
        with self.assertRaises(TypeError):
            _merge_list(original, override)

    def test_deep_nested_list_single_key(self):
        original = [[["eth0"]]]
        override = {0: {0: {0: "eth1"}}}
        merged = _merge_list(original, override)
        expected = [[["eth1"]]]
        self.assertEqual(expected, merged)

    def test_deep_nested_list_more_keys(self):
        original = [[["eth0", "eth1"], ["wlan0", "wlan1"]], [["/dev/sda1", "/dev/sda2"], ["/dev/sdb1", "/dev/sdb2"]]]
        override = {0: {0: {0: "eth2", 1: "eth3"}, 1: {0: "wlan2"}}, 1: {0: {0: "/dev/sda3"}}}
        merged = _merge_list(original, override)
        expected = [[["eth2", "eth3"], ["wlan2", "wlan1"]], [["/dev/sda3", "/dev/sda2"], ["/dev/sdb1", "/dev/sdb2"]]]
        self.assertEqual(expected, merged)


class SystemProfileTestCase(TestCase):
    def test_no_overrides(self):
        profile = system_profile()
        self.assertEqual(SYSTEM_PROFILE, profile)

    def test_simple_override(self):
        override = {"number_of_cpus": 3, "number_of_sockets": 4}
        profile = system_profile(override)
        expected = {**SYSTEM_PROFILE, **override}
        self.assertEqual(expected, profile)

    def test_list_replace(self):
        override = {"installed_services": ["ssh", "cron"]}
        profile = system_profile(override)
        expected = {**SYSTEM_PROFILE, **override}
        self.assertEqual(expected, profile)

    def test_list_update(self):
        override = {"installed_services": {0: "ssh"}}
        profile = system_profile(override)
        expected = {**SYSTEM_PROFILE, **{"installed_services": ["ssh", "krb5"]}}
        self.assertEqual(expected, profile)

    def test_dict_override(self):
        override = {"installed_products": {0: {"name": "ansible"}}}
        profile = system_profile(override)
        expected = {
            **SYSTEM_PROFILE,
            **{
                "installed_products": [
                    {"name": "ansible", "id": "123", "status": "UP"},
                    {"name": "jbws", "id": "321", "status": "DOWN"},
                ]
            },
        }
        self.assertEqual(expected, profile)

    def test_invalid_root_key(self):
        override = {"system_memory_octets": 1024}
        with self.assertRaises(KeyError):
            system_profile(override)

    def test_invalid_list_key(self):
        override = {"installed_products": {2: {"name": "ansible", "id": "123", "status": "UP"}}}
        with self.assertRaises(KeyError):
            system_profile(override)

    def test_invalid_dict_key(self):
        override = {"installed_products": {0: {"vendor": "Red Hat"}}}
        with self.assertRaises(KeyError):
            system_profile(override)
