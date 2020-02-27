import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '<qh-\y}4QT5gb[\p6qy=' # This is a random string
