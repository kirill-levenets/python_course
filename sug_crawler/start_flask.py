
# main.py

import logging
import sys

from init_app import create_app
from sug_config import FLASK_HOST, FLASK_PORT

app = create_app()

if __name__ == "__main__":
    # init logger
    # print(app.name)
    logger = logging.getLogger(app.name)
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(
        '[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} '
        '%(levelname)s - %(message)s'
    )

    file_handler = logging.FileHandler(
        'logs/logfile.log', mode='a', encoding='utf8')
    file_handler.setFormatter(log_formatter)

    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(s_handler)

    app.logger.info('start flask!')

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
