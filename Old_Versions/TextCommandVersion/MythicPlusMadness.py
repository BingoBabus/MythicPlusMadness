import discord
from discord.ext import tasks, commands
from discord.utils import get
from dotenv import load_dotenv
import asyncio
import os
import random
import math

#For a more secure, we loaded the .env file and assign the token value to a variable 
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

#Intents are permissions for the bot that are enabled based on the features necessary to run the bot.
intents=discord.Intents.all()

#Comman prefix is setup here, this is what you have to type to issue a command to the bot
prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)

#Removed the help command to create a custom help guide
bot.remove_command('help')

_roleTank = 'tank'
_roleDPS = 'dps'
_roleHealer = 'healer'
_defaultChannel = 'cream of the crop'

#------------------------------------------------Commands------------------------------------------------------#

@bot.command()
@commands.has_permissions(manage_messages=True)
async def Madness(ctx, arg=_defaultChannel):

    channel = discord.utils.get(ctx.guild.channels, name=arg)

    if channel is not None:

        membersInChannel = [m for m in channel.members] 
        
        if len(membersInChannel) == 0:
            await ctx.channel.send(f"Hey, no one is in the {channel}!")
            return

        MembersReadyForMadness = []
        for member in membersInChannel:
            if (get(member.roles, name=_roleTank) or 
                get(member.roles, name=_roleHealer) or
                get(member.roles, name=_roleDPS)):
                MembersReadyForMadness.append(member)

        if len(MembersReadyForMadness) == 0:
            await ctx.channel.send(f"Hey, no one has the role {_roleTank}, {_roleHealer}, or {_roleDPS} in channel: {channel}!")
            return              

        await ctx.channel.send("Members Ready For Madness: {0}".format(len(MembersReadyForMadness)))

        await StartMythicPlusMadness(ctx, channel, MembersReadyForMadness)

    else:
        print("Not Found: {0}".format(channel))

# #-----------------------------------------Functions---------------------------------------------------------------#

#Check for any groups with 2 or less memebers
#steal a dps from groups with at least 4 members
async def CheckGroupBalance(ctx, Groups):

    #Find groups of <=2 players
    for x in filter(lambda y: len(y) <= 2 and len(y) > 0, Groups):

        #Fill small group by stealing players from filled groups until at least 3 members
        while True:
            filledGroups = next(filter(lambda y: len(y) > 3, Groups), None)

            if (filledGroups is not None):
                first = next(filter(lambda y: y.__contains__("[D]"), filledGroups), None)
                x.append(first)
                filledGroups.remove(first)

                if len(x) > 2:
                    break
            else:
                break
        
#Fill Groups with Tanks, Healers, and DPS
#When selecting a player for a role, prioritize players with only a single role selected for initial fills
async def CreateMythicPlusGroups(ctx, sTanks, tanks, sHealers, healers, sDPS, dps, numberOfGroups):
    Groups = []

    #Tanks
    await FillTank(Groups, sTanks, tanks, sHealers, healers, sDPS, dps, numberOfGroups)

    #Healers
    await FillHealer(Groups, sTanks, tanks, sHealers, healers, sDPS, dps)

    #DPS
    await FillDPS(Groups, sTanks, tanks, sHealers, healers, sDPS, dps)

    if (len(sDPS) > 0 or len(dps) > 0):
        groupNum = 0
        
        for d in dps:
            Group = Groups[groupNum]
            await FillDPS(Groups, sTanks, tanks, sHealers, healers, sDPS, dps)
            groupNum+=1
            if groupNum == numberOfGroups: 
                groupNum = 0

    if(len(Groups) > 1):
        await CheckGroupBalance(ctx, Groups)

    await OutputGroups(ctx, Groups)
    await ctx.send("Good Luck and Have Fun :P")

async def DebugLogRoles(ctx, role, membersWithOnlyThisRole, membersWithRole):
    await ctx.send(f"Only {role.name}: {len(membersWithOnlyThisRole)}")
    await ctx.send(f"Total {role.name}: {len(role.members)}")
    await ctx.send(f"{role.name}: {' '.join([m.name for m in membersWithRole])}")

#Find quotient and the remainder of the numbers of players in the channel by groups of 5
#if there is a remainder then numbers of groups will be quotient + 1
async def DetermineNumberOfGroups(ctx, membersInChannel):
    leftOverMembers = divmod(len(membersInChannel), 5)
    numGroups = 0
    if leftOverMembers[1] == 0:
        numGroups = leftOverMembers[0]
    else:
        numGroups = leftOverMembers[0] + 1
    
    # await ctx.send(f"We will have {numGroups} groups")
    # await ctx.send(f"We will need {numGroups} tanks")
    # await ctx.send(f"We will need {numGroups} healers")
    # await ctx.send(f"We will need {numGroups * 3 } dps")

    return numGroups    

async def FillDPS(Groups, sTanks, tanks, sHealers, healers, sDPS, dps):
    for Group in Groups:
        if len(sDPS) > 0:
            random.shuffle(sDPS)
            Group.append(f"[D] {sDPS[0].mention}")        

            await RemoveMemberFromSelection(sDPS[0], sTanks, tanks, sHealers, healers, sDPS, dps)
        elif len(dps) > 0:
            random.shuffle(dps)
            Group.append(f"[D] {dps[0].mention}")        

            await RemoveMemberFromSelection(dps[0], sTanks, tanks, sHealers, healers, sDPS, dps)
        # else:
        #     Group.append("[D] Pug")   

async def FillHealer(Groups, sTanks, tanks, sHealers, healers, sDPS, dps):
    for Group in Groups:
        if len(sHealers) > 0:
            random.shuffle(sHealers)
            Group.append(f"[H] {sHealers[0].mention}")     

            await RemoveMemberFromSelection(sHealers[0], sTanks, tanks, sHealers, healers, sDPS, dps)
        elif len(healers) > 0:
            random.shuffle(healers)
            Group.append(f"[H] {healers[0].mention}")        
            
            await RemoveMemberFromSelection(healers[0], sTanks, tanks, sHealers, healers, sDPS, dps)
        # else:
        #     Group.append("[H] Pug")  

async def FillTank(Groups, sTanks, tanks, sHealers, healers, sDPS, dps, numberOfGroups):
    for x in range(numberOfGroups):
        Group = []
        if len(sTanks) > 0:
            random.shuffle(sTanks)
            Group.append(f"[T] {sTanks[0].mention}")     
            
            await RemoveMemberFromSelection(sTanks[0], sTanks, tanks, sHealers, healers, sDPS, dps)
        elif len(tanks) > 0:
            random.shuffle(tanks)
            Group.append(f"[T] {tanks[0].mention}")        

            await RemoveMemberFromSelection(tanks[0], sTanks, tanks, sHealers, healers, sDPS, dps)
        # else:
        #     Group.append("[T] Pug")    

        Groups.append(Group)

#Get List of Members with Role and in the Voice Channel
async def GetRoleInChannel(ctx, role, channel, membersInChannel):
    rMembers = [m for m in role.members]
    rMembersInChannel = []

    if(len(rMembers) > 0):
        rMembersInChannel = list(filter(lambda rMembers: rMembers in membersInChannel, rMembers))

    return rMembersInChannel

#Get list of members with ONLY the role
async def GetSoloRoleMembers(membersWithRole, NotRoles):
    MembersWithSoloRole = []
    for member in membersWithRole:
        if (not get(member.roles, name=NotRoles[0]) and not get(member.roles, name=NotRoles[1])):
            MembersWithSoloRole.append(member)
    return MembersWithSoloRole

async def GetVoiceChannel(voiceChannels):
    random.shuffle(voiceChannels)
    return voiceChannels[0]

async def OutputGroups(ctx, Groups):
    voiceChannels = ctx.guild.voice_channels

    if(len(Groups) > 0):
        length_lst = [len(item) for row in Groups for item in row]

        if(len(length_lst) > 0):
            col_wdth = max(length_lst)

            i=1
            for row in Groups:    
                voiceChannel = await GetVoiceChannel(voiceChannels)    

                await ctx.channel.send(f"G[{i}][<#{voiceChannel.id}>]: {''.join(item.ljust(col_wdth + 2) for item in row)}")
                voiceChannels.remove(voiceChannel)
                i = i + 1

#When a member is assigned remove them from all remaining role pools
async def RemoveMemberFromSelection(member, sTanks, tanks, sHealers, healers, sDPS, dps):
        if member in sTanks: sTanks.remove(member)
        if member in tanks: tanks.remove(member)
        if member in sHealers: sHealers.remove(member)
        if member in healers: healers.remove(member)
        if member in sDPS: sDPS.remove(member)
        if member in dps: dps.remove(member)

async def StartMythicPlusMadness(ctx, channel, membersInChannel):

    #Get each role
    rTank = discord.utils.get(ctx.guild.roles, name=_roleTank)
    rDPS = discord.utils.get(ctx.guild.roles, name=_roleDPS)
    rHealer = discord.utils.get(ctx.guild.roles, name=_roleHealer)

    if rTank is None:
        await ctx.channel.send("There is no {0} role on this server!".format(_roleTank))
    if rHealer is None:
        await ctx.channel.send("There is no {0} role on this server!".format(_roleHealer))
    if rDPS is None:
        await ctx.channel.send("There is no {0} role on this server!".format(_roleDPS))
    
    tanks = await GetRoleInChannel(ctx, rTank, channel, membersInChannel)
    healers = await GetRoleInChannel(ctx, rHealer, channel, membersInChannel)
    dps = await GetRoleInChannel(ctx, rDPS, channel, membersInChannel)

    sTanks = await GetSoloRoleMembers(tanks, [rDPS.name, rHealer.name])
    sHealers = await GetSoloRoleMembers(healers, [rDPS.name, rTank.name])
    sDPS = await GetSoloRoleMembers(dps, [rTank.name, rHealer.name])
    
    # await DebugLogRoles(ctx, rTank, sTanks, tanks)
    # await DebugLogRoles(ctx, rHealer, sHealers, healers)
    # await DebugLogRoles(ctx, rDPS, sDPS, dps)

    numberOfGroups = await DetermineNumberOfGroups(ctx, membersInChannel)

    await CreateMythicPlusGroups(ctx, sTanks, tanks, sHealers, healers, sDPS, dps, numberOfGroups)

#Run the bot
bot.run(TOKEN)
