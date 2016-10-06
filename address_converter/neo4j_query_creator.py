from neo4j.v1 import GraphDatabase, basic_auth
import re
from .address_objects import Address, AddrObject


class QueryExecutor(object):
    def __init__(self, server_address, login, password):
        self._server_address = server_address
        self._login = login
        self._password = password

    def __enter__(self):
        self._driver = GraphDatabase.driver(
            self._server_address,
            auth=basic_auth(self._login, self._password))
        self._session = self._driver.session()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def close(self):
        self._session.close()

    def execute_query(self, query):
        assert hasattr(self, "_session"), "At first create a session"
        result = self._session.run(query)
        return result


_begin_pattern = r"^"
_end_pattern = r"\\b.*"


def _create_mix_addr_query(
        address_names,
        node_max_num,
        level=0,
        node_name="a",
        param_name="biggestword",
        is_show_tabs=False):
    """Create a part of the query for finding address objects.
    """
    if (not any(address_names)
            or (node_max_num - level) > len(address_names)):
        return ""

    result = ""
    for addr_index, addr in enumerate(address_names):
        is_new_row = addr_index > 0 and is_show_tabs
        result += "{next_row}{tabs}{white_space}{or_}".format(
            next_row="\n" if is_new_row else "",
            tabs="\t" * (level + 1) if is_new_row else "",
            white_space=" " if addr_index > 0 else "",
            or_="OR " if addr_index > 0 else "")

        result += "{node_name}{node_num}.{param_name} =".format(
            node_name=node_name,
            node_num=level,
            param_name=param_name)

        result += " '{query_val}'".format(query_val=addr)

        if level < node_max_num - 1:
            sub_addr = list(address_names)
            del sub_addr[addr_index]
            sub_query = _create_mix_addr_query(
                sub_addr,
                node_max_num,
                level + 1,
                node_name,
                param_name)

            result += "{next_row}{tabs}{white_space}AND {sub_query}".format(
                next_row="\n" if is_show_tabs else "",
                tabs="\t" * (level + 2) if is_show_tabs else "",
                white_space=" " if not is_show_tabs else "",
                sub_query=sub_query)
    return "({0})".format(result)


def _create_addr_postcodes_query(postcodes, node_max_num):
    if not any(postcodes):
        return ""

    postcodes.append("")
    pc_re = "|".join([p[:3] + "[0-9]{3,}" for p in postcodes if len(p) > 3])
    pc_re = "{0}({1})$".format(_begin_pattern, pc_re)
    result = "\n\tAND a{0}.postalcode =~ '{1}'".format(
        (node_max_num - 1), pc_re)
    return result


def _create_house_query(house_nums, postcodes, node_max_num):
    if not any(house_nums):
        return ""

    if any(postcodes):
        pc_re = "|".join([p for p in postcodes])
        pc_re = "{0}({1})$".format(_begin_pattern, pc_re)

    house_nums = list(house_nums)
    pattern_num = re.compile("[0-9]")
    house_nums_re = []
    for num in house_nums:
        se = pattern_num.search(num)
        if se:
            house_nums_re.append(se.group(0))

    nums_re_str = "|".join([qr for qr in house_nums_re])
    nums_re_str = r"{0}({1})([^0-9]|$)".format(_begin_pattern, nums_re_str)
    result = "\nOPTIONAL MATCH (a{0})<-[*1]-(h:House)".format(node_max_num - 1)
    result += "\nWHERE"
    result += "\n\th.complexnum =~ '{0}'".format(nums_re_str)
    if any(postcodes):
        result += "\n\tAND h.postalcode =~ '{0}'".format(pc_re)
    return result


def _create_house_int_query(house_nums, postcodes, node_max_num):
    if not any(house_nums):
        return ""

    if any(postcodes):
        pc_re = "|".join([p for p in postcodes])
        pc_re = "{0}({1})$".format(_begin_pattern, pc_re)

    house_nums = list(house_nums)
    pattern = re.compile(r"(\d+)")
    for i, num in enumerate(house_nums):
        n = pattern.search(num)
        if n is not None:
            house_nums[i] = n.group()

    result = "\nOPTIONAL MATCH (a{0})<-[*1]-(hi:HouseInt)".format(
        node_max_num - 1)
    result += "\nWHERE"
    for i, num in enumerate([int(x) for x in house_nums]):
        result += "\n\t"
        if i > 0:
            result += "OR "
        result += "(hi.intstart <= {0}".format(num)
        result += " AND {0} <= hi.intend)".format(num)
    if any(postcodes):
        result += "\n\tAND hi.postalcode =~ '{0}'".format(pc_re)
    return result


def create_query(
        addr_obj_name,
        house_nums,
        postcodes,
        node_max_num=2,
        output_limit=100):
    """Create neo4j query for finding address objects

    Args:
        addr_obj_name: a list of addresses names
        house_nums: a list of house numbers
        postcodes: a list of postal codes
        node_max_num: int, a number of nodes used in the query
        output_limit: int, a number of requests return values
    Results:
        Query text
    """
    if not any(addr_obj_name):
        return ""

    # MATCH
    result_query = "MATCH (r:Root)"
    for i in range(node_max_num):
        result_query += ", (a{}:Addrobj)".format(i)
    # relations
    result_query += ", rel = (r)"
    for i in range(node_max_num):
        result_query += "<-[*..2]-(a{})".format(i)
    # WHERE
    result_query += "\nWHERE"
    addr_query = _create_mix_addr_query(
        addr_obj_name,
        node_max_num)
    if not any(addr_query):
        return ""

    result_query += addr_query
    result_query += _create_addr_postcodes_query(postcodes, node_max_num)
    result_query += "\nWITH rel, a{}".format(node_max_num - 1)

    result_query += _create_house_query(house_nums, postcodes, node_max_num)
    result_query += _create_house_int_query(house_nums, postcodes, node_max_num)

    result_query += "\nRETURN"
    result_query += "\n\t[n in nodes(rel) where n:Addrobj | n.offname] as {0},".format(_offname)
    result_query += "\n\t[n in nodes(rel) where n:Addrobj | n.aoguid] as {0},".format(_aoguid)
    result_query += "\n\t[n in nodes(rel) where n:Addrobj | n.socrname] as {0},".format(_socrname)
    result_query += "\n\t[n in nodes(rel) where n:Addrobj | n.postalcode] as {0}".format(_postcode)

    if any(house_nums):
        result_query += ", h as Houses"
        result_query += ", hi as HousesInt"

    result_query += "\nLIMIT {}".format(output_limit)
    return result_query

_offname = 'AddrobjOffname'
_aoguid = 'AddrobjAoguid'
_socrname = 'AddrobjSocrname'
_postcode = 'AddrobjPostalcode'


def convert_to_addr_objects(query_result):
    """Convert the query result into the list of Address objects
    """
    result = []
    if not hasattr(query_result, '__iter__'):
        return result
    for record in query_result:
        address = Address()
        offnames = record[_offname]
        ids = record[_aoguid]
        type_names = record[_socrname]
        postalcodes = record[_postcode]

        addr_path = []
        for arg in zip(offnames, ids, type_names, postalcodes):
            addr_path.append(AddrObject(
                name=arg[0],
                aoguid=arg[1],
                type_obj=arg[2],
                postalcode=arg[3]))
        address.addr_path = addr_path
        result.append(address)
    assert not any(result) or isinstance(result[0], Address)
    return result
