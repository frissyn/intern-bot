from .event import on_ready

def setup(bot):
    bot.add_listener(on_ready)