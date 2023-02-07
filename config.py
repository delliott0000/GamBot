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

pack_mapping = {
    'Small Money Pack': ('money_pack_s', 10000, 15000, 0, 0),
    'Medium Money Pack': ('money_pack_m', 35000, 50000, 0, 0),
    'Large Money Pack': ('money_pack_l', 100000, 150000, 0, 0),
    'Small Gold Pack': ('gold_pack_s', 0, 0, 5, 10),
    'Medium Gold Pack': ('gold_pack_m', 0, 0, 15, 25),
    'Large Gold Pack': ('gold_pack_l', 0, 0, 50, 75),
    'Jackpot Pack': ('jackpot_pack', 150000, 200000, 75, 95)}

boost_mapping = {
    'Common Payout Booster': ('pay_boost_c', 0.05, 0, 3600),
    'Rare Payout Booster': ('pay_boost_r', 0.15, 0, 21600),
    'Epic Payout Booster': ('pay_boost_e', 0.25, 0, 86400),
    'Common XP Booster': ('xp_boost_c', 0, 0.2, 3600),
    'Rare XP Booster': ('xp_boost_r', 0, 0.5, 21600),
    'Epic XP Booster': ('xp_boost_e', 0, 1.0, 86400)}
