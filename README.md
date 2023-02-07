# GamBot
Discord bot for playing casino-style games in your server.

# How To Use
The "official" version of this bot can be found [here](https://discord.com/api/oauth2/authorize?client_id=948132598364930088&permissions=274878188544&scope=bot).

If you wish to create your own instance of this bot, follow the instructions below:

- Create a new Discord application [here](https://discord.com/developers/applications). Create a bot user for this application and copy the token. Keep this safe and don't give it to anyone. Add the bot to one of your servers, so that you can interact with it.
- Make sure you have `Python >= 3.10` as well as the listed requirements installed. Many are dependencies of the `discord.py` library.
- Open the file named `envvar.env` and replace the values with your own. For variables that take a list of values, separate each value with only a comma.
- Makes sure the `envvar.env` and `data.db` files are kept in the same directory as `main.py`. Do not rename either of them. These files are what store your user & configuration data, so it's recommended to back them up regularly.
- Navigate into the GamBot directory in the terminal and run `python3 main.py`.

**This project is a WIP, some features may be unfinished!**