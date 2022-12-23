import os
import random

import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from dotenv import load_dotenv

from Models.MythicMadness import MythicMadness

load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

MY_GUILD = discord.Object(id=GUILD_ID)  # replace with your guild id

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client = MyClient(intents=discord.Intents.all())

#------------------------------------------------Commands------------------------------------------------------#

@client.tree.command()
@commands.has_permissions(manage_messages=True)
async def testingmadness(interaction: discord.Interaction, channel: discord.TextChannel):
    if channel is not None:
        await interaction.response.send_message(f"The Madness is Runnin’ Wild!")
        await BeginMythicPlusMadness(interaction, channel)
    else:
        await interaction.response.send_message(f"channel not found: {channel} {interaction.user.mention}")

@client.tree.command()
async def madness(interaction: discord.Interaction, channel: discord.VoiceChannel):
    if channel is not None:
        await interaction.response.send_message(f"The Madness is Runnin’ Wild!")
        await BeginMythicPlusMadness(interaction, channel)
    else:
        await interaction.response.send_message(f"channel not found: {channel} {interaction.user.mention}")

#-----------------------------------------Functions---------------------------------------------------------------#

async def BeginMythicPlusMadness(interaction: discord.Interaction, channel):
    try:
        #Get each role

        madness = MythicMadness(interaction, channel)
        madness.CreateGroups()
        madness.AssignPlayersToGroups()
        madness.AssignGroupsVoiceChannel(interaction.guild.voice_channels)
        await OutputMadness(interaction, madness, channel)

        if(madness.CountMembers(HasRole=False) > 0):
            await OutputLackingMadness(interaction, madness, channel)

        await interaction.channel.send(f"Good Luck and Have Fun! {interaction.user.mention}")
         

    except Exception as error:
        print(repr(error))

async def OutputLackingMadness(interaction: discord.Interaction, madness: MythicMadness, channel):
    await interaction.channel.send(f"Those who lack MADNESS in channel [<#{channel.id}>]: {madness.CountMembers(HasRole=False)}")

    if (madness.CountMembers(HasRole=False) > 0):
        roleChannel = None
        for v in interaction.guild.text_channels:
            if v.name.lower() == "roles":
                roleChannel = v
                break

        if(roleChannel is not None):
            await interaction.channel.send(f"Missing roles: {' '.join([m.MythicMember.mention for m in list(filter(lambda x : x.HasRole == False, madness.MembersOfMadness))])}")
            await interaction.channel.send(f"Head over to [<#{roleChannel.id}>] and grab {madness.TankEmoji}/{madness.HealerEmoji}/{madness.DPSEmoji}")  

async def OutputMadness(interaction: discord.Interaction, madness: MythicMadness, channel):
    for group in madness.MythicGroups:
        await interaction.channel.send(group.ToString(madness.TankEmoji, madness.HealerEmoji, madness.DPSEmoji, madness.randomEmoji))

    if (len(madness.TankRole.Members) > 0):
        await interaction.channel.send(f"Opps! TankRole not assigned: {' '.join([m.MythicMember.mention for m in madness.TankRole.Members])}")
    if (len(madness.HealerRole.Members) > 0):
        await interaction.channel.send(f"Opps! Healer not assigned: {' '.join([m.MythicMember.mention for m in madness.HealerRole.Members])}")
    if (len(madness.DPSRole.Members) > 0):
        await interaction.channel.send(f"Opps! DPS not assigned: {' '.join([m.MythicMember.mention for m in madness.DPSRole.Members])}")

    await interaction.channel.send(f"Members of Madness in [<#{channel.id}>]: {madness.CountMembers(HasRole=True)}")

client.run(TOKEN)
