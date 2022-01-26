import nextcord

from db import session

from db.models import Vote
from db.models import StaleView

from db.utility import commit
from db.utility import delete


def vote(uid, rn, cast):
    player = rn.players[cast]
    other = rn.players[int(not cast)]

    p_votes = [v.user_id for v in player.votes]
    o_votes = [v.user_id for v in other.votes]

    if uid in p_votes:
        return f"You've already voted for **{player.name}**!"
    elif uid not in p_votes and uid in o_votes:
        delete(
            session.query(Vote)
            .filter_by(user_id=uid, player_id=other.id)
            .first()
        )

        commit(Vote(user_id=uid, player_id=player.id))

        return f"Your vote has been changed to **{player.name}**!"
    elif uid not in p_votes and uid not in o_votes:
        commit(Vote(user_id=uid, player_id=player.id))

        return f"Your vote has been cast for **{player.name}**"
    
    return "Nothing happened?"


class ClashView(nextcord.ui.View):
    def __init__(self, tourn, rn):
        super().__init__(timeout=None)
        self.rn = rn
        self.tourn = tourn
        self.emotes = [r"☄️", r"💥"]

        for i, player in enumerate(rn.players):
            btn = nextcord.ui.Button(
                label=player.name,
                emoji=self.emotes[i],
                style=nextcord.ButtonStyle.primary
            )

            btn.callback = getattr(self, f"_{i}")

            self.add_item(btn)

    async def _0(self, interaction):
        res = await self.handler(interaction, 0)
        await interaction.response.send_message(res, ephemeral=True)

    async def _1(self, interaction):
        res = await self.handler(interaction, 1)
        await interaction.response.send_message(res, ephemeral=True)

    async def handler(self, itr, cast):
        s = (
            session.query(StaleView)
            .filter_by(msg_id=itr.message.id)
            .first()
        )
        
        if s: return "This vote has expired!"

        return vote(itr.user.id, self.rn, cast)


class ArchivedClashView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Expired", emoji=r"🔒", disabled=True)
    async def button(self, *args):
        pass