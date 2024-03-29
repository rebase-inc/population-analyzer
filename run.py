import rsyslog
import logging
from os import environ
from multiprocessing import current_process

from redis import StrictRedis, ConnectionPool
from rq import Worker, Queue, Connection

current_process().name = environ['SERVICE']
rsyslog.setup(log_level = environ['LOG_LEVEL'])
LOGGER = logging.getLogger()

try:
    # why just one connection at a time?
    pool = ConnectionPool(host='redis', max_connections=1)

    with Connection(StrictRedis(connection_pool = pool)):
        worker = Worker(environ['SERVICE'])
        worker.work(logging_level = environ['LOG_LEVEL'])
except Exception as exc:
    LOGGER.exception('Unhandled exception!')
