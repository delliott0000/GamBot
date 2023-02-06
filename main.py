import asyncio
import config
import logging
from typing import Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s (%(filename)s) - %(message)s')

try:
    from discord.ext import commands
    from discord import (
        __version__ as __discord__,
        Intents,
        Activity,
        ActivityType,
        Guild,
        Embed,
        Interaction,
        PrivilegedIntentsRequired,
        LoginFailure
    )
except ModuleNotFoundError:
    logging.fatal('Missing required dependencies.')
    exit(0)


class GamBot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=Intents.default(),
            command_prefix=None,
            help_command=None,
            activity=Activity(type=ActivityType.custom, name=config.ACTIVITY)
        )
        self.db = None

    @property
    def _token(self):
        return config.TOKEN

    @property
    def _colour_info(self):
        return hex(int(config.COLOUR_INFO, 16))

    @property
    def _colour_success(self):
        return hex(int(config.COLOUR_SUCCESS, 16))

    @property
    def _colour_error(self):
        return hex(int(config.COLOUR_ERROR, 16))

    def _bot_colour(self, guild: Union[Guild, None]):
        if guild:
            return guild.get_member(self.user.id).colour
        return 0xffffff

    @staticmethod
    async def ephemeral_response(interaction: Interaction, reply: str, colour: int):
        await interaction.response.send_message(embed=Embed(colour=colour, description=reply), ephemeral=True)

    def run_bot(self):
        async def runner():
            async with self:
                try:
                    await self.start(self._token)
                except LoginFailure:
                    logging.fatal('Invalid token passed.')
                except PrivilegedIntentsRequired:
                    logging.fatal('Privileged intents are being requested that have not '
                                  'been explicitly enabled in the developer portal..')

        async def cancel_tasks():
            try:
                await self.db.commit()
                await self.db.close()
            except AttributeError:
                pass

        try:
            asyncio.run(runner())
        except (KeyboardInterrupt, SystemExit):
            logging.info("Received signal to terminate bot and event loop.")
        finally:
            logging.info('Cleaning up tasks and connections...')
            asyncio.run(cancel_tasks())
            logging.info('Done. Have a nice day!')


if __name__ == '__main__':

    if __discord__ == '2.1.0':
        bot = GamBot()
        bot.run_bot()

    else:
        logging.error('The incorrect version of discord.py has been installed.')
        logging.error('Current Version: {}'.format(__discord__))
        logging.error('Required: 2.1.0')
