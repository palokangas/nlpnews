import sys
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# flash, g, redirect, request, url_for
from nlpnews import analysis

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

    from . import newsloader
    app.cli.add_command(newsloader.refresh_news_command)
    app.cli.add_command(newsloader.get_totals_command)
    app.cli.add_command(newsloader.get_content_command)

    @app.route("/")
    def hello():
        bar = analysis.plot_freqs()
        data = analysis.get_most_common_terms()        
        return render_template('index.html', plot=bar, tabledata=data)

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
