import discord

class MadnessMember:
    MythicMember = discord.Member
    HasRole = False
    Roles = ""

    # Constractor of the class
    def __init__(self, member: discord.Member, HasRole: bool, Roles: str):
        self.MythicMember = member
        self.HasRole = HasRole
        self.Roles = Roles

    def ToString(self):
        return f"{self.MythicMember.mention}"

    
