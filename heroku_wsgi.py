#!/usr/bin/env python3

# set server timezone in UTC before time module imported
import os, sys
os.environ['TZ'] = 'UTC'

# This line has been added, at first, with intention of running this db_initializer at a one step higher, and use
# the whole odoo as submodule
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/odoo")

import odoo
from odoo.service.server import load_server_wide_modules
from odoo.modules import initialize_sys_path

config = odoo.tools.config
default_database_url = "postgress://user:pass@host:3271/db_name"
database_url = os.environ.get('DATABASE_URL', default_database_url)

m1 = database_url.split(":")
config['db_user'] = m1[1][2:]
config['db_password'] = m1[2].split("@")[0]
config['db_host'] = m1[2].split("@")[1]
config['db_port'] = m1[3].split("/")[0]
config['db_name'] = m1[3].split("/")[1]
config['addons_path'] = "addons"

initialize_sys_path()
load_server_wide_modules()

application = odoo.http.root
# just trivial change to force heroku to rebuild;