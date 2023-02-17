from os import getenv
from dotenv import load_dotenv

load_dotenv('envvar.env')

TOKEN = getenv('TOKEN')
OWNERS = getenv('OWNERS')
ACTIVITY = getenv('ACTIVITY')

START_CASH = getenv('START_CASH')
START_GOLD = getenv('START_GOLD')

achievements_mapping = {
    'bj_max': ('Doubling Down', 'In Blackjack, win after doubling down on the max bet.'),
    'bj_sevens': ('Triple 7s', 'In Blackjack, get to 21 points by having 3 sevens.'),
    'rou_mil': ('On The Ball', 'Win over `$1,000,000` from a single game of Roulette.'),
    'rou_zero': ('The Forgotten Number', 'Bet `$25,000` or more on the number `0` in roulette and win.'),
    'poker_sf': ('Straight Flush', 'In Poker, win the game by having a straight flush or better.'),
    'poker_max': ('All In', 'In Poker, win and take home a total prize of `$1,000,000` or more.'),
    'hl_max': ('Higher And Higher', 'In Higher Or Lower, win `$800,000` or more from a single game.'),
    'hl_str': ('Lucky Streak', 'Make it to a streak of 25 cards in Higher Or Lower.'),
    'slot_jack': ('1 In A Million', 'Hit the ultimate Jackpot on the slots machine.'),
    'spin_jack': ('A Special Prize', 'Spin the lucky wheel and land on the Jackpot prize.'),
    'lott_win': ('Early Retirement', 'Get lucky on the lottery and take home a huge prize!'),
    'scrat_win': ('3 Shiny Diamonds', 'Purchase a scratch card and win a rare item.'),
    'mill': ('Millionaire', 'Accumulate `$1,000,000` of wealth in GamBot money.'),
    'bill': ('Billionaire', 'Wait, how long did it take you to get this achievement?'),
    'legend': ('Legend', 'Achieve the rank of Legend (rank 9 or higher).')}

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

emoji_cost_mapping = {
    'Common Payout Booster': ('<:Blue:1037198209128337521>', 10),
    'Rare Payout Booster': ('<:Red:1037198238144548914>', 25),
    'Epic Payout Booster': ('<:Yellow:1037198261875908638>', 50),
    'Common XP Booster': ('<:Green:1037198197199745065>', 5),
    'Rare XP Booster': ('<:Purple:1037198226727641149>', 15),
    'Epic XP Booster': ('<:Pink:1037198248596742144>', 30),
    'Small Money Pack': ('<:coin1:1058406791198818364>', 5),
    'Medium Money Pack': ('<:coin2:1058406808097669151>', 8),
    'Large Money Pack': ('<:coin3:1058406820382773389>', 15),
    'Small Gold Pack': ('<:gold:1058395878190223380>', 8),
    'Medium Gold Pack': ('<:gold2:1058397872997023775>', 22),
    'Large Gold Pack': ('<:gold3:1058398446962360442>', 65),
    'Jackpot Pack': ('<:Rainbow_2:1037198961552920596>', 100)}

rank_mapping = {
    1: 'Rookie',
    2: 'Novice',
    3: 'Trained',
    4: 'Experienced',
    5: 'Skilled',
    6: 'Semi-Pro',
    7: 'Pro',
    8: 'Expert'}
