from source import TOKEN
from source import robot

from db.handle import BASE
from db.handle import engine
from db.handle import session

from source.server import thread

try:
    BASE.metadata.create_all(engine)
    thread.start(); robot.run(TOKEN)
except KeyboardInterrupt:
    session.close() and exit(0)
