from db import Model
from db import engine
from db import session

from source import TOKEN
from source import robot

from source.server import thread

try:
    Model.metadata.create_all(engine)
    thread.start()
    robot.run(TOKEN)
except KeyboardInterrupt:
    session.close() and exit(0)
