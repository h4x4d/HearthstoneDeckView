from gevent.monkey import patch_all

patch_all(thread=False, select=False)