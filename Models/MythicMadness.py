import os
import discord
import random
from discord.utils import get
from dotenv import load_dotenv

from Models.PartyRole import PartyRole
from Models.MadnessMember import MadnessMember
from Models.MythicGroup import MythicGroup

load_dotenv(".env")
ROLE_NAME_TANK = os.getenv("ROLE_NAME_TANK")
ROLE_NAME_HEALER = os.getenv("ROLE_NAME_HEALER")
ROLE_NAME_DPS = os.getenv("ROLE_NAME_DPS")
EMOJI_NAME_TANK = os.getenv("EMOJI_NAME_TANK")
EMOJI_NAME_HEALER = os.getenv("EMOJI_NAME_HEALER")
EMOJI_NAME_DPS = os.getenv("EMOJI_NAME_DPS")

class MythicMadness:
    NumGroups = 0
    MythicGroups = []
    MembersOfMadness = []
    TankRole = PartyRole
    HealerRole = PartyRole
    DPSRole = PartyRole
    TankEmoji = discord.Emoji
    HealerEmoji = discord.Emoji
    DPSEmoji = discord.Emoji
    randomEmoji = [discord.Emoji]

    # Constractor of the class
    # Figure out Server Roles, who has which roles, and how many members are in the channel
    def __init__(self, interaction: discord.Interaction, channel):
        self.MembersOfMadness = []
        self.TankRole = PartyRole(interaction.guild.roles, ROLE_NAME_TANK)
        self.HealerRole = PartyRole(interaction.guild.roles, ROLE_NAME_HEALER)
        self.DPSRole = PartyRole(interaction.guild.roles, ROLE_NAME_DPS) 
        self.TankEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_TANK)
        self.HealerEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_HEALER)
        self.DPSEmoji = discord.utils.get(interaction.guild.emojis, name=EMOJI_NAME_DPS)
        
        emojis = list(filter(lambda x : x not in (self.TankEmoji, self.HealerEmoji, self.DPSEmoji), interaction.guild.emojis))
        #[e for e in interaction.guild.emojis if self.TankEmoji not in e.roles and self.HealerEmoji not in e.roles and self.DPSEmoji not in e.roles]
        # random.shuffle(emojis)
        self.randomEmoji = emojis

        self.CreatePoolOfMembersInChannel(channel)

    def AssignGroupsVoiceChannel(self, Channels):
        voiceChannels = []
        RemoveTheseChannels = ['afk']

         for v in Channels:
            if(v.name.lower() in RemoveTheseChannels) == False:
                voiceChannels.append(v)

        for group in self.MythicGroups:

            if(len(voiceChannels) > 0):
                random.shuffle(voiceChannels)
                voiceChannel = voiceChannels[0] 
                group.VoiceChannel = voiceChannel
                voiceChannels.remove(voiceChannel)
            else:
                break


    #First fill groups with tanks and healers. Afterward Assign DPS
    #We do not want a player with tank/healer choosen for DPS if there are still open slots for those roles amonst the groups
    def AssignPlayersToGroups(self):
        self.FillGroupsWithTanks(None)
        self.FillGroupsWithHealers(None)
        self.FillGroupsWithDPS(None)
        self.CreateGroupsForGrouplessMembers()
        self.BalanceGroups()

    def BalanceGroups(self):
        
        #Fill small group by stealing players from filled groups until at least 3 members
        for x in list(filter(lambda y: y.GroupCount() <= 2 and y.GroupCount() > 0, self.MythicGroups)):
            while True:
                filledGroups = next(filter(lambda z : z.GroupCount() > 3, self.MythicGroups), None)

                if (filledGroups is not None):
                    if (x.Tank is None and filledGroups.Tank):
                        x.Tank = filledGroups.Tank
                        filledGroups.Tank = None
                    elif (x.Healer is None and filledGroups.Healer):
                        x.Healer = filledGroups.Healer
                        filledGroups.Healer = None
                    elif (x.DPS1 is None and filledGroups.DPS1):
                        x.DPS1 = filledGroups.DPS1
                        filledGroups.DPS1 = None
                    elif (x.DPS2 is None and filledGroups.DPS2):
                        x.DPS2 = filledGroups.DPS2
                        filledGroups.DPS2 = None
                    elif (x.DPS3 is None and filledGroups.DPS3):
                        x.DPS3 = filledGroups.DPS3
                        filledGroups.DPS3 = None

                    if x.GroupCount() > 2:
                        break
                else:
                    break

        numTanks =  sum(map(lambda x : x.Tank is not None, self.MythicGroups))
        numHealers=  sum(map(lambda x : x.Healer is not None, self.MythicGroups))

        #If a group is full and there are any groups without a tank/healer than move tank to that group
        if(numTanks < self.NumGroups and numHealers < self.NumGroups):
            for m in list(filter(lambda x : x.Tank is None and x.Healer is None, self.MythicGroups)):
                filledGroup = next(filter(lambda x : x.Tank is not None and x.Healer is not None and x.DPS1 is not None and x.DPS2 is not None and x.DPS3 is not None, self.MythicGroups), None)

                if(filledGroup is not None):
                    m.Tank = filledGroup.Tank
                    filledGroup.Tank = None



    # Return the number of members in the channel according to HasRole parameter
    def CountMembers(self, HasRole: bool):
        return sum(map(lambda x : x.HasRole == HasRole, self.MembersOfMadness))

    #Determin the Number of Groups Required and Create them
    def CreateGroups(self):
        self.NumGroups = MythicMadness.DetermineNumberOfGroups(self)
        
        self.MythicGroups = []
        for x in range(self.NumGroups):
            self.MythicGroups.append(MythicGroup(x))

    def CreateGroupsForGrouplessMembers(self):
        while(len(self.FindLeftOvers()) > 0):
            newGroup = MythicGroup(self.NumGroups)
            self.MythicGroups.append(newGroup)
            self.NumGroups += 1

            self.FillGroupsWithTanks(newGroup)
            self.FillGroupsWithHealers(newGroup)
            self.FillGroupsWithDPS(newGroup)

    def CreatePoolOfMembersInChannel(self, channel):
        for member in channel.members:
            HasRole = False
            roles = []

            if (get(member.roles, name=self.TankRole.Role.name)):
                HasRole = True
                roles.append("T")
            if (get(member.roles, name=self.HealerRole.Role.name)):
                HasRole = True
                roles.append("H")  
            if (get(member.roles, name=self.DPSRole.Role.name)):
                HasRole = True
                roles.append("D")
                
            madnessMember = MadnessMember(member, HasRole, roles)

            if(madnessMember.Roles.__contains__("T")):
                self.TankRole.AddMember(madnessMember)
            if(madnessMember.Roles.__contains__("H")):
                self.HealerRole.AddMember(madnessMember)
            if(madnessMember.Roles.__contains__("D")):
                self.DPSRole.AddMember(madnessMember)

            self.MembersOfMadness.append(madnessMember)

    #Find quotient and the remainder of the numbers of players in the channel by groups of 5
    #if there is a remainder then numbers of groups will be quotient + 1
    def DetermineNumberOfGroups(self):
        players = MythicMadness.CountMembers(self, HasRole=True)
        leftOverMembers = divmod(players, 5)
        
        numGroups = 0
        if leftOverMembers[1] == 0:
            numGroups = leftOverMembers[0]
        else:
            numGroups = leftOverMembers[0] + 1
            
        return numGroups

    def FillGroupsWithDPS(self, group):
        PureDPS = [m for m in self.DPSRole.Members if self.HealerRole.Role not in m.MythicMember.roles and self.TankRole.Role not in m.MythicMember.roles]
        
        if(group is not None):
            for i in range(3):
                group.AddDPS(PureDPS, self.TankRole, self.HealerRole, self.DPSRole)
        else:
            for MythicGroup in self.MythicGroups:
                for i in range(3):
                    MythicGroup.AddDPS(PureDPS, self.TankRole, self.HealerRole, self.DPSRole)

    def FillGroupsWithHealers(self, group):
        PureHealer = [m for m in self.HealerRole.Members if self.DPSRole.Role not in m.MythicMember.roles and self.TankRole.Role not in m.MythicMember.roles]
        
        if(group is not None):
            group.AddHealer(PureHealer, self.TankRole, self.HealerRole, self.DPSRole)
        else:
            for MythicGroup in self.MythicGroups:
                MythicGroup.AddHealer(PureHealer, self.TankRole, self.HealerRole, self.DPSRole)

    def FillGroupsWithTanks(self, group):
        PURETANKS = [m for m in self.TankRole.Members if self.DPSRole.Role not in m.MythicMember.roles and self.HealerRole.Role not in m.MythicMember.roles]

        if(group is not None):
            group.AddTank(PURETANKS, self.TankRole, self.HealerRole, self.DPSRole)
        else:
            for MythicGroup in self.MythicGroups:
                MythicGroup.AddTank(PURETANKS, self.TankRole, self.HealerRole, self.DPSRole)

    def FindLeftOvers(self):
        leftOverMembers = []
        if (len(self.TankRole.Members) > 0):
            for m in self.TankRole.Members: leftOverMembers.append(m.MythicMember)
        if (len(self.HealerRole.Members) > 0):
            for m in self.HealerRole.Members: leftOverMembers.append(m.MythicMember)
        if (len(self.DPSRole.Members) > 0):
            for m in self.DPSRole.Members: leftOverMembers.append(m.MythicMember)
        
        return leftOverMembers

        



    
