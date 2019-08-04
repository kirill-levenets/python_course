# main.py

import logging
from init_app import create_app

app = create_app()

if __name__ == "__main__":
    # init logger
    logger = logging.getLogger(app.name)
    file_handler = logging.FileHandler(
        'logs/logfile.log', mode='a', encoding='utf8')
    file_handler.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(
        '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} '
        '%(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    app.run(debug=True)
