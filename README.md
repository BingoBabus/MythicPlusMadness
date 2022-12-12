# MythicPlusMadness
Randomize a voice channel members list by role into MMO groups

Made By: Bingo Babus

#
## Command
!rando [channel-name] 

default channel name is currently "cream of the crop"

This is made for World of Warcraft Mythic Plus Groups. 

Requirement 
discord roles of 
 - tank
 - healer
 - dps
 
the discord bot will look at all members and their roles in the channel parameter

NumberGroupsNeeded = NumMembersInChannel mod 5 (wow party size) 
if the mod remainder is > 0 
  then the numbers of groups needed is the quotient + 1
else
  quotient
 (example: 38 mod 5 = Quotient: 7, remainder:3. So 8 groups will be needed )
 
  
make list of all members with members with pure tank, healer, or DPS role
make list of all members with tank, healer, or dps role
 
start filling in the groups with pure role members first, after those lists are empty use the members with hybrid roles

after all members have been assigned then check the balance of the groups. If any group has 2 or less players then even out the groups until all groups have at least 3 members

each group will be assigned a random channel to join while they run the dungeon

#
## Installation Guide

- uhh, I kind of forget :P 
- Have python 3 installed
- get a discord token from your bot via https://discord.com/developers/applications
- fill in the token value in the .env file

