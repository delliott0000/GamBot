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

achievements_mapping = {
    'bj_max': 'Doubling Down', 'bj_sevens': 'Triple 7s', 'rou_mil': 'On The Ball', 'rou_zero': 'The Forgotten Number',
    'poker_sf': 'Straight Flush', 'poker_max': 'All In', 'hl_max': 'Higher And Higher', 'hl_str': 'Lucky Streak',
    'slot_jack': '1 In A Million', 'spin_jack': 'A Special Prize', 'lott_win': 'Early Retirement',
    'scrat_win': '3 Shiny Diamonds', 'mill': 'Millionaire', 'bill': 'Billionaire', 'legend': 'Legend'}
