
import os
from string import ascii_lowercase, digits
import dotenv
dotenv.load_dotenv()

# flask app
RANDOM_STRING = os.getenv("RANDOM_STRING", "random string")
APP_NAME = "Suggestions Crawler"
FLASK_HOST = os.getenv("FLASK_HOST", 'localhost')
FLASK_PORT = os.getenv("FLSAK_PORT", 5000)

# params for rabbit queue
RABBIT_HOST = 'localhost'
RABBIT_PORT = 5672
RABBIT_VHOST = '/'
RABBIT_USER = 'guest'
RABBIT_PASSWORD = 'guest'
EXCHANGE_NAME = 'sug_exchange'
QUEUE_NAME = 'sug_queue'
ROUTING_KEY = 'sug_rkey'
MAX_ERRORS_COUNT = 5

RABBITMQ_URL = os.environ.get('RABBITMQ_URL')

# params for db (sqlite)
DB_NAME = os.environ.get(
    'DATABASE_URL',
    f'sqlite:///{os.path.join(os.getcwd(), "db", "keywords.sqlite3")}'
)

# params for proxy
PROXY_FILE_PATH = os.path.join(os.getcwd(), 'db', 'proxy_list.txt')
PROXY_OK_TIMEOUT = 10
PROXY_BN_TIMEOUT = 300


# configs for crawler
NUM_WORKERS = int(os.getenv('NUM_WORKERS', 5))
USE_PROXY = os.getenv('USE_PROXY', True)

ALPHABETS = ascii_lowercase + digits + "абвгдеёжзийклмнопрстуфхцчшщэюяїъыі"
MAX_INNER_QUEUE_SIZE = 1
URL = 'https://duckduckgo.com/ac/?callback=autocompleteCallback&q={query}&kl=wt-wt&_=1565197079862'
HEADERS = {
  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
  'Accept': '*/*',
  'Accept-Language': 'en-US,en;q=0.5',
  'Referer': 'https://duckduckgo.com/',
  'Connection': 'keep-alive'
}



