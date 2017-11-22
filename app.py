from flask import Flask, url_for, render_template, redirect, request
from controller import router, AppError
from flask_babel import Babel
from config import LANGUAGES

app = Flask("hooktest-validator", static_folder="assets", template_folder="templates")
babel = Babel(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["POST", "GET"])
def evaluation():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        try:
            return render_template("results.html", **router(request.form))
        except AppError as error:
            return render_template("index.html", error=error.message)


if __name__ == "__main__":
    app.run(debug=True)
