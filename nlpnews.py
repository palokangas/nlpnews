from flask import Flask
app = Flask(__name__)
application = app  # our hosting requires application in passenger_wsgi


@app.route("/")
def hello():
    return "This is Jello World!\n"

if __name__ == "__main__":
    app.run()
