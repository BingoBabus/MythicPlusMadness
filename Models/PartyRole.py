import discord
from Models.MadnessMember import MadnessMember
from typing import List

class PartyRole:
    Role = discord.Role
    Members = []

    def __init__(self, roles: List[discord.Role], RoleName: str):
        partyRole = discord.utils.get(roles, name=RoleName)
        self.Members = []

        if partyRole is not None:
            self.Role  = partyRole
        else:
            raise  ValueError("There is no {0} role on this server!".format(RoleName))

    def AddMember(self, member: discord.member):
        self.Members.append(member)

    
        
        
