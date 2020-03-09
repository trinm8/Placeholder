import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '<qh-\y}4QT5gb[\p6qy=' # This is a random string
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #                           'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTGRES_URL = "127.0.0.1:5432"
    POSTGRES_USER = "postgres"
    POSTGRES_PW = "postgres"  # TODO: Make more secure for server
    POSTGRES_DB = "dbtutor"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                               'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL,
                                                          db=POSTGRES_DB)
