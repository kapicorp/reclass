#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from reclass import get_storage, get_path_mangler
from reclass.core import Core
from reclass.settings import Settings
from reclass.errors import ClassNotFound

import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestCore(unittest.TestCase):

    def _core(self, dataset, opts={}, class_mappings=[]):
        inventory_uri = os.path.dirname(os.path.abspath(__file__)) + '/data/' + dataset
        path_mangler = get_path_mangler('yaml_fs')
        nodes_uri, classes_uri = path_mangler(inventory_uri, 'nodes', 'classes')
        settings = Settings(opts)
        storage = get_storage('yaml_fs', nodes_uri, classes_uri, settings.compose_node_name)
        return Core(storage, class_mappings, settings)

    def test_type_conversion(self):
        reclass = self._core('01')
        node = reclass.nodeinfo('data_types')
        params = { 'int': 1, 'bool': True, 'string': '1', '_reclass_': { 'environment': 'base', 'name': {'full': 'data_types', 'parts': ['data_types'], 'path': 'data_types', 'short': 'data_types' } } }
        self.assertEqual(node['parameters'], params)

    def test_raise_class_notfound(self):
        reclass = self._core('01')
        with self.assertRaises(ClassNotFound):
            node = reclass.nodeinfo('class_notfound')

    def test_ignore_class_notfound(self):
        reclass = self._core('01', opts={ 'ignore_class_notfound': True, 'ignore_class_notfound_warning': False })
        node = reclass.nodeinfo('class_notfound')
        params = { 'node_test': 'class not found', '_reclass_': { 'environment': 'base', 'name': {'full': 'class_notfound', 'parts': ['class_notfound'], 'path': 'class_notfound', 'short': 'class_notfound' } } }
        self.assertEqual(node['parameters'], params)

    def test_raise_class_notfound_with_regexp(self):
        reclass = self._core('01', opts={ 'ignore_class_notfound': True, 'ignore_class_notfound_warning': False, 'ignore_class_notfound_regexp': 'notmatched.*' })
        with self.assertRaises(ClassNotFound):
            node = reclass.nodeinfo('class_notfound')

    def test_ignore_class_notfound_with_regexp(self):
        reclass = self._core('01', opts={ 'ignore_class_notfound': True, 'ignore_class_notfound_warning': False, 'ignore_class_notfound_regexp': 'miss.*' })
        node = reclass.nodeinfo('class_notfound')
        params = { 'node_test': 'class not found', '_reclass_': { 'environment': 'base', 'name': {'full': 'class_notfound', 'parts': ['class_notfound'], 'path': 'class_notfound', 'short': 'class_notfound' } } }
        self.assertEqual(node['parameters'], params)

    def test_relative_class_names(self):
        reclass = self._core('02')
        node = reclass.nodeinfo('relative')
        params = { 'test1': 1, 'test2': 2, 'test3': 3, 'test4': 4, 'test5': 5, 'one_beta': 1, 'two_beta': 2, 'four_alpha': 3, 'two_gamma': 4, 'alpha_init': 5, '_reclass_': { 'environment': 'base', 'name': { 'full': 'relative', 'parts': ['relative'], 'path': 'relative', 'short': 'relative' } } }
        self.assertEqual(node['parameters'], params)

    def test_top_relative_class_names(self):
        reclass = self._core('02')
        node = reclass.nodeinfo('top_relative')
        params = { 'test1': 1, 'test2': 2, 'test3': 3, 'test4': 4, 'test5': 5, 'one_beta': 1, 'two_beta': 2, 'four_alpha': 3, 'two_gamma': 4, 'alpha_init': 5, '_reclass_': { 'environment': 'base', 'name': { 'full': 'top_relative', 'parts': ['top_relative'], 'path': 'top_relative', 'short': 'top_relative' } } }
        self.assertEqual(node['parameters'], params)

    def test_compose_node_names(self):
        reclass = self._core('03', opts={'compose_node_name': True})
        alpha_one_node = reclass.nodeinfo('alpha.one')
        alpha_one_res = {'a': 1, 'alpha': [1, 2], 'beta': {'a': 1, 'b': 2}, 'b': 2, '_reclass_': {'environment': 'base', 'name': {'full': 'alpha.one', 'parts': ['alpha', 'one'], 'path': 'alpha/one', 'short': 'one'}}}
        alpha_two_node = reclass.nodeinfo('alpha.two')
        alpha_two_res = {'a': 1, 'alpha': [1, 3], 'beta': {'a': 1, 'c': 3}, 'c': 3, '_reclass_': {'environment': 'base', 'name': {'full': 'alpha.two', 'parts': ['alpha', 'two'], 'path': 'alpha/two', 'short': 'two'}}}
        beta_one_node = reclass.nodeinfo('beta.one')
        beta_one_res = {'alpha': [2, 3], 'beta': {'c': 3, 'b': 2}, 'b': 2, 'c': 3, '_reclass_': {'environment': 'base', 'name': {'full': 'beta.one', 'parts': ['beta', 'one'], 'path': 'beta/one', 'short': 'one'}}}
        beta_two_node = reclass.nodeinfo('beta.two')
        beta_two_res = {'alpha': [3, 4], 'c': 3, 'beta': {'c': 3, 'd': 4}, 'd': 4, '_reclass_': {'environment': u'base', 'name': {'full': u'beta.two', 'parts': ['beta', 'two'], 'path': 'beta/two', 'short': u'two'}}}
        self.assertEqual(alpha_one_node['parameters'], alpha_one_res)
        self.assertEqual(alpha_two_node['parameters'], alpha_two_res)
        self.assertEqual(beta_one_node['parameters'], beta_one_res)
        self.assertEqual(beta_two_node['parameters'], beta_two_res)

    def test_class_mappings_match_path_false(self):
        reclass = self._core('04', opts={'class_mappings_match_path': False}, class_mappings=['node*    two', 'alpha/node*    three'])
        node = reclass.nodeinfo('node1')
        params = { 'test1': 1, 'test2': 2, '_reclass_': {'environment': u'base', 'name': {'full': 'node1', 'parts': ['node1'], 'path': 'node1', 'short': 'node1'}}}
        self.assertEqual(node['parameters'], params)

    def test_class_mappings_match_path_true(self):
        reclass = self._core('04', opts={'class_mappings_match_path': True}, class_mappings=['node*    two', 'alpha/node*    three'])
        node = reclass.nodeinfo('node1')
        params = { 'test1': 1, 'test3': 3, '_reclass_': {'environment': u'base', 'name': {'full': 'node1', 'parts': ['node1'], 'path': 'node1', 'short': 'node1'}}}
        self.assertEqual(node['parameters'], params)
    
    def test_merging_of_parameters_before_class_interpolation_enabling_overrides(self):
        reclass = self._core('05')

        dev = reclass.nodeinfo('dev')
        stg = reclass.nodeinfo('stg')
        prd = reclass.nodeinfo('prd')

        self.assertEqual(dev['parameters']['loaded_from']['core_dns'], 'v1')
        self.assertEqual(dev['parameters']['loaded_from']['cluster_autoscaler'], 'v1')

        self.assertEqual(stg['parameters']['loaded_from']['core_dns'], 'v1')
        self.assertEqual(stg['parameters']['loaded_from']['cluster_autoscaler'], 'v0')

        self.assertEqual(prd['parameters']['loaded_from']['core_dns'], 'v0')
        self.assertEqual(prd['parameters']['loaded_from']['cluster_autoscaler'], 'v0')

    def test_application_removal(self):
        reclass = self._core('06')

        A_node = reclass.nodeinfo('A_node')
        B_node = reclass.nodeinfo('B_node')

        self.assertEqual(A_node['applications'], A_node['parameters']['expected_apps'])
        self.assertEqual(B_node['applications'], B_node['parameters']['expected_apps'])

if __name__ == '__main__':
    unittest.main()
