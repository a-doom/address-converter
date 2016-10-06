from .parser import (
    create_stop_words_list,
    clean_address_names_list,
    parse_address_names,
    parse_house_nums,
    parse_postcode)
from .neo4j_query_creator import (
    QueryExecutor,
    create_query,
    convert_to_addr_objects)
from .spellcheck import SpellChecker
from .config import config
import logging


class Converter(object):
    def __init__(self,
                 spellchecker=None,
                 queryExecutor=None,
                 stop_words_list=None,
                 write_error_log=False):
        self.spellchecker = spellchecker \
            or SpellChecker.create(
                config.SPELLCHECKER_DICT_FILENAME,
                config.COUNTED_DICT_FILENAME)

        self.executor = queryExecutor \
            or QueryExecutor(
                config.NEO4J_SERVER_ADDRESS,
                config.NEO4J_SERVER_LOGIN,
                config.NEO4J_SERVER_PASSWORD)

        self.stop_words_list = stop_words_list \
            or create_stop_words_list(config.STOP_WORDS_LIST_FILENAME)

        self.write_error_log = write_error_log
        logging.basicConfig(
            format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
            level=logging.ERROR,
            filename=config.ERROR_LOG_FILENAME)

        assert hasattr(self.spellchecker, 'check_words')
        assert hasattr(self.executor, 'execute_query')
        assert hasattr(self.stop_words_list, '__iter__')


    def __enter__(self):
        self.executor.__enter__()
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.close()


    def close(self):
        self.executor.close()


    def execute_query(self, query):
        result = []
        try:
            result = self.executor.execute_query(query)
        except:
            if self.write_error_log:
                logging.error('An error occurred while processing \
                              query:\n{0}'.format(query))
        return result


    def convert(self,
                address,
                addrobj_only=True,
                is_check_grammar=False):
        addr_objects = parse_address_names(address)
        postcodes = parse_postcode(address)
        nums = [] if addrobj_only else parse_house_nums(address)

        if is_check_grammar:
            addr_objects = self.spellchecker.check_words(addr_objects)

        query = create_query(
            clean_address_names_list(addr_objects, self.stop_words_list),
            nums,
            postcodes)

        query_result = self.execute_query(query)
        result = convert_to_addr_objects(query_result)
        return result
