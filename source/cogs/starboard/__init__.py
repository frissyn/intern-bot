from .cog import Starboard

def setup(bot):
    bot.add_cog(Starboard(bot))