import discord
import random
from Models.MadnessMember import MadnessMember
from Models.PartyRole import PartyRole

class MythicGroup:
    GroupNumber = None
    VoiceChannel = discord.VoiceChannel
    Tank = MadnessMember
    Healer = MadnessMember
    DPS1 = MadnessMember
    DPS2 = MadnessMember
    DPS3 = MadnessMember

    # Constractor of the class
    def __init__(self, GroupNumber):
        self.GroupNumber = GroupNumber
        self.VoiceChannel = None
        self.Tank = None
        self.Healer = None
        self.DPS1 = None
        self.DPS2 = None
        self.DPS3 = None
        self.Count = 0
    
    def AddDPS(self, PureDPS, Tank: PartyRole, Healer: PartyRole, DPS: PartyRole):
        dpsPlayer = self.FindPlayerForRole(DPS, PureDPS)   
        if(dpsPlayer is not None):
            if (self.DPS1 is None):
                self.DPS1 = dpsPlayer
            elif (self.DPS2 is None):
                self.DPS2 = dpsPlayer
            elif (self.DPS3 is None):
                self.DPS3 = dpsPlayer

            self.RemoveMemberFromSelection(dpsPlayer, Tank, Healer, DPS, PureDPS)

    def AddHealer(self, PureHealer, Tank: PartyRole, Healer: PartyRole, DPS: PartyRole):
        healerPlayer = self.FindPlayerForRole(Healer, PureHealer)
        if(healerPlayer is not None):
            self.Healer = healerPlayer
            self.RemoveMemberFromSelection(healerPlayer, Tank, Healer, DPS, PureHealer)

    def AddTank(self, PureTanks, Tank: PartyRole, Healer: PartyRole, DPS: PartyRole):
        tankPlayer = self.FindPlayerForRole(Tank, PureTanks)   
        if(tankPlayer is not None):
            self.Tank = tankPlayer
            self.RemoveMemberFromSelection(tankPlayer, Tank, Healer, DPS, PureTanks)

    def GroupCount(self):
        count = 0
        if(self.Tank is not None):
            count += 1
        if(self.Healer is not None):
            count += 1
        if(self.DPS1 is not None):
            count += 1
        if(self.DPS2 is not None):
            count += 1
        if(self.DPS3 is not None):
            count += 1

        return count

    def IsFilled(self):
        isFilled = True
        if(self.Tank is None):
            isFilled = False
        if(self.Healer is None):
            isFilled = False
        if(self.DPS1 is None):
            isFilled = False
        if(self.DPS2 is None):
            isFilled = False
        if(self.DPS3 is None):
            isFilled = False
            
        return isFilled

    def FindPlayerForRole(self, role, pureRole):
        if len(pureRole) > 0:
            random.shuffle(pureRole)
            return pureRole[0]
        elif len(role.Members) > 0:
            random.shuffle(role.Members)
            return role.Members[0]      
        else:
            return None

    def RemoveMemberFromSelection(self, member, Tanks, Healers, DPS, PureRole):
        if member in Tanks.Members: 
            Tanks.Members.remove(member)
        if member in PureRole: 
            PureRole.remove(member)
        if member in Healers.Members: 
            Healers.Members.remove(member)
        if member in DPS.Members: 
            DPS.Members.remove(member)

    def ToString(self, tEmoji: discord.Emoji, hEmoji: discord.Emoji, dEmoji: discord.Emoji, rEmoji):
        random.shuffle(rEmoji)

        if(len(rEmoji) > 0):
            output = f"G[{self.GroupNumber + 1} {rEmoji[0]}]"
            rEmoji.remove(rEmoji[0])
        else:
            output = f"G[{self.GroupNumber + 1} EMOJI!]"

        if(self.VoiceChannel is not None):
            output += f"[<#{self.VoiceChannel.id}>]: "
        else:
            output += f"[RAN OUT OF VOICE CHANNELS]: "

        if(self.Tank is not None):
            output += f"{tEmoji}{self.Tank.ToString()} "
        if(self.Healer is not None):
            output += f"{hEmoji}{self.Healer.ToString()} "
        if(self.DPS1 is not None):
            output += f"{dEmoji}{self.DPS1.ToString()} "
        if(self.DPS2 is not None):
            output += f"{dEmoji}{self.DPS2.ToString()} "
        if(self.DPS3 is not None):
            output += f"{dEmoji}{self.DPS3.ToString()} "



        return output




    
