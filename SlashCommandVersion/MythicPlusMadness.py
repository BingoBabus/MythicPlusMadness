import discord
from discord import app_commands
from discord.utils import get
from dotenv import load_dotenv

import random
import os

load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
ROLE_NAME_TANK = os.getenv("ROLE_NAME_TANK")
ROLE_NAME_HEALER = os.getenv("ROLE_NAME_HEALER")
ROLE_NAME_DPS = os.getenv("ROLE_NAME_DPS")
EMOJI_NAME_TANK = os.getenv("EMOJI_NAME_TANK")
EMOJI_NAME_HEALER = os.getenv("EMOJI_NAME_HEALER")
EMOJI_NAME_DPS = os.getenv("EMOJI_NAME_DPS")

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
async def madness(interaction: discord.Interaction, channel: discord.VoiceChannel):
    if channel is not None:
        await interaction.response.send_message(f"Good Luck and Have Fun :P {interaction.user.mention}")
        await BeginMythicPlusMadness(interaction, channel)
    else:
        print()
        await interaction.response.send_message(f"channel not found: {channel} {interaction.user.mention}")

#-----------------------------------------Functions---------------------------------------------------------------#

async def BeginMythicPlusMadness(interaction: discord.Interaction, channel: discord.VoiceChannel):
    
    #Get each role
    ROLE_TANK = discord.utils.get(interaction.guild.roles, name=ROLE_NAME_TANK)
    ROLE_HEALER = discord.utils.get(interaction.guild.roles, name=ROLE_NAME_HEALER)
    ROLE_DPS = discord.utils.get(interaction.guild.roles, name=ROLE_NAME_DPS)

    if ROLE_TANK is None:
        await interaction.response.send_message("There is no {0} role on this server!".format(ROLE_NAME_TANK))
        return
    if ROLE_HEALER is None:
        await interaction.response.send_message("There is no {0} role on this server!".format(ROLE_NAME_HEALER))
        return
    if ROLE_DPS is None:
        await interaction.response.send_message("There is no {0} role on this server!".format(ROLE_NAME_DPS))
        return

    MembersReadyForMadness = []
    MembersInVoiceWhoNeedRoles = []
    for member in channel.members:
        print(f"{member.name} roles: {' '.join([m.name for m in member.roles])}")

        if (get(member.roles, name=ROLE_TANK.name) or 
            get(member.roles, name=ROLE_HEALER.name) or
            get(member.roles, name=ROLE_DPS.name)):
            MembersReadyForMadness.append(member)
        else:
            MembersInVoiceWhoNeedRoles.append(member)
            

    TANKS = [m for m in MembersReadyForMadness if ROLE_TANK in m.roles]
    HEALERS = [m for m in MembersReadyForMadness if ROLE_HEALER in m.roles]
    DPS = [m for m in MembersReadyForMadness if ROLE_DPS in m.roles]

    PURE_TANKS = [m for m in TANKS if ROLE_DPS not in m.roles and ROLE_HEALER not in m.roles]
    PURE_HEALERS = [m for m in HEALERS if ROLE_DPS not in m.roles and ROLE_TANK not in m.roles]
    PURE_DPS = [m for m in DPS if ROLE_HEALER not in m.roles and ROLE_TANK not in m.roles]

    print(f"tanks: {len(TANKS)}")
    print(f"healers: {len(HEALERS)}")
    print(f"dps: {len(DPS)}")
    print(f"pure tank: {len(PURE_TANKS)}")
    print(f"pure healer: {len(PURE_HEALERS)}")
    print(f"pure dps: {len(PURE_DPS)}")

    await interaction.channel.send(f"Players in channel [<#{channel.id}>] Ready for Madness: {len(MembersReadyForMadness)}")

    numGroups = await DetermineNumberOfGroups(MembersReadyForMadness)
    
    await CreateGroups(interaction, numGroups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)     
    
    await TellPeopleToGetRoles(interaction, MembersInVoiceWhoNeedRoles)


#Fill Groups with Tanks, Healers, and DPS
#When selecting a player for a role, prioritize players with only a single role selected for initial fills
async def CreateGroups(interaction: discord.Interaction, numGroups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS):
    Groups = []

    TankEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_TANK)
    HealerEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_HEALER)
    DPSEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_DPS)

    for x in range(numGroups):
        Groups.append([])

    await FillTank(Groups, numGroups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS, TankEmoji)
    await FillHealer(Groups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS, HealerEmoji)
    await FillDPS(Groups, numGroups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS, DPSEmoji)

    await CheckGroupBalance(Groups, DPSEmoji)

    await OutputGroups(interaction, Groups)

    if (len(TANKS) > 0):
        await interaction.channel.send(f"Opps! {TankEmoji} not assigned: {' '.join([m.mention for m in TANKS])}")
    if (len(HEALERS) > 0):
        await interaction.channel.send(f"Opps! {HealerEmoji} not assigned: {' '.join([m.mention for m in HEALERS])}")
    if (len(DPS) > 0):
        await interaction.channel.send(f"Opps! {DPSEmoji} not assigned: {' '.join([m.mention for m in DPS])}")

    return

async def OutputGroups(interaction: discord.Interaction, Groups):
    voiceChannels = interaction.guild.voice_channels

    for v in interaction.guild.voice_channels:
        if v.name.lower() == "afk":
            voiceChannels.remove(v)
            break


    if(len(Groups) > 0):
        length_lst = [len(item) for row in Groups for item in row]

        if(len(length_lst) > 0):
            col_wdth = max(length_lst)

            i=1
            for row in Groups:    
                random.shuffle(voiceChannels)
                voiceChannel = voiceChannels[0] 

                await interaction.channel.send(f"G[{i}][<#{voiceChannel.id}>]: {''.join(item.ljust(col_wdth + 2) for item in row)}")
                voiceChannels.remove(voiceChannel)
                i = i + 1

async def TellPeopleToGetRoles(interaction: discord.Interaction, MembersInVoiceWhoNeedRoles):
    if (len(MembersInVoiceWhoNeedRoles) > 0):
        roleChannel = None
        for v in interaction.guild.text_channels:
            if v.name.lower() == "roles":
                roleChannel = v
                break
        

        if(roleChannel is not None):
            TankEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_TANK)
            HealerEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_HEALER)
            DPSEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_DPS)

            await interaction.channel.send(f"Missing roles: {' '.join([m.mention for m in MembersInVoiceWhoNeedRoles])}")
            await interaction.channel.send(f"Head over to [<#{roleChannel.id}>] and grab {TankEmoji}/{HealerEmoji}/{DPSEmoji}")
            

#----------------------------------------- Helper Functions---------------------------------------------------------------#

#Check for any groups with 2 or less memebers
#steal a dps from groups with at least 4 members
async def CheckGroupBalance(Groups, DPSEmoji: discord.Emoji):

    #Find groups of <=2 players
    for x in filter(lambda y: len(y) <= 2 and len(y) > 0, Groups):

        #Fill small group by stealing players from filled groups until at least 3 members
        while True:
            filledGroups = next(filter(lambda y: len(y) > 3, Groups), None)

            if (filledGroups is not None):
                first = next(filter(lambda y: y.__contains__(f"{DPSEmoji}"), filledGroups), None)
                x.append(first)
                filledGroups.remove(first)

                if len(x) > 2:
                    break
            else:
                break

#Find quotient and the remainder of the numbers of players in the channel by groups of 5
#if there is a remainder then numbers of groups will be quotient + 1
async def DetermineNumberOfGroups(membersInChannel):
    leftOverMembers = divmod(len(membersInChannel), 5)
    numGroups = 0
    if leftOverMembers[1] == 0:
        numGroups = leftOverMembers[0]
    else:
        numGroups = leftOverMembers[0] + 1
        
    return numGroups  

async def FillDPS(Groups, numGroups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS, DPSEmoji: discord.Emoji):
    groupNum = 0
    for x in range(len(DPS)):
        Group = Groups[groupNum]

        count = sum(map(lambda x : x.__contains__(f"{DPSEmoji}"), Group))
        if(count<3):

            if len(PURE_DPS) > 0:
                random.shuffle(PURE_DPS)
                print(f"pure dps assigned: {PURE_DPS[0].name} to Group {groupNum  + 1}")
                Group.append(f"{DPSEmoji} {PURE_DPS[0].mention}")        

                await RemoveMemberFromSelection(PURE_DPS[0], TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)
            elif len(DPS) > 0:
                random.shuffle(DPS)
                print(f" dps assigned: {DPS[0].name} to Group {groupNum  + 1}")
                Group.append(f"{DPSEmoji} {DPS[0].mention}")        

                await RemoveMemberFromSelection(DPS[0], TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)
            else:
                break

        groupNum+=1
        if groupNum == numGroups: 
            groupNum = 0   

async def FillHealer(Groups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS, HealerEmoji: discord.Emoji):
    for Group in Groups:
        if len(PURE_HEALERS) > 0:
            random.shuffle(PURE_HEALERS)
            print(f"pure healer assigned: {PURE_HEALERS[0].name} to Group {Groups.index(Group) + 1}")
            Group.append(f"{HealerEmoji} {PURE_HEALERS[0].mention}")     

            await RemoveMemberFromSelection(PURE_HEALERS[0], TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)
        elif len(HEALERS) > 0:
            random.shuffle(HEALERS)
            print(f" healer assigned: {HEALERS[0].name} to Group {Groups.index(Group) + 1}")
            Group.append(f"{HealerEmoji} {HEALERS[0].mention}")        
            
            await RemoveMemberFromSelection(HEALERS[0], TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)
        else:
            return

async def FillTank(Groups, numGroups, TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS, TankEmoji: discord.Emoji):
    for Group in Groups:
        if len(PURE_TANKS) > 0:
            random.shuffle(PURE_TANKS)
            print(f"pure tank assigned: {PURE_TANKS[0].name} to Group {Groups.index(Group) + 1}")
            Group.append(f"{TankEmoji} {PURE_TANKS[0].mention}")     
            
            await RemoveMemberFromSelection(PURE_TANKS[0], TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)
        elif len(TANKS) > 0:
            random.shuffle(TANKS)
            print(f" tank assigned: {TANKS[0].name} to Group {Groups.index(Group) + 1}")
            Group.append(f"{TankEmoji}  {TANKS[0].mention}")        

            await RemoveMemberFromSelection(TANKS[0], TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS)
        else:
            return

                
async def RemoveMemberFromSelection(member,  TANKS, PURE_TANKS, HEALERS, PURE_HEALERS, DPS, PURE_DPS):
        if member in TANKS: TANKS.remove(member)
        if member in PURE_TANKS: PURE_TANKS.remove(member)
        if member in HEALERS: HEALERS.remove(member)
        if member in PURE_HEALERS: PURE_HEALERS.remove(member)
        if member in DPS: DPS.remove(member)
        if member in PURE_DPS: PURE_DPS.remove(member)

client.run(TOKEN)
