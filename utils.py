import discord
from discord.ext.buttons import Paginator


class Pager(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


# This function returns False if the bot cannot mute the member
async def mute_check(client_id, ctx, bot_role, member, muted_role):
    if member == ctx.author:
        await ctx.send("❌ You can't mute yourself!")
        return False

    if member.id == client_id:
        await ctx.send("❌ I can't mute myself!")
        return False

    if bot_role <= member.top_role:
        await ctx.send(
            "❌ The user has a higher role or the same top role as mine.\n"
            + "Please move my role higher!"
        )
        return False

    if not muted_role:
        await ctx.send(
            ":information_source: Couldn't find a Muted role in this server. Creating a new one..."
        )
        muted_role = await ctx.guild.create_role(name="Muted", colour=0x919191)

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)

    if bot_role <= muted_role:
        await ctx.send(
            "❌ My role is too low. I can only mute users if my role is higher than the Muted role!"
        )
        return False


time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}


async def time2seconds(send, time):
    try:
        return int(time[:-1]) * time_dict[time[-1]]
    except:
        await send(
            "❌ **Invalid duration**! Use `s` for seconds, `m` for minutes, `h` for hours or `d` for days.\n"
            + "For example: 30s is 30 seconds, 2m is 2 minutes"
        )
        return False
