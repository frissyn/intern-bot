from .cog import Tickets
from .listen import TicketsEvents


def setup(bot):
    bot.add_cog(Tickets(bot))
    bot.add_cog(TicketsEvents(bot))