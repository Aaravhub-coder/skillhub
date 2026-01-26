from flask import Flask,render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/about/<username>")
def team(username):
    return render_template("about.html",username=username)

if __name__ == "__main__":
    app.run(debug=True,port=8000)