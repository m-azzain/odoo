#!/usr/bin/env python3

# set server timezone in UTC before time module imported
import os
import re
os.environ['TZ'] = 'UTC'

# This line has been added, at first, with intention of running this db_initializer at a one step higher, and use
# the whole odoo as submodule
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/odoo")

import odoo
from odoo.service.server import load_server_wide_modules
from odoo.modules import initialize_sys_path

config = odoo.tools.config
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

initialize_sys_path()
load_server_wide_modules()

application = odoo.http.root
# just trivial change to force heroku to rebuild;