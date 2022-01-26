from .event import on_connect

def setup(bot):
    bot.add_listener(on_connect)