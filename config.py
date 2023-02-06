from os import getenv
from dotenv import load_dotenv

load_dotenv('envvar.env')

TOKEN = getenv('TOKEN')
OWNERS = getenv('OWNERS')

ACTIVITY = getenv('ACTIVITY')

START_CASH = getenv('START_CASH')
START_GOLD = getenv('START_GOLD')

COLOUR_INFO = getenv('COLOUR_INFO')
COLOUR_SUCCESS = getenv('COLOUR_SUCCESS')
COLOUR_ERROR = getenv('COLOUR_ERROR')
