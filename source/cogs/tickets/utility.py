import re
import nextcord

from os import path

from db import session
from db.models import Client
from db.utility import commit


TARGET = 938840762878152725
HELPER = 938616795223429130
LOYAL = 481953084726312977
LOGGER = [938545742295998514]
TEST = "xxx users are currently in this help thread."
ROLES = [
    {"value": "help-bash", "default": False, "label": "Bash"},
    {"value": "help-basic-lang", "default": False, "label": "Basic (Lang)"},
    {"value": "help-cpp", "default": False, "label": "C++"},
    {"value": "help-csharp", "default": False, "label": "C#"},
    {"value": "help-css", "default": False, "label": "CSS"},
    {"value": "help-github", "default": False, "label": "Github"},
    {"value": "help-go", "default": False, "label": "Go"},
    {"value": "help-html", "default": False, "label": "HTML"},
    {"value": "help-java", "default": False, "label": "Java"},
    {"value": "help-js", "default": False, "label": "JavaScript"},
    {"value": "help-misc", "default": False, "label": "Miscellaneous"},
    {"value": "help-mongo", "default": False, "label": "Mongo"},
    {"value": "help-nix", "default": False, "label": "Nix"},
    {"value": "help-php", "default": False, "label": "PHP"},
    {"value": "help-python", "default": False, "label": "Python"},
    {"value": "help-ruby", "default": False, "label": "Ruby"},
    {"value": "help-rust", "default": False, "label": "Rust"},
    {"value": "help-swift", "default": False, "label": "Swift"}
]


def make_client(i: int):
    c = session.query(Client).filter_by(user_id=i).first()

    if not c:
        c = commit(Client(user_id=i))[0]

    return c


def file_content(name: str):
    d = path.dirname(path.abspath(__file__))

    with open(f"{d}/data/{name}.txt", "r+") as fh:
        content = fh.read()

    return content


async def increment_notice(msg: nextcord.Message, count):
    em = msg.embeds[0]
    limit = len(em.description) - len(TEST)
    num = re.findall(r"\d+", em.description[limit:])[0]

    em.description = (
        em.description[:limit] +
        em.description[limit:].replace(num, str(int(num) + count))
    )

    await msg.edit(embed=em)
