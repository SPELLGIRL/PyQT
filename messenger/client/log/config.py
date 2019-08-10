import logging
import os
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'client.log'),
                                   when="d",
                                   interval=1,
                                   backupCount=5,
                                   encoding='utf-8')
handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(message)s"))
client_logger = logging.getLogger('client')
client_logger.addHandler(handler)
client_logger.setLevel(logging.INFO)
