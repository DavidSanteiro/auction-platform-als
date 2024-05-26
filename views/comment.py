

import flask
import sirope
import flask_login
import bleach

from model.Comment import Comment
from model.User import User
from views.product import get_product


def get_blprint():
    cooment_module = flask.blueprints.Blueprint("comment_blpr", __name__,
                                        url_prefix="/comment",
                                        template_folder="templates/comment",
                                        static_folder="static/comment")
    syrp = sirope.Sirope()
    return cooment_module, syrp


...


comment_blpr, srp = get_blprint()


@comment_blpr.route("<product_id>/add", methods=["POST"])
@flask_login.login_required
def add(product_id):
    # Recoge los datos del formulario
    usr = User.current()
    product = get_product(product_id)

    if product is None:
        flask.abort(404)
    ...

    comment_text = flask.request.form.get("edNewComment", "").strip()

    # Comprueba si se han rellenado todos los campos obligatorios
    if not comment_text:
        flask.flash("No se puede publicar un comentario vacío.")
        return flask.redirect(flask.url_for("product_blpr.detail", product_id=product_id))
    ...

    # Limpia posible XSS de los campos de texto
    clean_comment = bleach.clean(comment_text)

    product.add_comment_oid(srp.save(Comment(usr.email, usr.name, clean_comment, srp.oid_from_safe(product_id))))
    flask.flash("Comentario publicado.")
    return flask.redirect(flask.url_for("product_blpr.detail", product_id=product.get_safe_id(srp)))


@comment_blpr.route("<product_id>/<comment_id>/delete", methods=["POST"])
@flask_login.login_required
def delete(comment_id, product_id):

    usr = User.current()
    product = get_product(product_id)

    comment_oid = srp.oid_from_safe(comment_id)

    if srp.exists(comment_oid):
        if srp.load(comment_oid).email_author != usr.email:
            flask.flash("No puedes eliminar un comentario de otro usuario.")
            return flask.redirect(flask.url_for("product_blpr.detail", product_id=product_id))
        ...
        product.remove_comment_oid(comment_oid)
        srp.delete(comment_oid)
        flask.flash("Comentario eliminado.")
    else:
        flask.flash("Comentario no encontrado.")
    ...

    return flask.redirect(flask.url_for("product_blpr.detail", product_id=product_id))
