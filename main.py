"""Anonimowe disco wyznania"""
import asyncio
from asyncio import get_event_loop

# Django
import django

# 3rd-party
import discord
from aiohttp import web
from aiohttp.web import Application
from discord import app_commands
from discord.ext.commands import DefaultHelpCommand
from django.apps import apps
from utils import read_json_file

django.setup()


class CustomHelpCommand(DefaultHelpCommand):

    def __init__(self, **options):
        super().__init__(**options)
        self.no_category = 'General'


config = read_json_file('config.json')
desc = 'AnonimoweDiscoWyznania.'
intents = discord.Intents.default()
intents.message_content = True
activity = discord.Game('Made by NosApki')
client = discord.Client(
    intents=intents,
    command_prefix=config.get('cmd_prefix', '/'),
    activity=activity,
    description=desc,
    help_command=CustomHelpCommand(),
)
tree = app_commands.CommandTree(client)
discord_py = None


@client.event
async def on_ready():
    """Print that bot logged in as."""
    print(f'Logged in as {client.user.name} | ID: {client.user.id}!')
    await tree.sync()


class AnonymousModal(discord.ui.Modal, title='AnonimoweDiscoWyznania'):
    designation = discord.ui.TextInput(
        label='Wyznanie',
    )

    async def on_submit(self, interaction):
        print('hey')
        designate = apps.get_model('storage', 'Designate')
        print('owo')
        print(self.designation)
        designate.objects.create(message=f'{self.designation}')
        print('beka z czuowieka')
        await getattr(
            interaction.response,
            'send_message',
        )(f'Thank you!', ephemeral=True)


@tree.command(description='Wyślij anonimową wiadomość')
async def anonim(interaction):
    await interaction.response.send_modal(AnonymousModal())


async def handle_msg(request):
    designation_id = config.get('designation_id')
    if designation_id:
        channel = client.get_channel(designation_id)
        msg_ids = request.data['msg_ids']
        designate = apps.get_model('main', 'Designate')
        queryset = designate.objects.filter(
            id__in=msg_ids,
        )
        for item in queryset:
            await channel.send(item.message)
        queryset.update(approved=True)
    return web.Response(status=200)


async def start_bot():
    await client.start(config.get('token'))


async def background_tasks(app):
    app[discord_py] = asyncio.create_task(start_bot())
    yield
    app[discord_py].cancel()
    await app[discord_py]


if __name__ == '__main__':
    app = Application()
    app.add_routes([web.post('/handle-msg/', handle_msg)])
    discord_py = web.AppKey('discord_py', asyncio.Task[None])
    app.cleanup_ctx.append(background_tasks)
    web.run_app(app, port=2137)
