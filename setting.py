from dataclasses import dataclass, field
from types import SimpleNamespace

import discord
from discord import Client, Forbidden
from discord.ext import tasks
import json
import static_data


@dataclass()
class ChannelData:
    guild: discord.Guild
    owner: discord.Member
    role_manager: discord.Role
    role_member: discord.Role
    text_channel: discord.TextChannel
    voice_channel: discord.VoiceChannel

    def cog_unload(self):
        self.delete_channel_alert.cancel()
        self.delete_channel.cancel()

    async def release(self):
        await self.role_manager.delete()
        await self.role_member.delete()
        await self.voice_channel.delete()
        self.delete_channel_alert.cancel()
        self.delete_channel.cancel()
        setting_ins.remove_channel_data(self.guild.id, self)

    @tasks.loop(hours=1.0, minutes=50.0, count=2)
    async def delete_channel_alert(self):
        if self.delete_channel_alert.current_loop == 1:
            await self.voice_channel.send(f"{self.role_manager.mention} 時間剩10分鐘囉")

    @tasks.loop(hours=20.0, count=2)
    async def delete_channel(self):
        if self.delete_channel.current_loop == 1:
            if len(self.voice_channel.members) != 0:
                await self.text_channel.send(f"{', '.join([str(m.mention) for m in self.voice_channel.members])} 時間到了 滾滾滾")
            await self.role_manager.delete()
            await self.role_member.delete()
            await self.voice_channel.delete()
            setting_ins.remove_channel_data(self.guild.id, self)

    def re_reserve(self):
        self.delete_channel.restart()
        self.delete_channel_alert.restart()

    def contain_id(self, _id: int):
        if _id == self.role_manager.id:
            return True
        if _id == self.role_member.id:
            return True
        if _id == self.text_channel.id:
            return True
        if _id == self.voice_channel.id:
            return True
        return False

    def info(self):
        return f"\n{self.voice_channel.name} : owner {self.owner.name}\nmanager_role : {self.role_manager.name}\nmember-using : {', '.join([mem.name for mem in self.voice_channel.members])}\n\n"

    def to_save_data(self) -> str:
        return f"{self.guild.id} {self.owner.id} {self.role_manager.id} {self.role_member.id} {self.text_channel.id} {self.voice_channel.id}"

    def __str__(self) -> str:
        return f"{self.guild.id} {self.role_manager.id} {self.role_member.id} {self.text_channel.id} {self.voice_channel.id}"


@dataclass()
class user_setting:
    default_channel_name: str


@dataclass()
class setting:
    __server_data: dict[discord.Guild.id, list[ChannelData]] = field(default_factory=lambda: {})
    user_setting: dict[discord.Guild.id, dict[discord.User.id, str]] = field(default_factory=lambda: {})
    bot_setting: static_data.bot_setting = static_data.bot_setting()
    administrator: static_data.administrator = static_data.administrator()

    # def __init__(self):
    #     self.administrator = administrator()

    def get_channel_data(self, guild: discord.Guild.id):
        return self.__server_data.get(guild, [])

    def add_channel_data(self, guild: discord.Guild.id, channel: ChannelData):
        if guild not in self.__server_data:
            self.__server_data[guild] = []
        self.__server_data[guild].append(channel)

    def remove_channel_data(self, guild: discord.Guild.id, channel: ChannelData):
        self.__server_data[guild].remove(channel)

    def user_has_role(self, guild: discord.Guild.id, user: discord.Member) -> bool:
        return any(check in [role.id for role in user.roles] for check in [channel.role_manager.id for channel in self.get_channel_data(guild)])

    def has_role(self, guild: discord.Guild.id, role: discord.Role) -> bool:
        return role.id in [ro.role_manager.id for ro in self.get_channel_data(guild)] or role.id in [ro.role_member.id for ro in self.get_channel_data(guild)]

    def get_owner_room(self, guild: discord.Guild.id, user: discord.Member) -> ChannelData:
        return next(iter([rom for rom in self.get_channel_data(guild) if rom.owner.id == user.id]), None)

    def get_user_manager_room(self, guild: discord.Guild.id, user: discord.Member) -> ChannelData:
        return next(iter([rom for rom in self.get_channel_data(guild) if rom.role_manager.id in [ro.id for ro in user.roles]]), None)

    def get_manager_member_room(self, guild: discord.Guild.id, role: discord.Role) -> ChannelData:
        return next(iter([rom for rom in self.get_channel_data(guild) if rom.role_manager.id == role.id or rom.role_member.id == role.id]), None)

    def add_user_default_channel_name(self, guild: discord.Guild.id, user: discord.User.id, name: str):
        if guild not in self.user_setting:
            self.user_setting[guild] = {}
        if user not in self.user_setting[guild]:
            self.user_setting[guild][user] = name

    def delete_user_default_channel_name(self, guild: discord.Guild.id, user: discord.User.id):
        if guild not in self.user_setting:
            return
        if user not in self.user_setting[guild]:
            return
        del self.user_setting[guild][user]
        if len(self.user_setting[guild]) == 0:
            del self.user_setting[guild]

    async def release_channels(self):
        for server, channels in self.__server_data.items():
            for channel in channels:
                await channel.release()
        self.__server_data.clear()

    def save_data(self):
        print(self)
        with open('server_data.txt', 'w') as file:
            # print(self.__dict__)
            # print(self.__server_data.__dict__)
            file.write(json.dumps(self.__dict__, default=lambda attr: attr.to_save_data()))
            # file.write("=====\n")
            # file.write(json.dumps(self.administrator.__dict__))
            # file.write("=====\n")
            # file.write(self.administrator.users_id.__repr__())
            # file.write("=====\n")
            # file.write(self.administrator.users_id.__str__())
        pass

    async def load_data(self, cli: discord.Client):
        # print(cli.)
        with open('server_data.txt', 'r') as f:
            result = json.loads("".join(f.readlines()))
            # region user-setting
            u_s: dict[str, dict[str, str]] = result["user_setting"]
            for guild_id, user_list in u_s.items():
                for user_id, name in user_list.items():
                    self.user_setting[int(guild_id)] = {}
                    self.user_setting[int(guild_id)][int(user_id)] = name

            # endregion

            # server_data: dict[str, list[str]] = result['_setting__server_data']
            # for key, channel_list in server_data.items():
            #     for channel in channel_list:
            #         val = [int(va) for va in channel.split(" ")]
            #         guild: discord.Guild = await cli.fetch_guild(val[0])
            #         owner: discord.Member = guild.get_member(val[1])
            #         role_manager: discord.Role = guild.get_role(val[2])
            #         role_member: discord.Role = guild.get_role(val[3])
            #         text_channel: discord.TextChannel = guild.get_channel(val[4])
            #         voice_channel: discord.VoiceChannel = guild.get_channel(val[5])
            #         self.__server_data[key] = []
            #         self.__server_data[key].append(ChannelData(
            #             guild=guild,
            #             owner=owner,
            #             role_manager=role_manager,
            #             role_member=role_member,
            #             text_channel=text_channel,
            #             voice_channel=voice_channel
            #         ))
            #
            # print("load success..")
            # print(self)
            # self.server_data =
            # print(result)
            # return
            # print(s)
            # print(type(s))

        # try:
        #     guild = await cli.get_guild(id)
        # except Forbidden:
        #     pass
        # else:
        #     for channel in guild.channels:
        #         print(channel.id)
        # guild: discord.Guild = cli.get
        # self.server_data[guild] += ChannelData()
        pass


setting_ins = setting()
