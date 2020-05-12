from unittest import TestCase

from test_fixtures import _merge_dict


class MergeDictTestCase(TestCase):
    def test_merge_dict_single_simple_value(self):
        original = {"number_of_cpus": 1}
        override = {"number_of_cpus": 2}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_merge_dict_one_value(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2}
        override = {"number_of_cpus": 2}
        merged = _merge_dict(original, override)
        expected = {**original, **override}
        self.assertEqual(expected, merged)

    def test_merge_dict_more_values(self):
        original = {"number_of_cpus": 1, "number_of_sockets": 2, "cores_per_socket": 4}
        override = {"number_of_cpus": 2, "number_of_sockets": 3}
        merged = _merge_dict(original, override)
        expected = {**original, **override}
        self.assertEqual(expected, merged)

    def test_merge_dict_wrong_key(self):
        original = {"number_of_cpus": 1}
        override = {"number_of_sockets": 3}
        with self.assertRaises(KeyError):
            _merge_dict(original, override)

    def test_merge_dict_wrong_type(self):
        original = {"number_of_cpus": 1}
        override = {"number_of_cpus": "2"}
        with self.assertRaises(TypeError):
            _merge_dict(original, override)

    def test_merge_dict_nested_dict_single_value(self):
        original = {"network_interface": {"state": "UP"}}
        override = {"network_interface": {"state": "DOWN"}}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_merge_dict_nested_dict_one_value(self):
        original = {"network_interface": {"state": "UP", "name": "eth0"}}
        override = {"network_interface": {"state": "DOWN"}}
        expected = {"network_interface": {**original["network_interface"], **override["network_interface"]}}
        merged = _merge_dict(original, override)
        self.assertEqual(expected, merged)

    def test_merge_dict_nested_dict_more_values(self):
        original = {"network_interface": {"state": "UP", "type": "loopback", "name": "eth0"}}
        override = {"network_interface": {"state": "DOWN", "name": "eth1"}}
        expected = {"network_interface": {**original["network_interface"], **override["network_interface"]}}
        merged = _merge_dict(original, override)
        self.assertEqual(expected, merged)

    def test_merge_dict_nested_dict_wrong_key(self):
        original = {"network_interface": {"state": "UP"}}
        override = {"network_interface": {"name": "eth0"}}
        with self.assertRaises(KeyError):
            _merge_dict(original, override)

    def test_merge_dict_nested_dict_wrong_type(self):
        original = {"network_interface": {"mtu": 1500}}
        override = {"network_interface": {"mtu": "1500"}}
        with self.assertRaises(TypeError):
            _merge_dict(original, override)

    def test_merge_dict_deep_nested_dict_single_key(self):
        original = {"network_interfaces": {"eth0": {"state": "UP"}}}
        override = {"network_interfaces": {"eth0": {"state": "DOWN"}}}
        merged = _merge_dict(original, override)
        self.assertEqual(override, merged)

    def test_merge_dict_deep_nested_dict_more_keys(self):
        original = {"network_interfaces": {"eth0": {"state": "UP"}}, "eth1": {"state": "UP"}}
        override = {"network_interfaces": {"eth0": {"state": "DOWN"}}}
        merged = _merge_dict(original, override)
        expected = {"network_interfaces": {**original["network_interfaces"], **override["network_interfaces"]}}
        self.assertEqual(expected, merged)
