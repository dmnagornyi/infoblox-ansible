# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.infoblox.nios_modules.plugins.modules import nios_host_record
from ansible_collections.infoblox.nios_modules.plugins.module_utils import api
from ansible_collections.infoblox.nios_modules.tests.unit.compat.mock import patch, MagicMock, Mock
from .test_nios_module import TestNiosModule, load_fixture


class TestNiosHostRecordModule(TestNiosModule):

    module = nios_host_record

    def setUp(self):

        super(TestNiosHostRecordModule, self).setUp()
        self.module = MagicMock(name='ansible_collections.infoblox.nios_modules.plugins.modules.nios_host_record.WapiModule')
        self.module.check_mode = False
        self.module.params = {'provider': None}

        self.mock_wapi = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_host_record.WapiModule')
        self.exec_command = self.mock_wapi.start()
        self.mock_wapi_run = patch('ansible_collections.infoblox.nios_modules.plugins.modules.nios_host_record.WapiModule.run')

        self.load_config = self.mock_wapi_run.start()
        self.mock_check_type_dict = patch('ansible.module_utils.common.validation.check_type_dict')
        self.mock_check_type_dict_obj = self.mock_check_type_dict.start()

    def tearDown(self):
        super(TestNiosHostRecordModule, self).tearDown()
        self.mock_wapi.stop()
        self.mock_check_type_dict.stop()

    def _get_wapi(self, test_object):
        wapi = api.WapiModule(self.module)
        wapi.get_object = Mock(name='get_object', return_value=test_object)
        wapi.create_object = Mock(name='create_object')
        wapi.update_object = Mock(name='update_object')
        wapi.delete_object = Mock(name='delete_object')
        return wapi

    def load_fixtures(self, commands=None):
        self.exec_command.return_value = (0, load_fixture('nios_result.txt').strip(), None)
        self.load_config.return_value = dict(diff=None, session='session')

    def test_nios_host_record_create(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'ansible',
                              'comment': None, 'extattrs': None}

        test_object = None
        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        print("WAPI: ", wapi)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.create_object.assert_called_once_with('testobject', {'name': 'ansible'})

    def test_nios_host_record_remove(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'ansible',
                              'comment': None, 'extattrs': None}

        ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [{
            "comment": "test comment",
            "_ref": ref,
            "name": "ansible",
            "extattrs": {'Site': {'value': 'test'}}
        }]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)
        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ref)

    def test_nios_host_record_remove_ipam_only(self):
        self.module.params = {'provider': None, 'state': 'absent', 'name': 'ansible',
                              'comment': None, 'extattrs': None, 'configure_for_dns': False}

        dns_ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/true"
        ipam_ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:ansible/false"

        test_object = [
            {
                "comment": "dns host",
                "_ref": dns_ref,
                "name": "ansible",
                "configure_for_dns": True,
                "extattrs": {}
            },
            {
                "comment": "ipam host",
                "_ref": ipam_ref,
                "name": "ansible",
                "configure_for_dns": False,
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "configure_for_dns": {"ib_req": True}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run(api.NIOS_HOST_RECORD, test_spec)
        self.assertTrue(res['changed'])
        wapi.delete_object.assert_called_once_with(ipam_ref)

    def test_nios_host_record_update_comment(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': 'default',
                              'comment': 'updated comment', 'extattrs': None}

        ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "default",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'updated comment', 'name': 'default'}
        )

    def test_nios_host_record_update_record_name(self):
        self.module.params = {'provider': None, 'state': 'present', 'name': {'new_name': 'default', 'old_name': 'old_default'},
                              'comment': 'comment', 'extattrs': None}

        ref = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:default/true"
        test_object = [
            {
                "comment": "test comment",
                "_ref": ref,
                "name": "old_default",
                "extattrs": {}
            }
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {}
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref, {'comment': 'comment', 'name': 'default'}
        )

    def test_nios_host_record_duplicate_ipv4(self):
        self.module.params = {
            'provider': None,
            'state': 'present',
            'name': 'ansible',
            'comment': 'updated comment',
            'extattrs': None,
            'ipv4addrs': [{'ipv4addr': '192.168.1.2'}],
        }

        ref_match = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:ansible1/true"
        ref_other = "record:host/ZG5zLm5ldHdvcmtfdmlldyQw:ansible2/true"

        test_object = [
            {
                "comment": "old comment",
                "_ref": ref_match,
                "name": "ansible",
                "ipv4addrs": [{"ipv4addr": "192.168.1.2"}],
                "extattrs": {},
            },
            {
                "comment": "other comment",
                "_ref": ref_other,
                "name": "ansible",
                "ipv4addrs": [{"ipv4addr": "192.168.1.3"}],
                "extattrs": {},
            },
        ]

        test_spec = {
            "name": {"ib_req": True},
            "comment": {},
            "extattrs": {},
            "ipv4addrs": {},
        }

        wapi = self._get_wapi(test_object)
        res = wapi.run('testobject', test_spec)

        self.assertTrue(res['changed'])
        wapi.update_object.assert_called_once_with(
            ref_match,
            {
                'comment': 'updated comment',
                'name': 'ansible',
                'ipv4addrs': [{'ipv4addr': '192.168.1.2'}],
            },
        )
