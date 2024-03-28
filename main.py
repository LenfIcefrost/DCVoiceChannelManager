import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from discord.interactions import Interaction
import setting

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)


@tasks.loop(minutes=3.0, count=2)
async def text_auto_delete(msg: discord.Message):
    await msg.delete()


@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command (s) ")
        await setting.setting_ins.load_data(cli=client)
    except Exception as e:
        print(e)


@bot.event
async def on_connect():
    print("on connect")
    pass


@bot.event
async def on_disconnect():
    print("on disconnect")
    pass


@bot.event
async def on_message(message: discord.Message):
    if message.author.id not in setting.setting_ins.administrator.users_id:
        return

@bot.tree.command(name="help", description="help you to know librarian better")
async def help(interaction: discord.Interaction):
    interaction.response.send_message("wait lazy programmer to update.")

@bot.tree.command(name="get_off", description="librarian get tired.")
async def get_off(interaction: discord.Interaction):
    if interaction.user.id not in setting.setting.administrator.users_id:
        await interaction.response.send_message("it is a administrator's command.")
        return
    await interaction.response.send_message("server close.")
    await setting.setting_ins.release_channels()
    setting.setting_ins.save_data()
    print("cmd: server close.")
    await bot.close()


@bot.tree.command(name="rooms_info", description="check all the rooms info.")
async def rooms_info(interaction: discord.Interaction):
    await interaction.response.send_message(f"Info:\n{'============'.join([rom.info() for rom in setting.setting_ins.get_channel_data(interaction.guild.id)])}")


@bot.tree.command(name="set_default_name", description="set default discussion name per user")
async def set_default_name(interaction: discord.Interaction, name: str):
    setting.setting_ins.add_user_default_channel_name(interaction.guild.id, interaction.user.id, name)
    await interaction.response.send_message(f"{interaction.user.mention} 好窩 以後您在此伺服器中的預設房間名字就是 : {name}")


async def reserve_room_func(interaction: discord.Interaction, name: str):
    has_role = setting.setting_ins.user_has_role(interaction.guild.id, interaction.user)

    if has_role:
        await interaction.response.send_message(f"{interaction.user.mention} 是要多少間==")
        return

    gu = interaction.guild

    index = -1

    while f"{name}{'' if index == -1 else str(index)}" in [c.name for c in interaction.channel.category.channels]:
        index += 1

    index_str = '' if index == -1 else str(index)

    ro = await gu.create_role(name=f"{name}{index_str}-manager")
    mem_ro = await gu.create_role(name=f"{name}{index_str}-member")

    roma = discord.utils.get(gu.roles, name=setting.setting_ins.bot_setting.bot_role_name)

    overwrites = {
        gu.default_role: discord.PermissionOverwrite(connect=False),
        ro: discord.PermissionOverwrite(connect=True, read_messages=True, manage_channels=True, manage_permissions=True),
        mem_ro: discord.PermissionOverwrite(connect=True, read_messages=True),
        roma: discord.PermissionOverwrite(connect=True, read_messages=True, manage_channels=True, manage_permissions=True)
    }

    await interaction.user.add_roles(ro)

    ch = await gu.create_voice_channel(f"{name}{index_str}", category=interaction.channel.category, overwrites=overwrites)

    setting.setting_ins.add_channel_data(interaction.guild.id, setting.ChannelData(
        guild=gu,
        owner=interaction.user,
        role_manager=ro,
        role_member=mem_ro,
        text_channel=interaction.channel,
        voice_channel=ch
    ))

    await interaction.response.send_message(f"{interaction.user.mention} 這邊是設備包，拿好")


@bot.tree.command(name="reserve_name_room", description="reserve a room with name for 2hr, for u to study hard! gogo!")
async def reserve_name_room(interaction: discord.Interaction, name: str):
    await reserve_room_func(interaction, name)
    return


@bot.tree.command(name="reserve_room", description="reserve a room for 2hr, for u to study hard! gogo!")
async def reserve_room(interaction: discord.Interaction):
    name = setting.setting_ins.user_setting[interaction.guild.id][interaction.user.id] if interaction.guild.id in setting.setting_ins.user_setting and interaction.user.id in setting.setting_ins.user_setting[interaction.guild.id] else "discussion-room"
    await reserve_room_func(interaction, name)


@bot.tree.command(name="open_door", description="let other person can go in your room.")
async def opendoor(interaction: discord.Interaction, member: discord.Member):
    room = setting.setting_ins.get_user_manager_room(interaction.guild.id, interaction.user)

    if room is None:
        await interaction.response.send_message(f"{interaction.user.mention} 你不能開門。")
        return

    if interaction.user == member:
        await interaction.response.send_message(f"{interaction.user.mention} 三小? 請進")
        return

    await member.add_roles(room.role_member)

    await interaction.response.send_message(f"{member.mention} {interaction.user.mention} 大發慈悲幫你開門了")


@bot.tree.command(name="knock_knock", description="tag people in room to make you go in.")
async def knock(interaction: discord.Interaction, role: discord.Role):
    if not setting.setting_ins.has_role(interaction.guild.id, role):
        await interaction.response.send_message(f"{interaction.user.mention} 敲三小?")
        return

    if role in interaction.user.roles:
        await interaction.response.send_message(f"{interaction.user.mention} ? 進不去喔 我幫你開門阿")
        return

    room = setting.setting_ins.get_manager_member_room(interaction.guild.id, role)

    await room.voice_channel.send(f"{role.mention} {interaction.user.mention} 在敲敲門")
    await interaction.response.send_message(f"{interaction.user.mention} 好的 幫你敲敲")


@bot.tree.command(name="return_key", description="if you have good habit, you can return your key.")
async def return_key(interaction: discord.Interaction):
    room = setting.setting_ins.get_user_manager_room(interaction.guild.id, interaction.user)

    if room is None:
        msg = await interaction.response.send_message(f"{interaction.user.mention} 你關啥玩意兒?")
        return

    await interaction.response.send_message(f"咚{interaction.user.mention} 把 {room.voice_channel.name} 門關起來了")
    await room.release()


@bot.tree.command(name="extend_reserve_time_to2hr", description="if you want to fight more, then just do it.")
async def extend_reserve_time(interaction: discord.Interaction):
    room = setting.setting_ins.get_user_manager_room(interaction.guild.id, interaction.user)
    if room is None:
        await interaction.response.send_message(f"{interaction.user.mention} 啥?")
        return

    room.re_reserve()
    await interaction.response.send_message(f"{interaction.user.mention} {room.voice_channel.name} 續借成功囉 繼續加油加油!")

if __name__ == '__main__':
    bot.run(setting.setting_ins.bot_setting.bot_token)
