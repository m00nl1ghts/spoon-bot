import re
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands
from utils import BlooContext, cfg, transform_context
from utils.framework import (always_whisper,
                             ensure_invokee_role_lower_than_bot, whisper)
from utils.views import (Confirm, device_autocomplete, get_ios_cfw,
                         ios_on_device_autocomplete, transform_groups)


class Devices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.devices_test = re.compile(r'^.+ \[.+\,.+\]$')
        self.devices_remove_re = re.compile(r'\[.+\,.+\]$')

    device = app_commands.Group(
        name="device", description="Interact with tags", guild_ids=[cfg.guild_id])

    # TODO: device transformer?
    # TODO: version transformer?
    @ensure_invokee_role_lower_than_bot()
    @device.command(description="Add device to nickname")
    @app_commands.describe(device="Name of your device")
    @app_commands.autocomplete(device=device_autocomplete)
    @app_commands.describe(version="Device OS version")
    @app_commands.autocomplete(version=ios_on_device_autocomplete)
    @transform_context
    @always_whisper
    async def add(self, ctx: BlooContext, device: str, version: str) -> None:
        pass
        new_nick = ctx.author.display_name
        # check if user already has a device in their nick
        if re.match(self.devices_test, ctx.author.display_name):
            # they already have a device set
            view = Confirm(ctx, true_response="Alright, we'll swap your device!",
                           false_response="Cancelled adding device to your name.")
            await ctx.respond('You already have a device in your nickname. Would you like to replace it?', view=view, ephemeral=True)
            # Wait for the View to stop listening for input...
            await view.wait()
            change_name = view.value

            if change_name:
                # user wants to remove existing device, let's do that
                new_nick = re.sub(self.devices_remove_re, "",
                                  ctx.author.display_name).strip()
                if len(new_nick) > 32:
                    raise commands.BadArgument("Nickname too long")
            else:
                return

        response = await get_ios_cfw()
        device_groups = response.get("group")

        transformed_groups = transform_groups(device_groups)
        devices = [group for group in transformed_groups if group.get(
            'name').lower() == device.lower() or device.lower() in [x.lower() for x in group.get('devices')]]

        if not devices:
            raise commands.BadArgument("No device found with that name.")

        matching_device = devices[0]
        board = devices[0].get("devices")[0]

        ios = response.get("ios")
        ios = [i for _, i in ios.items()]
        version = version.replace("iOS ", "")
        firmware = [v for v in ios if board in v.get(
            'devices') and version == v.get('version')]

        if not firmware:
            raise commands.BadArgument("No firmware found with that version.")

        firmware = firmware[0].get('version')
        # change the user's nickname!
        if firmware is not None:
            firmware = re.sub(r' beta (\d+)', r'b\1', firmware)
            detailed_device = response.get("device").get(
                matching_device.get("devices")[0])
            name = detailed_device["soc"]
            new_nick = f"{new_nick} [{name}, {firmware}]"

            if len(new_nick) > 32:
                raise commands.BadArgument(
                    f"Discord's nickname character limit is 32. `{discord.utils.escape_markdown(new_nick)}` is too long.")

            await ctx.author.edit(nick=new_nick)
            await ctx.send_success(f"Changed your nickname to `{discord.utils.escape_markdown(new_nick)}`!")

    @ensure_invokee_role_lower_than_bot()
    @device.command(description="Remove device from nickname")
    @transform_context
    @always_whisper
    async def remove(self, ctx: BlooContext) -> None:
        if not re.match(self.devices_test, ctx.author.display_name):
            raise commands.BadArgument("You don't have a device nickname set!")

        new_nick = re.sub(self.devices_remove_re, "",
                          ctx.author.display_name).strip()
        if len(new_nick) > 32:
            raise commands.BadArgument("Nickname too long")

        await ctx.author.edit(nick=new_nick)
        await ctx.send_success("Removed device from your nickname!")

    @device.command(name="list", description="List all devices you can set your nickname to")
    @transform_context
    @whisper
    async def _list(self, ctx: BlooContext) -> None:
        devices_dict = defaultdict(list)

        response = await get_ios_cfw()
        devices = response.get("group")
        devices_transformed = transform_groups(devices)

        for device in devices_transformed:
            device_type = device.get("type")
            if device_type == "TV":
                devices_dict['Apple TV'].append(device)
            elif device_type == "Watch":
                devices_dict['Apple Watch'].append(device)
            else:
                devices_dict[device_type].append(device)

        embed = discord.Embed(title="Devices list")
        embed.color = discord.Color.blurple()
        for key, devices in devices_dict.items():
            devices.sort(key=lambda x: x.get('order'))
            devices = [device.get("name") for device in devices]
            embed.add_field(name=key, value=', '.join(
                devices), inline=False)

        embed.set_footer(text="Powered by https://ios.cfw.guide")
        await ctx.respond(embed=embed, ephemeral=ctx.whisper)


async def setup(bot):
    await bot.add_cog(Devices(bot))
