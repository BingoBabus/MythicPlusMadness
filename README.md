# MythicPlusMadness
Randomize a voice channel members list by role into MMO groups

Made By: Bingo Babus

#
## Command
!rando <Channel you want to randomize>

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
  
 make list of all members with members with pure tank, healer, or DPS role
 make list of all members with tank, healer, or dps role
 
 start filling in the groups with pure role members first, after those lists are empty use the members with hybrid roles


#
## Installation Guide

- Have python 3 installed
