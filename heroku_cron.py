
# This file intended to run as heroku worker. It is not like the web dyno which run automatically
# the moment you define it on the Procfile, for this to run as a worker you need to run it manually
# you can execute the command "heroku run worker" on the terminal, or you can run it from the portal.
#
import os
import sys
import re
import select
import datetime
import time
import threading
import logging
import odoo
from odoo.tools import config
from odoo.service.server import load_server_wide_modules
from odoo.modules import initialize_sys_path


SLEEP_INTERVAL = 60    # 1 minute

DATABASE_URL_RE = re.compile(r'postgres://(?P<db_user>.+):(?P<db_password>.+)@(?P<db_host>.+):(?P<db_port>\d+)/(?P<db_name>.+)')
default_database_url = "postgres://db_initializer:db_initializer@localhost:5432/db_initializer"
database_url = os.environ.get('DATABASE_URL', default_database_url)
group_dict = DATABASE_URL_RE.match(database_url).groupdict()
config['db_user'] = group_dict['db_user']
config['db_password'] = group_dict['db_password']
config['db_host'] = group_dict['db_host']
config['db_port'] = group_dict['db_port']
config['db_name'] = group_dict['db_name']
config['addons_path'] = "addons"

config['log_db'] = group_dict['db_name']
config['log_db_level'] = 'info'
# config['logfile'] = 'odoo.log'
# config['log_level'] = 'info'

odoo.netsvc._logger_init = False
odoo.netsvc.init_logger()

# This way fo naming is very essential, for the handlers that defined on odoo namespace to handel the log
# https://stackoverflow.com/questions/7621897/python-logging-module-globally
_logger = logging.getLogger(f'odoo.{__name__}')

initialize_sys_path()
load_server_wide_modules()

def cron_thread(number):
    _logger.debug('beginning of cron%d', number)
    # Steve Reich timing style with thundering herd mitigation.
    #
    # On startup, all workers bind on a notification channel in
    # postgres so they can be woken up at will. At worst they wake
    # up every SLEEP_INTERVAL with a jitter. The jitter creates a
    # chorus effect that helps distribute on the timeline the moment
    # when individual worker wake up.
    #
    # On NOTIFY, all workers are awaken at the same time, sleeping
    # just a bit prevents they all poll the database at the exact
    # same time. This is known as the thundering herd effect.

    # from odoo.addons.base.models.ir_cron import ir_cron
    # conn = odoo.sql_db.db_connect('postgres')
    conn = odoo.sql_db.db_connect(config['db_name'])
    with conn.cursor() as cr:
        pg_conn = cr._cnx
        # LISTEN / NOTIFY doesn't work in recovery mode
        cr.execute("SELECT pg_is_in_recovery()")
        in_recovery = cr.fetchone()[0]
        if not in_recovery:
            cr.execute("LISTEN cron_trigger")
        else:
            _logger.warning("PG cluster in recovery mode, cron trigger not activated")
        cr.commit()

        # to initialize the registry
        evn = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        ir_cron = evn['ir.cron']

        while True:
            select.select([pg_conn], [], [], SLEEP_INTERVAL + number)
            time.sleep(number / 100)
            pg_conn.poll()

            registries = odoo.modules.registry.Registry.registries
            _logger.debug('cron%d polling for jobs', number)
            for db_name, registry in registries.d.items():
                if registry.ready:
                    thread = threading.current_thread()
                    thread.start_time = time.time()
                    try:
                        ir_cron._process_jobs(db_name)
                    except Exception:
                        _logger.warning('cron%d encountered an Exception:', number, exc_info=True)
                        print('cron%d encountered an Exception:' % number, exc_info=True)
                    thread.start_time = None

def cron_spawn():
    """ Start the above runner function in a daemon thread.

    The thread is a typical daemon thread: it will never quit and must be
    terminated when the main process exits - with no consequence (the processing
    threads it spawns are not marked daemon).

    """
    # Force call to strptime just before starting the cron thread
    # to prevent time.strptime AttributeError within the thread.
    # See: http://bugs.python.org/issue7980
    datetime.datetime.strptime('2012-01-01', '%Y-%m-%d')
    for i in range(odoo.tools.config['max_cron_threads']):
        def target():
            cron_thread(i)
        t = threading.Thread(target=target, name="odoo.service.cron.cron%d" % i)
        t.daemon = True
        t.type = 'cron'
        t.start()
        _logger.debug("cron%d started!" % i)

if __name__ == "__main__":
    cron_spawn()
    while 1:
        time.sleep(3600)