import os
import sys
import inspect
import nextcord

from db import sandbox

from ..cog import Base

from nextcord.ext import commands


class Sandbox(Base):
    def _prep(self, code: str):
        code = code.replace("-s\n", "", 1)

        arr = code.strip("```").replace("py\n", "").split("\n")

        if not arr[::-1][0].replace(" ", "").startswith("return"):
            arr[len(arr) - 1] = "return " + arr[::-1][0]

        return "".join(f"\n\t{i}" for i in arr)

    def _resolve(self, var):
        if hasattr(var, "__iter__"):
            vlen = len(list(var))

            if vlen > 100 and not isinstance(var, str):
                return f"<{type(var).__name__} iterable with >= 100 values ({vlen})>"
            elif not vlen:
                return f"<empty {type(var).__name__} iterable>"

        if not var and not isinstance(var, bool):
            return f"<empty {type(var).__name__} object>"

        return var

    async def _play(self, ctx, code: str):
        args = {
            "os": os,
            "ctx": ctx,
            "sys": sys,
            "this": self,
            "imp": __import__,
            "nextcord": nextcord,
            "commands": commands,
            "sauce": inspect.getsource,
            **dict([(n, getattr(sandbox, n)) for n in sandbox.names]),
        }

        exec(f"async def task(): {code}", args)
        response = await eval("task()", args)

        return response

    @commands.command("sandbox.play")
    async def sandbox_play(self, ctx, *, code: str):
        silent = "-s" in code

        code = self._prep(code)

        try:
            result = await self._play(ctx, code)

            if isinstance(result, nextcord.Message):
                return
            else:
                final = self._resolve(result)

            if not silent:
                await ctx.send(f"```py\n{final}\n```")
        except Exception as e:
            await ctx.send(f"```\n{type(e).__name__}: {str(e)}```")

    @commands.command("sandbox.spec")
    async def sandbox_spec(self, ctx, path, name="None", lines=None):
        space = __import__(path, fromlist=[""])

        if name == "None":
            spec = inspect.getsource(space)
        else:
            spec = inspect.getsource(getattr(space, name, 404))
                
        if lines:
            start, end = [int(n) for n in lines.split("-")[:2]]
            spec = "\n".join(spec.split("\n")[start:end])

        if len(spec) <= 3985:
            await ctx.send(f"```py\n{spec}\n```")
        else:
            await ctx.send(f"```txt\nResult is >= 4000 characters.\n```")
