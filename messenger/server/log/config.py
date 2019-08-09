import os
import logging
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'server.log'),
                                   when="d",
                                   interval=1,
                                   backupCount=5,
                                   encoding='utf-8')
handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(message)s"))
server_logger = logging.getLogger('server')
server_logger.addHandler(handler)
server_logger.setLevel(logging.INFO)
