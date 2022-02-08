import nextcord

from nextcord import ui

from ..utility import ROLES


class ConfirmView(ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Confirm', style=nextcord.ButtonStyle.green)
    async def confirm(self, btn, inter):
        self.value = True
        self.stop()

    @nextcord.ui.button(label='Cancel', style=nextcord.ButtonStyle.grey)
    async def cancel(self, btn, inter):
        self.value = False
        self.stop()


class CategoryDropdownView(ui.View):
    def __init__(self, check: callable):
        super().__init__(timeout=None)

        self.values = None
        # self.interaction_check = check
    
    @ui.select(
        min_values=1,
        max_values=3,
        placeholder="Select the languages that apply.",
        options=[nextcord.SelectOption(**r) for r in ROLES]
    )
    async def callback(self, sel, inter):
        self.values = sel.values

        self.stop()


class JoinThreadView(ui.View):
    def __init__(self, t, bot):
        super().__init__(timeout=None)

        btn = ui.Button(
            disabled=t.resolved,
            label="Join the Thread!",
            style=nextcord.ButtonStyle.success,
            custom_id=f"ps:thread-{t.thread_id}",
        ); btn.callback = self.callback

        self.bot = bot
        self.ticket = t
        self.add_item(btn)
    
    async def callback(self, inter):
        thread = self.bot.get_channel(self.ticket.thread_id)

        await thread.add_user(inter.user)


class ResolvedThreadView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Thread has been resolved", emoji=r"🔒", disabled=True)
    async def button(self, *args, **kwargs):
        pass


class HelpRoleSelectView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)

        self.bot = bot
        self.values = None
    
    @ui.select(
        min_values=0,
        max_values=len(ROLES),
        custom_id="ps:helproleselect",
        placeholder="Select all the help roles you'd like add or remove.",
        options=[nextcord.SelectOption(**r) for r in ROLES]
    )
    async def callback(self, sel, inter: nextcord.Interaction):
        diff = "```diff\n"
        user = inter.user

        for v in sel.values:
            role = nextcord.utils.get(inter.guild.roles, name=v)
            rnames = [r.name for r in inter.user.roles]

            if v in rnames:
                await user.remove_roles(role)
                diff += f"- {v}\n"
            else:
                await user.add_roles(role)
                diff += f"+ {v}\n"
        
        await inter.response.send_message(
            f"Updated your help roles!\n{diff}\n```", ephemeral=True
        )
