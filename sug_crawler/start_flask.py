

# import logging
# import sys
#
# # Создать регистратор верхнего уровня с именем ‘app’
# app_log = logging.getLogger("app")
# app_log.setLevel(logging.INFO)
# app_log.propagate = False
#
# # Добавить несколько обработчиков в регистратор ‘app’
# app_log.addHandler(logging.FileHandler('app.log'))
# app_log.addHandler(logging.StreamHandler(sys.stderr))
# # app_log.addHandler(logging.StreamHandler(sys.stdout))
#
# # Отправить несколько сообщений. Они попадут в файл app.log
# # и будут выведены в поток sys.stderr
# app_log.critical("Creeping death detected!")
# app_log.info("FYI")
#
# exit()


# main.py

import logging
import sys
from init_app import create_app

app = create_app()

if __name__ == "__main__":
    # init logger
    # print(app.name)
    logger = logging.getLogger(app.name)
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(
        '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} '
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

    app.run(debug=True)
