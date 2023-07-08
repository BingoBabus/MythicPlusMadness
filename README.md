# MythicPlusMadness
Randomize discord members in a voice channel into MMO Groups based on their role in discord

Made By: Bingo Babus

## Command
/madness [voice_channel] 

This is made for World of Warcraft Mythic Plus Groups. 

Discord Requirements:
roles
 - tank
 - healer
 - dps
 
emoji
 - Tank
 - Healer
 - DPS
 
 Channel
  - roles
 
the discord bot will look at all members and their roles in the voice channel

NumberGroupsNeeded = NumMembersInChannel mod 5 (wow party size) 
 - if the mod remainder is > 0 
   - then the numbers of groups needed is the quotient + 1
 - else
   - quotient


 (example: 38 mod 5 = Quotient: 7, remainder:3. So 8 groups will be needed )
 
start assigning Tanks, then healers, than DPS. Members with only one role will be prioritized first. Depending of the pools of roles available. Some players might not get assigned. So create new groups, filling in the roles needed until all players have a group.
 
after all members have been assigned then check the balance of the groups. 
If any group has 2 or less players then even out the groups until all groups have at least 3 members
If any group has a Tank + Healer and another group has neither then remove the tank and add it to that group

each group will be assigned a random channel to join while they run the dungeon

The bot isn't perfect let me know if you run into bugs!

If a member is in voice channel and missing a tank/healer/dps role then they will be listed out and directed to the roles channel

## Installation Guide

- Have python 3 and PyNaCl installed
- py -m pip install -U discord.py[voice]
- get a discord token from your bot via https://discord.com/developers/applications
- get the guild id of your server. You can do this with developer mode enabled and right clicking on your server name then selecting copy id
- fill in the token and guild id value in the .env file
- put the file path to the python script into the .bat file
- run bat and prepare for madness

