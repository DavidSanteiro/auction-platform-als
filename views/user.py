import os

import flask
import sirope
import flask_login
import bleach

from redis import Redis
from config import load_config

from model.Bid import Bid
from model.Comment import Comment
from model.Product import Product
from model.User import User


def get_blprint():
    usr_module = flask.blueprints.Blueprint("user_blpr", __name__,
                                            url_prefix="/user",
                                            template_folder="templates/user",
                                            static_folder="static")
    syrp = sirope.Sirope(Redis.from_url(load_config()['REDISCLOUD_URL']))
    return usr_module, syrp


...

user_blpr, srp = get_blprint()

"""
====================================
Métodos relacionados con el Registro
====================================

Aquí se encuentran todos los métodos que están relacionados con el registro de usuarios. 
Estos incluyen la visualización del formulario de registro, la validación de los datos 
del formulario y la creación de un nuevo usuario en la base de datos.
"""


@user_blpr.route("register", methods=["GET"])
def register_form():
    if User.current() is not None:
        flask_login.logout_user()
        flask.flash("Ha pasado algo extraño. Por favor, entra de nuevo.")
        return flask.redirect("/user/login")
    ...
    return flask.render_template("register.jinja2")


@user_blpr.route("register", methods=["POST"])
def register():
    if User.current() is not None:
        flask_login.logout_user()
        flask.flash("No puedes registrarte mientras tienes una sesión iniciada.")
        return flask.redirect("/")
    ...

    usr_name = flask.request.form.get("edName").strip()
    usr_email = flask.request.form.get("edEmail", "").strip()
    usr_pswd = flask.request.form.get("edPswd", "").strip()

    if (not usr_name
            or not usr_email
            or not usr_pswd):
        flask.flash("Credenciales incompletas")
        return flask.redirect("/user/register")
    ...

    if User.find(srp, usr_email):
        flask.flash("Ya estás registrado")
        return flask.redirect("/user/login")
    ...

    # Limpia posible XSS de los campos de texto (la contraseña no se limpia porque se cifra y no sale de backend)
    clean_name = bleach.clean(usr_name)
    clean_email = bleach.clean(usr_email)


    usr = User(clean_name, clean_email, usr_pswd)
    srp.save(usr)
    flask.flash("Registrado correctamente")
    return flask.redirect("/user/login")


...

"""
==============================
Métodos relacionados con Login
==============================

Aquí se encuentran todos los métodos que están relacionados con el inicio de sesión de los usuarios. 
Estos incluyen la visualización del formulario de inicio de sesión, la validación de las credenciales 
del usuario y la creación de una nueva sesión para el usuario.
"""


@user_blpr.route("login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        if User.current() is not None:
            flask.flash("Ya has iniciado sesión.")
            return flask.redirect("/")
        ...
        return flask.render_template("login.jinja2")
    else:
        if User.current() is not None:
            flask_login.logout_user()
            flask.flash("No puedes iniciar sesión porque ya tienes una sesión iniciada.")
            return flask.redirect("/user/login")
        ...

        usr_email = flask.request.form.get("edEmail", "").strip()
        usr_pswd = flask.request.form.get("edPswd", "").strip()

        if (not usr_email
                or not usr_pswd):
            flask.flash("Credenciales incompletas")
            return flask.redirect("/user/login")
        ...

        usr = User.find(srp, usr_email)

        if (not usr
                or not usr.chk_pswd(usr_pswd)):
            flask.flash("Credenciales incorrectas: ¿has hecho el registro?")
            return flask.redirect("/user/login")
        ...

        flask_login.login_user(usr)
        return flask.redirect("/")


"""
==========================================
Métodos relacionados con edición de perfil
==========================================

Aquí se encuentran todos los métodos que están relacionados con la edición de perfil de los usuarios.
Estos son la edición de los datos del usuario (salvo la contraseña), la contraseña y la eliminación 
de la cuenta del usuario.
"""

@user_blpr.route("edit", methods=["GET", "POST"])
@flask_login.login_required
def edit():
    usr = User.current()
    if flask.request.method == "GET":
        ...
        return flask.render_template("edit.jinja2", usr=usr)
    else:
        ...
        usr_name = flask.request.form.get("edName").strip()
        usr_email = flask.request.form.get("edEmail", "").strip()

        if (not usr_name
                or not usr_email):
            flask.flash("Credenciales incompletas")
            return flask.redirect(flask.url_for("user_blpr.edit"))
        ...

        usr.name = bleach.clean(usr_name)
        usr.email = bleach.clean(usr_email)
        srp.save(usr)
        flask.flash("Perfil actualizado correctamente")
        return flask.redirect("/")


@user_blpr.route("edit/password", methods=["GET", "POST"])
@flask_login.login_required
def change_password():
    usr = User.current()

    if flask.request.method == "GET":
        return flask.render_template("change_password.jinja2", usr=usr)
    else:
        usr_pswd = flask.request.form.get("edPswd", "").strip()
        usr_new_pswd = flask.request.form.get("edNewPswd", "").strip()

        if (not usr_pswd
                or not usr_new_pswd):
            flask.flash("Credenciales incompletas")
            return flask.redirect(flask.url_for("user_blpr.change_password"))
        ...

        if not usr.chk_pswd(usr_pswd):
            flask.flash("Contraseña incorrecta")
            return flask.redirect(flask.url_for("user_blpr.change_password"))
        ...

        usr.change_pswd(usr_new_pswd)

        srp.save(usr)
        flask.flash("Contraseña actualizada correctamente")

        return flask.redirect("/")


@flask_login.login_required
@user_blpr.route("delete", methods=["GET", "POST"])
def delete():
    usr = User.current()
    if flask.request.method == "GET":
        return flask.render_template("delete.jinja2", usr=usr)
    else:

        # Elimina los comentarios del usuario
        comments = srp.filter(Comment, lambda c: c.email_author == usr.email)
        for cmt in comments:
            cmt_oid = cmt.get_safe_id(srp)
            if srp.exists(cmt_oid):
                srp.delete(cmt_oid)

        # Elimina las pujas del usuario
        bids = srp.filter(Bid, lambda b: b.email_owner == usr.email)
        for bid in bids:
            bid_oid = bid.get_safe_id(srp)
            if srp.exists(bid_oid):
                srp.delete(bid_oid)

        # Elimina los productos del usuario
        products = srp.filter(Product, lambda p: p.email_owner == usr.email)
        for prd in products:
            prd_oid = prd.get_safe_id(srp)
            if srp.exists(prd_oid):
                product = srp.load(prd_oid)
                delete_files = product.media_file_names.copy()
                for file_name_delete in delete_files:
                    if file_name_delete not in product.media_file_names:
                        flask.flash(f"Archivo {file_name_delete} no encontrado.")
                    else:
                        file_path = os.path.join('.' + load_config()['MULTIMEDIA_DATA_FOLDER'], file_name_delete)
                        try:
                            os.remove(file_path)
                            product.remove_media_file_name(file_name_delete)
                            flask.flash(f"Archivo {file_name_delete} eliminado.")
                        except OSError as error:
                            print(error)
                            flask.flash(f"Error al eliminar el archivo {file_name_delete}")
                ...
                srp.delete(prd_oid)

        # Elimina el usuario de la base de datos
        if srp.exists(usr.__oid__):
            srp.delete(usr.__oid__)
            flask_login.logout_user()
            flask.flash("Cuenta eliminada correctamente")
        else:
            flask.flash("No se ha podido eliminar la cuenta. No se ha encontrado el usuario en la base de datos")
        ...
        return flask.redirect("/")


@flask_login.login_required
@user_blpr.route("logout", methods=["GET"])
def logout():
    flask_login.logout_user()
    return flask.redirect("/")