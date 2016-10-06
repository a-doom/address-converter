LETTER = "литера"


class AddrObject(object):
    def __init__(self, aoguid, name, type_obj, postalcode):
        self.aoguid = aoguid
        self.name = name
        self.type_obj = type_obj
        self.postalcode = postalcode

    def __str__(self):
        return "{0} - {1}".format(self.aoguid, self.name)

    def __repr__(self):
        return "{0} - {1}".format(self.aoguid, self.name)


class Address(object):
    def __init__(self):
        self._addr_path = ()
        self.house_num = 0
        self.house_num_liter = ""

    @property
    def postalcode(self):
        """Get the postal code from the last address in the list
        """
        if any(self.addr_path):
            return self.addr_path[-1].postalcode
        else:
            return ''

    def calc_address_string(self):
        result = ", ".join(
            ["{0} {1}".format(addrobj.type_obj, addrobj.name)
             for addrobj in self.addr_path])
        if self.house_num:
            result += ", {0}".format(self.house_num)
        if self.house_num_liter:
            result += " {0} {1}".format(LETTER, self.house_num_liter)
        if self.postalcode:
            result += ", {0}".format(self.postalcode)
        return result

    @property
    def addr_path(self):
        return self._addr_path

    @addr_path.setter
    def addr_path(self, value):
        self._addr_path = tuple(
            [v for v in value if isinstance(v, AddrObject)])
