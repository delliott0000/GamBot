# GamBot
Discord bot for playing casino-style games in your server.

# How To Use
The "official" version of this bot can be found [here](https://discord.com/api/oauth2/authorize?client_id=948132598364930088&permissions=274878188544&scope=bot).

If you wish to create your own instance of this bot, follow the instructions below:

- Create a new application at https://discord.com/developers/applications. Create a bot user for this application and copy the token. Keep this safe and don't give it to anyone.
- Make sure you have Python >= 3.10 as well as the listed requirements installed. Many are dependencies of discord.py.
- Open the .env file and replace the values with your own. For variables that take a list of values, separate each value with only a comma.
- Makes sure the .env and .db files are kept in the same directory as main.py. Do not rename either of them.
- Run main.py.