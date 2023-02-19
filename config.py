from os import getenv
from dotenv import load_dotenv

load_dotenv('envvar.env')

TOKEN = getenv('TOKEN')
OWNERS = getenv('OWNERS')
ACTIVITY = getenv('ACTIVITY')

INVITE = getenv('INVITE')
SUPPORT = getenv('SUPPORT')
VOTE = getenv('VOTE')

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

wheel_mapping = {
    1: ('green', 'https://cdn.discordapp.com/emojis/991767837242822828.webp?size=128&quality=lossless', 1000, 3000),
    2: ('blue', 'https://cdn.discordapp.com/emojis/991767561379254333.webp?size=128&quality=lossless', 5000, 8500),
    3: ('purple', 'https://cdn.discordapp.com/emojis/991767912085987348.webp?size=128&quality=lossless', 12000, 18000),
    4: ('red', 'https://cdn.discordapp.com/emojis/991767644627808336.webp?size=128&quality=lossless', 25000, 35000),
    5: ('pink', 'https://cdn.discordapp.com/emojis/991767672041787483.webp?size=128&quality=lossless', 60000, 100000),
    6: ('gold', 'https://cdn.discordapp.com/emojis/991767615603228743.webp?size=128&quality=lossless', 250000, 250000)}

slot_num_to_emote = {
    1: '<:White:1037198176068841522>', 2: '<:Green:1037198197199745065>', 3: '<:Blue:1037198209128337521>',
    4: '<:Purple:1037198226727641149>', 5: '<:Red:1037198238144548914>', 6: '<:Pink:1037198248596742144>',
    7: '<:Yellow:1037198261875908638>', 8: '<:Rainbow_1:1037198949347500042>', 9: '<:Rainbow_2:1037198961552920596>',
    0: '<:Grey:1038095549729079316>'}

roulette_listings = {
    'Odd': [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
    'Even': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
    'Red': [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
    'Black': [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
    '1st Column': [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
    '2nd Column': [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    '3rd Column': [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    '1st Dozen': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    '2nd Dozen': [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    '3rd Dozen': [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
    '1st Eighteen': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    '2nd Eighteen': [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]}
for i in range(37):
    roulette_listings[f'Number {i}'] = [i]

rou_nums_to_emotes = {
    0: '<:0_:951573939962908762>', 1: '<:1_:951573969717313556>', 2: '<:2_:951573986234495008>',
    3: '<:3_:951574181428994118>', 4: '<:4_:951574193999339560>', 5: '<:5_:951574205948891216>',
    6: '<:6_:951574216988303412>', 7: '<:7_:951574230225543258>', 8: '<:8_:951574242527440956>',
    9: '<:9_:951574256075022356>', 10: '<:10:951574300064882740>', 11: '<:11:951574312383545374>',
    12: '<:12:951574386253631498>', 13: '<:13:951574397959942275>', 14: '<:14:951574410085662841>',
    15: '<:15:951574428171518033>', 16: '<:16:951574440322400266>', 17: '<:17:951574453123416114>',
    18: '<:18:951574466624905277>', 19: '<:19:951574477802729552>', 20: '<:20:951574500242247770>',
    21: '<:21:951574584577114184>', 22: '<:22:951574597709479936>', 23: '<:23:951574610380460124>',
    24: '<:24:951574629024153701>', 25: '<:25:951574642718568572>', 26: '<:26:951574657520255037>',
    27: '<:27:951574673030787082>', 28: '<:28:951574687840870450>', 29: '<:29:951574702751645806>',
    30: '<:30:951574724033536000>', 31: '<:31:951574736188629053>', 32: '<:32:951574749446823947>',
    33: '<:33:951574765167067237>', 34: '<:34:951574780199436299>', 35: '<:35:951574794174865438>',
    36: '<:36:951574807206563860>'}

cards_to_emotes = {
    0: '<:card_back:1038508124941856889>',
    1: '<:2C:950438413683814410>', 2: '<:2D:950438427264946218>',
    3: '<:2H:950438439323594802>', 4: '<:2S:950438450828546118>',
    5: '<:3C:950438463059144765>', 6: '<:3D:950438476837453894>',
    7: '<:3H:950438489336467466>', 8: '<:3S:950438501411852289>',
    9: '<:4C:950438519388659733>', 10: '<:4D:950438531547951214>',
    11: '<:4H:950438549226922044>', 12: '<:4S:950438559817531402>',
    13: '<:5C:950438571821649962>', 14: '<:5D:950438584635228230>',
    15: '<:5H:950438596807114823>', 16: '<:5S:950438609813643335>',
    17: '<:6C:950438671562207312>', 18: '<:6D:950438682224099359>',
    19: '<:6H:950438695771725906>', 20: '<:6S:950438711865278575>',
    21: '<:7C:950438726369177680>', 22: '<:7D:950438739824476200>',
    23: '<:7H:950438753455984671>', 24: '<:7S:950438813266755674>',
    25: '<:8C:950438842396188722>', 26: '<:8D:950438859664158780>',
    27: '<:8H:950438875375992912>', 28: '<:8S:950438889368203354>',
    29: '<:9C:950438912252334120>', 30: '<:9D:950438934196932638>',
    31: '<:9H:950438957840216184>', 32: '<:9S:950438983698120744>',
    33: '<:10C:950439046084182056>', 34: '<:10D:950439059266883584>',
    35: '<:10H:950439081358266488>', 36: '<:10S:950439096805912637>',
    37: '<:JC:950439250833317989>', 38: '<:JD:950439345855295498>',
    39: '<:JH:950439365455282226>', 40: '<:JS:950439377794924574>',
    41: '<:QC:950439413501022208>', 42: '<:QD:950439425043750992>',
    43: '<:QH:950439436292857876>', 44: '<:QS:950439447479083028>',
    45: '<:KC:950439517544923196>', 46: '<:KD:950439528202633246>',
    47: '<:KH:950439537719529522>', 48: '<:KS:950474184327323690>',
    49: '<:AC:950441553212629002>', 50: '<:AD:950441571390730301>',
    51: '<:AH:950441585059967088>', 52: '<:AS:950441600201392178>'}

higher_lower_emotes = {
    'higher': '<:Higher:1038546827995263066>',
    'lower': '<:Lower:1038546838426484847>',
    'walk': '<:Start:1039619761677541478>'}
