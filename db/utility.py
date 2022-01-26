import nextcord

from db import session


def commit(*objects):
    for o in objects:
        session.add(o)
    
    session.commit()

    return objects


def delete(*objects):
    for o in objects:
        session.delete(o)
    
    session.commit()

    return True


def embed_object(obj, **kw):
    em = nextcord.Embed(**kw)
    
    if em.title == nextcord.Embed.Empty:
        em.title = f"{obj.__tablename__.title()}: {obj.id}"
    
    for column, value in obj.__dict__.items():
        if not column.startswith("_"):
            em.add_field(name=column.upper(), value=str(value))

    return em