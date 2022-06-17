#!/usr/bin/env python3

# set server timezone in UTC before time module imported
import os
import sys
import logging
import re

import odoo
from odoo.modules.registry import Registry

os.environ['TZ'] = 'UTC'
# This line has been added, at first, with intention of running this db_initializer at a one step higher, and use
# the whole odoo as submodule
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/odoo")

logging.getLogger().addHandler(logging.StreamHandler())
_logger = logging.getLogger(__name__)

config = odoo.tools.config
#. (dot): ANY ONE character except newline. Same as [^\n]
#\w, \W: ANY ONE word/non-word character. For ASCII, word characters are [a-zA-Z0-9_]
DATABASE_URL_RE = re.compile(r'(?:postgresql|postgres)://(?P<db_user>.+):(?P<db_password>.+)@(?P<db_host>.+):(?P<db_port>\d+)/(?P<db_name>.+)')

default_database_url = "postgres://db_initializer:db_initializer@localhost:5432/db_initializer"
database_url = os.environ.get('DATABASE_URL', default_database_url)

group_dict = DATABASE_URL_RE.match(database_url).groupdict()
config['db_user'] = group_dict['db_user']
config['db_password'] = group_dict['db_password']
config['db_host'] = group_dict['db_host']
config['db_port'] = group_dict['db_port']
config['db_name'] = group_dict['db_name']
config['addons_path'] = "addons"
config['init']['base'] = True
config['without_demo'] = 'all'


def initialize():

    _logger.warning("Starting database initialization")
    # from preload_registries of service/server.py
    update_module = config['init'] or config['update']
    registry = Registry.new(config['db_name'], update_module=update_module)
    _logger.warning("Finished database initialization")

if __name__ == "__main__":
    initialize()