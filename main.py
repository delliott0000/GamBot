import config
import logging

from discord.ext import commands
from discord import (
    __version__ as __discord__,
    Intents,
    Activity,
    ActivityType,
    Guild,
    Embed,
    Interaction
)
from typing import Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s (%(filename)s) - %(message)s')


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


if __name__ == '__main__':

    if __discord__ == '2.1.0':
        pass

    else:
        pass
