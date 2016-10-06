import unittest
import address_converter.address_objects as ao


def create_addr_object(postfix):
    return ao.AddrObject(
        aoguid='a_{0}'.format(postfix),
        name='n_{0}'.format(postfix),
        type_obj='t_{0}'.format(postfix),
        postalcode='p_{0}'.format(postfix))


class TestAddress(unittest.TestCase):

    def test_postalcode(self):
        addr_objects = []
        addr_objects.append(create_addr_object(1))
        addr_objects.append(create_addr_object(2))
        address = ao.Address()
        address.addr_path = addr_objects
        self.assertEqual(address.postalcode, 'p_2')

    def test_calc_address_string(self):
        addr_objects = []
        addr_objects.append(create_addr_object(1))
        addr_objects.append(create_addr_object(2))
        address = ao.Address()
        address.addr_path = addr_objects
        self.assertEqual(address.calc_address_string(),
                         't_1 n_1, t_2 n_2, p_2')

        addr_objects[1].postalcode = None
        self.assertEqual(address.calc_address_string(),
                         't_1 n_1, t_2 n_2')

        address.house_num = 123
        self.assertEqual(address.calc_address_string(),
                         't_1 n_1, t_2 n_2, 123')

        address.house_num_liter = 'abc'
        self.assertEqual(address.calc_address_string(),
                         't_1 n_1, t_2 n_2, 123 литера abc')

    def test_set_addr_path(self):
        addr_objects = []
        addr_objects.append(create_addr_object(1))
        addr_objects.append('wrong value')
        addr_objects.append(create_addr_object(2))
        address = ao.Address()
        address.addr_path = addr_objects
        self.assertEqual(address.calc_address_string(),
                         't_1 n_1, t_2 n_2, p_2')
