import discord
from discord import app_commands
from data.model import FilterWord
from data.services import guild_service, user_service
from discord.ext import commands
from utils import GIRContext, cfg, transform_context
from utils.framework import (admin_and_up, always_whisper, gatekeeper,
                             mod_and_up)
from utils.views import Menu, filterwords_autocomplete


def format_filter_page(_, entries, current_page, all_pages):
    """Formats the page for the filtered words embed

    Parameters
    ----------
    entry : dict
        "The dictionary for the entry"
    all_pages : list
        "All entries that we will eventually iterate through"
    current_page : number
        "The number of the page that we are currently on"

    Returns
    -------
    discord.Embed
        "The embed that we will send"

    """
    embed = discord.Embed(
        title=f'Filtered words', color=discord.Color.blurple())
    for word in entries:
        notify_flag = ""
        piracy_flag = ""
        flags_check = ""
        if word.notify is True:
            notify_flag = "🔔"
        if word.piracy:
            piracy_flag = " 🏴‍☠️"
        if word.notify is False and not word.piracy:
            flags_check = "None"
        embed.add_field(
            name=word.word, value=f"Bypassed by: {gatekeeper.level_info(word.bypass)}\nFlags: {flags_check}{notify_flag}{piracy_flag}")
    embed.set_footer(
        text=f"Page {current_page} of {len(all_pages)}")
    return embed


class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @mod_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Toggles bot pinging for reports when offline.")
    @app_commands.describe(val="True for ping, false for not")
    @transform_context
    @always_whisper
    async def offlineping(self, ctx: GIRContext, val: bool = None):
        cur = user_service.get_user(ctx.author.id)

        if val is None:
            val = not cur.offline_report_ping

        cur.offline_report_ping = val
        cur.save()

        if val:
            await ctx.send_success("You will now be pinged for reports when offline")
        else:
            await ctx.send_warning("You will no longer be pinged for reports when offline")

    _filter = app_commands.Group(name="filter", description="Interact with filter", guild_ids=[cfg.guild_id])

    @mod_and_up()
    @_filter.command(description="Add a word to filter")
    @app_commands.describe(notify="Whether to generate a report or not when this word is filtered")
    @app_commands.describe(bypass="The level of bypass for this word")
    @app_commands.choices(bypass=[app_commands.Choice(name=name, value=key) for key, name in gatekeeper._permission_names.items()])
    @app_commands.describe(phrase="The word to filter")
    @transform_context
    async def add(self, ctx: GIRContext, notify: bool, bypass: int, phrase: str) -> None:
        fw = FilterWord()
        fw.bypass = bypass
        fw.notify = notify
        fw.word = phrase

        if bypass == 1:
            try:
                rule = await ctx.guild.fetch_automod_rule(guild_service.get_guild().automod_memberplus_id)
                rule_id = await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=rule.trigger.keyword_filter + [f"*{phrase}*"]))
                rule_id = rule_id.id
                fw.automod_rule_id = rule_id
            except:
                pass
            
            # rule_id = await ctx.guild.create_automod_rule(name=f"Filter Word for: {phrase}", event_type=discord.AutoModRuleEventType.message_send,
            #     trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.keyword,
            #     keyword_filter=[f"*{phrase}*"]), actions=[discord.AutoModRuleAction(channel_id=guild_service.get_guild().channel_automod_log),
            #     discord.AutoModRuleAction()],
            #     enabled=True, exempt_roles=[ctx.guild.get_role(guild_service.get_guild().role_memberplus), ctx.guild.get_role(guild_service.get_guild().role_memberpro), ctx.guild.get_role(guild_service.get_guild().role_memberedition),
            #                                 ctx.guild.get_role(guild_service.get_guild().role_genius),
            #     ctx.guild.get_role(guild_service.get_guild().role_moderator), ctx.guild.get_role(guild_service.get_guild().role_administrator)], reason=f"Automod rule for filter word {phrase}")
            # fw.automod_rule_id = rule_id.id
            
        if bypass == 2:
            try:
                rule = await ctx.guild.fetch_automod_rule(guild_service.get_guild().automod_memberpro_id)
                rule_id = await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=rule.trigger.keyword_filter + [f"*{phrase}*"]))
                rule_id = rule_id.id
                fw.automod_rule_id = rule_id
            except:
                pass
            # rule_id = await ctx.guildcord.create_automod_rule(name=f"Filter Word for: {phrase}", event_type=discord.AutoModRuleEventType.message_send,
            #     trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.keyword,
            #     keyword_filter=[f"*{phrase}*"]), actions=[discord.AutoModRuleAction(channel_id=guild_service.get_guild().channel_automod_log),
            #     discord.AutoModRuleAction()],
            #     enabled=True, exempt_roles=[ctx.guild.get_role(guild_service.get_guild().role_memberpro), ctx.guild.get_role(guild_service.get_guild().role_memberedition),
            #                                 ctx.guild.get_role(guild_service.get_guild().role_genius),
            #     ctx.guild.get_role(guild_service.get_guild().role_moderator), ctx.guild.get_role(guild_service.get_guild().role_administrator)], reason=f"Automod rule for filter word {phrase}")
            # fw.automod_rule_id = rule_id.id

        if bypass == 4:
            try:
                rule = await ctx.guild.fetch_automod_rule(guild_service.get_guild().automod_genius_id)
                rule_id = await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=rule.trigger.keyword_filter + [f"*{phrase}*"]))
                rule_id = rule_id.id
                fw.automod_rule_id = rule_id
            except:
                pass
            # rule_id = await ctx.guild.create_automod_rule(name=f"Filter Word for: {phrase}", event_type=discord.AutoModRuleEventType.message_send,
            #     trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.keyword,
            #     keyword_filter=[f"*{phrase}*"]), actions=[discord.AutoModRuleAction(channel_id=guild_service.get_guild().channel_automod_log),
            #     discord.AutoModRuleAction()],
            #     enabled=True, exempt_roles=[ctx.guild.get_role(guild_service.get_guild().role_genius),
            #     ctx.guild.get_role(guild_service.get_guild().role_moderator), ctx.guild.get_role(guild_service.get_guild().role_administrator)], reason=f"Automod rule for filter word {phrase}")
            # fw.automod_rule_id = rule_id.id

        if bypass == 5:
            try:
                rule = await ctx.guild.fetch_automod_rule(guild_service.get_guild().automod_moderator_id)
                rule_id = await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=rule.trigger.keyword_filter + [f"*{phrase}*"]))
                rule_id = rule_id.id
                fw.automod_rule_id = rule_id
            except:
                pass
            # rule_id = await ctx.guild.create_automod_rule(name=f"Filter Word for: {phrase}", event_type=discord.AutoModRuleEventType.message_send,
            #     trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.keyword,
            #     keyword_filter=[f"*{phrase}*"]), actions=[discord.AutoModRuleAction(channel_id=guild_service.get_guild().channel_automod_log),
            #     discord.AutoModRuleAction()],
            #     enabled=True, exempt_roles=[
            #     ctx.guild.get_role(guild_service.get_guild().role_moderator), ctx.guild.get_role(guild_service.get_guild().role_administrator)], reason=f"Automod rule for filter word {phrase}")
            # fw.automod_rule_id = rule_id.id

        if bypass == 6:
            try:
                rule = await ctx.guild.fetch_automod_rule(guild_service.get_guild().automod_admin_id)
                rule_id = await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=rule.trigger.keyword_filter + [f"*{phrase}*"]))
                rule_id = rule_id.id
                fw.automod_rule_id = rule_id
            except:
                pass
            # rule_id = await ctx.guild.create_automod_rule(name=f"Filter Word for: {phrase}", event_type=discord.AutoModRuleEventType.message_send,
            #     trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.keyword,
            #     keyword_filter=[f"*{phrase}*"]), actions=[discord.AutoModRuleAction(channel_id=guild_service.get_guild().channel_automod_log),
            #     discord.AutoModRuleAction()],
            #     enabled=True, exempt_roles=[ctx.guild.get_role(guild_service.get_guild().role_administrator)], reason=f"Automod rule for filter word {phrase}")
            # fw.automod_rule_id = rule_id.id

        if bypass >= 7:
            try:
                rule = await ctx.guild.fetch_automod_rule(guild_service.get_guild().automod_everyone_id)
                rule_id = await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=rule.trigger.keyword_filter + [f"*{phrase}*"]))
                rule_id = rule_id.id
                fw.automod_rule_id = rule_id
            except:
                pass
            # rule_id = await ctx.guild.create_automod_rule(name=f"Filter Word for: {phrase}", event_type=discord.AutoModRuleEventType.message_send,
            #     trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.keyword,
            #     keyword_filter=[f"*{phrase}*"]), actions=[discord.AutoModRuleAction(channel_id=guild_service.get_guild().channel_automod_log),
            #     discord.AutoModRuleAction()],
            #     enabled=True, exempt_roles=[], reason=f"Automod rule for filter word {phrase}")
            # fw.automod_rule_id = rule_id.id

        if not guild_service.add_filtered_word(fw):
            raise commands.BadArgument("That word is already filtered!")

        phrase = discord.utils.escape_markdown(phrase)
        phrase = discord.utils.escape_mentions(phrase)

        await ctx.send_success(title="Added new word to filter!", description=f"This filter {'will' if notify else 'will not'} ping for reports, level {bypass} can bypass it, and the phrase is `{phrase}`")

    @mod_and_up()
    @_filter.command(description="List filtered words", name="list")
    @transform_context
    async def _list(self, ctx: GIRContext):
        filters = guild_service.get_guild().filter_words
        if len(filters) == 0:
            raise commands.BadArgument(
                "The filterlist is currently empty. Please add a word using `/filter`.")

        filters = sorted(filters, key=lambda word: word.word.lower())

        menu = Menu(ctx, filters, per_page=12,
                    page_formatter=format_filter_page, whisper=False)
        await menu.start()

    @mod_and_up()
    @app_commands.describe(word="The word to mark as piracy")
    @app_commands.autocomplete(word=filterwords_autocomplete)
    @transform_context
    async def piracy(self, ctx: GIRContext, word: str):
        word = word.lower()

        words = guild_service.get_guild().filter_words
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))

        if len(words) > 0:
            words[0].piracy = not words[0].piracy
            guild_service.update_filtered_word(words[0])

            await ctx.send_success("Marked as a piracy word!" if words[0].piracy else "Removed as a piracy word!")
        else:
            await ctx.send_warning("You must filter that word before it can be marked as piracy.", delete_after=5)

    @mod_and_up()
    @_filter.command(description="Remove word from filter")
    @app_commands.describe(word="The word to remove")
    @app_commands.autocomplete(word=filterwords_autocomplete)
    @transform_context
    async def remove(self, ctx: GIRContext, word: str):
        word = word.lower()

        words = guild_service.get_guild().filter_words
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))

        if len(words) > 0:
            try:
                if ctx.guild.fetch_automod_rule(words[0].automod_rule_id):
                    await (await ctx.guild.fetch_automod_rule(words[0].automod_rule_id)).delete()
            except:
                pass
            guild_service.remove_filtered_word(words[0].word)
            await ctx.send_success("Deleted!")
        else:
            await ctx.send_warning("That word is not filtered.", delete_after=5)

    @admin_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Whitelist a guild from invite filter")
    @app_commands.describe(guild_id="The guild to whitelist")
    @transform_context
    async def whitelist(self, ctx: GIRContext, guild_id: str):
        try:
            guild_id = int(guild_id)
        except ValueError:
            raise commands.BadArgument("Invalid ID!")

        if guild_service.add_whitelisted_guild(guild_id):
            await ctx.send_success("Whitelisted.")
        else:
            await ctx.send_warning("That server is already whitelisted.", delete_after=5)

    @admin_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Add a guild back to invite filter")
    @app_commands.describe(guild_id="The guild to blacklist")
    @transform_context
    async def blacklist(self, ctx: GIRContext, guild_id: str):
        try:
            guild_id = int(guild_id)
        except ValueError:
            raise commands.BadArgument("Invalid ID!")

        if guild_service.remove_whitelisted_guild(guild_id):
            await ctx.send_success("Blacklisted.")
        else:
            await ctx.send_warning("That server is already blacklisted.", delete_after=5)

    @admin_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Ignore channel in filter")
    @app_commands.describe(channel="Channel to ignore")
    @transform_context
    async def ignorechannel(self, ctx: GIRContext, channel: discord.TextChannel) -> None:
        if guild_service.add_ignored_channel(channel.id):
            await ctx.send_success(f"The filter will no longer run in {channel.mention}.")
        else:
            await ctx.send_warning("That channel is already ignored.", delete_after=5)

    @admin_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Ungnore channel in filter")
    @app_commands.describe(channel="Channel to unignore")
    @transform_context
    async def unignorechannel(self, ctx: GIRContext, channel: discord.TextChannel) -> None:
        if guild_service.remove_ignored_channel(channel.id):
            await ctx.send_success(f"Resumed filtering in {channel.mention}.")
        else:
            await ctx.send_warning("That channel is not already ignored.", delete_after=5)
   
    @admin_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Ignore channel in logs")
    @app_commands.describe(channel="Channel to ignore")
    @transform_context
    async def ignorechannellogs(self, ctx: GIRContext, channel: discord.TextChannel) -> None:
        if guild_service.add_ignored_channel_logging(channel.id):
            await ctx.send_success(f"{channel.mention} will no longer be logged.")
        else:
            await ctx.send_warning("That channel is already ignored.", delete_after=5)

    @admin_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Ungnore channel in logs")
    @app_commands.describe(channel="Channel to unignore")
    @transform_context
    async def unignorechannellogs(self, ctx: GIRContext, channel: discord.TextChannel) -> None:
        if guild_service.remove_ignored_channel_logging(channel.id):
            await ctx.send_success(f"Resumed logging in {channel.mention}.")
        else:
            await ctx.send_warning("That channel is not already ignored.", delete_after=5)

    @mod_and_up()
    @app_commands.guilds(cfg.guild_id)
    @app_commands.command(description="Disable enhanced filter checks on a word")
    @app_commands.describe(word="The word to disable")
    @app_commands.autocomplete(word=filterwords_autocomplete)
    @transform_context
    async def falsepositive(self, ctx: GIRContext, *, word: str):
        word = word.lower()

        words = guild_service.get_guild().filter_words
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))

        if len(words) > 0:
            words[0].false_positive = not words[0].false_positive
            if guild_service.update_filtered_word(words[0]):
                await ctx.send_success("Marked as potential false positive, we won't perform the enhanced checks on it!" if words[0].false_positive else "Removed as potential false positive.")
            else:
                raise commands.BadArgument(
                    "Unexpected error occured trying to mark as false positive!")
        else:
            await ctx.send_warning("That word is not filtered.", delete_after=5)


async def setup(bot):
    await bot.add_cog(Filters(bot))
