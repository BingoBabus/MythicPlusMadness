# MythicPlusMadness
Randomize a voice channel members list by role into MMO groups

Made By: Bingo Babus

## Command
/madness [channel] 

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
 
  
make list of all members with members with pure tank, healer, or DPS role

make list of all members with tank, healer, or dps role
 
start filling in the groups with pure role members first, after those lists are empty use the members with hybrid roles

after all members have been assigned then check the balance of the groups. If any group has 2 or less players then even out the groups until all groups have at least 3 members

each group will be assigned a random channel to join while they run the dungeon

The bot isn't perfect and sometimes players are not assigned due to the ratio of member roles. Those players will be listed at the end with an Opps! message. Some manual assignment will be needed for them

If a member is in voice channel and missing a tank/healer/dps role then they will be listed out and directed to the roles channel

## Installation Guide

- Have python 3 installed
- get a discord token from your bot via https://discord.com/developers/applications
- get the guild id of your server. You can do this with developer mode enabled and right clicking on your server name then selecting copy id
- fill in the token and guild id value in the .env file

