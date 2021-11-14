from random import randint, choice

from discord import Embed, Colour, File, Game
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Cog, Context, command, check, has_permissions, has_guild_permissions
from lib.bot import OWNER_IDS, PREFIX

# CONTRIBUTORS: add your discord tag and github link in this dictionary
CONTRIBUTORS = {
    "Asi4n#5622": "github.com/Asi4nn",
}


async def is_owner(ctx: Context):
    """Checks if the caller of the command is a bot owner"""
    return ctx.author.id in OWNER_IDS


class General(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=Game(f"{PREFIX}help"))
        print("General cog ready")

    @command(name="source", brief="Gets bot source link with invite link")
    async def source(self, ctx):
        embed = Embed(
            title='The Administrator Bot',
            description='Open source discord bot made for picking medics for Team Fortress 2 pugs',
            colour=Colour.purple(),
            url='https://github.com/Asi4nn/MedicPickerBot'
        )

        image = open("data/images/admin.png", "rb")
        file = File(image, filename="admin.png")
        embed.set_image(url='attachment://admin.png')
        embed.set_footer(text='Licensed under the MIT License')
        embed.add_field(name='Contributors:', value='https://github.com/Asi4nn/MedicPickerBot')
        for c in CONTRIBUTORS:
            embed.add_field(name=c, value=CONTRIBUTORS[c], inline=False)
        await ctx.send(embed=embed, file=file)
        image.close()


def setup(bot):
    bot.add_cog(General(bot))
