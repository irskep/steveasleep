import logging
from google.appengine.api import memcache

def memcache_or_db_or_web(memcache_name, db_func, web_func):
    def get():
        thingy = memcache.get(memcache_name)
        if thingy is not None:
            return thingy
        else:
            try:
                thingy = db_func()
                memcache.set(memcache_name, thingy)
            except IndexError:
                thingy = web_func()
        return thingy
    return get

def delete_all(ModelClass):
    objs = ModelClass.all()
    for obj in objs:
        obj.delete()
