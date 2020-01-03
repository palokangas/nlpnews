### Ipython

To work with ipython, need to push an application context. See https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/:

from nlpnews import create_app; app = create_app(); app.app_context().push()

