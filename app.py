import flask
import flask_login
import sirope

from model.Product import Product
from model.User import User

from views.user import user_blpr
from views.product import product_blpr
from views.bid import bid_blpr
from views.comment import comment_blpr

from config import load_config


def create_app():
    flapp = flask.Flask(__name__)
    sirop = sirope.Sirope()
    login = flask_login.login_manager.LoginManager()

    flapp.config.update(load_config())
    login.init_app(flapp)

    flapp.register_blueprint(user_blpr)
    flapp.register_blueprint(product_blpr)
    flapp.register_blueprint(bid_blpr)
    flapp.register_blueprint(comment_blpr)

    return flapp, sirop, login


...

app, srp, lm = create_app()


@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash(
        "No puedes realizar la operación solicitada. Por favor, inicia sesión con una cuenta con los permisos apropiados.")
    return flask.redirect("/")


@lm.user_loader
def user_loader(email: str) -> User:
    return User.find(srp, email)


@app.route("/favicon.ico")
def get_fav_icon():
    return app.send_static_file("favicon.ico")


@app.route("/", methods=["GET"])
def main():
    usr = User.current()

    sust = {
        "title": "",
        # Lo convierto a lista para poder comparar con "== []" en la plantilla jinja
        "products": list(srp.load_last(Product, 100)),
        "usr": usr,
        "srp": srp,
        "multimedia_data_folder": load_config()['MULTIMEDIA_DATA_FOLDER'] + '/',
    }

    return flask.render_template("dashboard.jinja2", **sust)


@app.route("/about", methods=["GET"])
def about():
    usr = User.current()
    return flask.render_template("about.jinja2", usr=usr)


if __name__ == "__main__":
    app.run(debug=True)
...
