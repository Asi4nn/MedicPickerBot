from discord.ext import commands
from typing import Dict, Optional
from random import randint
from lib.helpers.mention_tools import verify_mention, get_id_from_mention
from lib.bot import PREFIX


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    if voice and voice.channel:
        return True
    else:
        await ctx.send("You need to be in the channel to do that")


class PugState:
    """Helper class managing multiple pugs per guild"""

    def __init__(self):
        self.medics = []

    def add_medics(self, medics):
        self.medics += medics
        immunes = []
        while len(self.medics) > 2:
            immunes.append(self.medics.pop(0))
        return immunes


class GuildState:
    """Helper class managing per-guild state"""

    def __init__(self):
        self.pugs = {}
        self.immunes = []

    def get_pug(self, pug: str):
        try:
            return self.pugs[pug]
        except KeyError:
            self.pugs[pug] = PugState()

        return self.pugs[pug]


class MedicPicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states: Dict[GuildState] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Medic Picker cog ready")

    def get_state(self, guild) -> GuildState:
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.command(name="pick_medics", aliases=["roll", "pick"],
                      brief="Randomly picks 2 people by default in the voice channel for "
                            "medic, ignoring any immune players.")
    @commands.check(in_voice_channel)
    @commands.has_guild_permissions(manage_roles=True)
    async def pick_medics(self, ctx: commands.Context, amount="2", pug="A"):
        if amount not in ['1', '2']:
            await ctx.send("Invalid roll amount (choose 1 or 2)")
            return

        if not pug.isalpha():
            await ctx.send("Use letters for identifying different pugs! (A pug, B pug, etc.)")
            return

        members = ctx.author.voice.channel.members

        if len(members) < 12:
            await ctx.send("Warning! Less than 12 people in voice channel!")

        picks = []
        state = self.get_state(ctx.guild)
        current_pug = state.get_pug(pug)

        if amount == "2":  # when rolling 2 meds, set all previous meds to be immune
            state.immunes += current_pug.medics
            current_pug.medics = []

        # picks medics
        while len(picks) < int(amount):
            index = randint(0, len(members) - 1)
            if members[index] not in state.immunes and members[index] not in picks and not members[index].bot:
                picks.append(members[index])

        immunes = current_pug.add_medics(picks)
        state.immunes += immunes

        await ctx.send("Picked medics: " + ", ".join([user.mention for user in picks]))

    @commands.command(name="immunes", brief="Shows players immune to being rolled as medic")
    async def immunes(self, ctx: commands.Context):
        state = self.get_state(ctx.guild)
        if not state.immunes:
            await ctx.send("No immune players at the moment")
        else:
            await ctx.send("Players immune to medic: " + ", ".join([user.mention for user in state.immunes]))

    @commands.command(name="set_immune", aliases=["si"], brief="Sets the given player immune to being picked as medic")
    @commands.has_guild_permissions(manage_roles=True)
    async def set_immune(self, ctx: commands.Context, mention):
        if not verify_mention(mention):
            await ctx.send(f"Invalid mention, type {PREFIX}help for command syntax!")
            return

        user = ctx.guild.get_member(get_id_from_mention(mention))
        state = self.get_state(ctx.guild)
        state.immunes.append(user)

        await ctx.send(f"{user.mention} is now immune to being medic!")

    @commands.command(name="clear_immune", aliases=["ci", "clear"],
                      brief="Removes the given player immune to being picked as medic if applicable")
    @commands.has_guild_permissions(manage_roles=True)
    async def clear_immune(self, ctx: commands.Context, *, mention: Optional[str]):
        if mention and not verify_mention(mention):
            await ctx.send(f"Invalid mention, type {PREFIX}help for command syntax!")
            return

        state = self.get_state(ctx.guild)
        if mention:
            user = ctx.guild.get_member(get_id_from_mention(mention))
            if user in state.immunes:
                state.immunes.remove(user)
                await ctx.send(f"{user.mention} is no longer immune")
            else:
                await ctx.send(f"{user.mention} was not immune to medic!")
        else:
            state.immunes = []
            await ctx.send("Cleared all immune players")


def setup(bot):
    bot.add_cog(MedicPicker(bot))
