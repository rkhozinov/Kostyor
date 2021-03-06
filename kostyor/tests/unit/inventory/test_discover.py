import unittest

from kostyor.inventory import discover
import mock


class OpenStackServiceDiscoveryTest(unittest.TestCase):

    def setUp(self):
        keystone = mock.Mock()
        self.osd = discover.OpenStackServiceDiscovery(keystone)

    @mock.patch('novaclient.v2.services.ServiceManager.list')
    def test_discover_nova(self, fake_manager_list):
        expected = [('foo', 'nova-cpu'), ('bar', 'nova-cpu')]
        service1 = mock.Mock()
        service1.host = "foo"
        service1.binary = 'nova-cpu'
        service2 = mock.Mock()
        service2.host = "bar"
        service2.binary = 'nova-cpu'
        fake_manager_list.return_value = [service1, service2]
        res = self.osd.discover_nova()
        self.assertEqual(expected, res)

    @mock.patch("neutronclient.v2_0.client.Client.list_agents")
    def test_discover_neutron(self, fake_list_agents):
        expected = [('foo', 'neutron-l3')]
        fake_list_agents.return_value = {"agents": [{"binary": "neutron-l3",
                                                     "host": "foo"}]}
        res = self.osd.discover_neutron()
        self.assertEqual(expected, res)

    @mock.patch("keystoneclient.v2_0.endpoints.EndpointManager.list")
    @mock.patch("keystoneclient.v2_0.services.ServiceManager.list")
    def test_discover_keystone(self, fk_servicemanager, fk_endpointmanager):
        host = 'http://devstack-1.coreitpro.com:93923/'
        fake_id = 'fake-id'
        expected = [('devstack-1.coreitpro.com', 'nova-api')]
        fake_endpoint = mock.Mock()
        fake_endpoint.service_id = fake_id
        fake_endpoint.internalurl = host
        fake_service = mock.Mock()
        fake_service.id = fake_id
        fake_service.name = 'nova'

        fk_endpointmanager.return_value = [fake_endpoint]
        fk_servicemanager.return_value = [fake_service]
        self.assertEqual(expected, self.osd.discover_keystone())
