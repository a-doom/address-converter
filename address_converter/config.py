from configobj import ConfigObj
import os
CONFIG_FILENAME = 'config.ini'


class Config(object):
    def __init__(self):
        abs_config_filename = os.path.join(
            os.path.dirname(__file__),
            CONFIG_FILENAME)

        co = ConfigObj(abs_config_filename, encoding='UTF8')
        self.SPELLCHECKER_DICT_FILENAME = co['spellchecker_dict_filename']
        self.COUNTED_DICT_FILENAME = co['counted_dict_filename']
        self.STOP_WORDS_LIST_FILENAME = co['stop_words_list_filename']
        self.NEO4J_SERVER_ADDRESS = co['neo4j_server_address']
        self.NEO4J_SERVER_LOGIN = co['neo4j_login']
        self.NEO4J_SERVER_PASSWORD = co['neo4j_password']
        self.ERROR_LOG_FILENAME = co['error_log_filename']

config = Config()
