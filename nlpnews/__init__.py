import sys
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# flash, g, redirect, request, url_for



db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__,
                instance_relative_config=True,
                static_folder="static")
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" +
            os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    migrate = Migrate(app, db)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    print(f"Flask app instance path set to {app.instance_path}")

    db.init_app(app)
#    from . import models
#    app.cli.add_command(models.init_db_command)

#    from . import feedparser
#    app.cli.add_command(feedparser.refresh_feeds_command)
#    app.cli.add_command(feedparser.populate_from_files_command)

    @app.route("/")
    def hello():
        helloversion = "Hello, I am still running: " + sys.version
        return render_template('index.html')

    return app



app = create_app()

if __name__ == "__main__":
    app.run()
