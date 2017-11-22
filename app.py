from flask import Flask, url_for, render_template


app = Flask("hooktest-validator", static_folder="assets", template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results")
def evaluation():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
