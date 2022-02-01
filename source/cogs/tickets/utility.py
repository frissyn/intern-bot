from os import path

from db import session
from db.models import Ticket
from db.models import Client
from db.models import Context
from db.utility import commit


TARGET = 938094149222158376
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
