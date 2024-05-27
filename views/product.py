
import flask
import sirope
import flask_login
import os
import uuid
import bleach

from redis import Redis
from config import load_config

from datetime import datetime
from werkzeug.utils import secure_filename

from config import load_config
from model.Bid import Bid
from model.Comment import Comment
from model.User import User
from model.Product import Product


def get_blprint():
    product_module = flask.blueprints.Blueprint("product_blpr", __name__,
                                        url_prefix="/product",
                                        template_folder="templates/product",
                                        static_folder="static/product")
    syrp = sirope.Sirope(Redis.from_url(load_config()['REDISCLOUD_URL']))
    return product_module, syrp


...


product_blpr, srp = get_blprint()


@product_blpr.route("/", methods=["GET"])
@flask_login.login_required
def list_products():
    usr = User.current()
    products = srp.filter(Product, lambda p: p.email_owner == usr.email)
    sust = {
        "title": "Mis subastas",
        "usr": usr,
        "products": list(products),
        "srp": srp,
    }

    return flask.render_template("product_dashboard.jinja2", **sust)


@product_blpr.route("add", methods=["GET", "POST"])
@flask_login.login_required
def add():
    if flask.request.method == "GET":
        sust = {
            "title": "Añadir subasta",
            "usr": User.current()
        }

        return flask.render_template("product_add_form.jinja2", **sust)
    else:
        # Recoge los datos del formulario
        usr = User.current()
        product_title = flask.request.form.get("edTitle", "").strip()
        product_description = flask.request.form.get("edDescription", "").strip()
        product_start_price = flask.request.form.get("edStartPrice", "").strip().replace(",", ".")
        product_start_date = flask.request.form.get("edStartDate", "").strip()
        product_end_date = flask.request.form.get("edEndDate", "").strip()
        new_files = flask.request.files.getlist('edFiles[]')

        # Comprueba si se han rellenado todos los campos obligatorios
        if (not product_title
                or not product_description
                or not product_start_price
                or not product_start_date
                or not product_end_date):
            flask.flash("Faltan datos del producto.")
            return flask.redirect(flask.url_for("product_blpr.add"))
        ...

        product_start_price = safe_float_conversion(product_start_price)
        if product_start_price is None:
            flask.flash("El precio de salida debe ser un número.")
            return flask.redirect(flask.url_for("product_blpr.add"))
        ...

        product_start_price = round(float(product_start_price), 2)

        if product_start_price <= 0:
            flask.flash("El precio de salida debe ser mayor que 0.")
            return flask.redirect(flask.url_for("product_blpr.add"))
        ...

        # Añadir nuevos archivos
        filenames = []
        for file in new_files:
            if file and file.filename != '':
                try:
                    if allowed_file(file.filename):
                        file_extension = file.filename.rsplit('.', 1)[1].lower()
                        file_name_add = secure_filename(f'{uuid.uuid4()}.{file_extension}')
                        file_path = os.path.join('.' + load_config()['MULTIMEDIA_DATA_FOLDER'], file_name_add)
                        file.save(file_path)
                        filenames.append(file_name_add)
                    else:
                        flask.flash("Tipo de archivo no permitido.")
                        return flask.redirect(flask.url_for("product_blpr.add"))
                except OSError:
                    flask.flash(f"Error al añadir el archivo {file.filename}")
                    return flask.redirect(flask.url_for("product_blpr.add"))
        ...

        # Limpia posible XSS de los campos de texto
        clean_title = bleach.clean(product_title)
        clean_description = bleach.clean(product_description)

        start_date = datetime.strptime(product_start_date, '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(product_end_date, '%Y-%m-%dT%H:%M')

        new_product = Product(clean_title, clean_description, product_start_price, start_date, end_date, filenames, usr.email)
        oid = srp.save(new_product)
        flask.flash(f"Subasta de '{product_title}' añadida.")
        return flask.redirect(f'/product/{srp.safe_from_oid(oid)}')


@product_blpr.route("/<product_id>/edit", methods=["GET", "POST"])
@flask_login.login_required
def edit(product_id):
    usr = User.current()
    if usr is None:
        flask.abort(401)

    product: Product = get_product(product_id)
    if product is None:
        flask.abort(404)

    if product.email_owner != usr.email:
        flask.abort(403)

    if flask.request.method == "GET":
        sust = {
            "title": "Editar subasta",
            "product_id": product.get_safe_id(srp),
            "usr": usr,
            "edTitle": product.title,
            "edDescription": product.description,
            "edStartPrice": product.price,
            "edStartDate": product.auction_open_date.strftime("%Y-%m-%dT%H:%M"),
            "edEndDate": product.auction_close_date.strftime("%Y-%m-%dT%H:%M"),
            "edFiles": product.media_file_names,
            "data_dir": load_config()['MULTIMEDIA_DATA_FOLDER']
        }
        return flask.render_template("product_edit_form.jinja2", **sust)
    else:
        # Recogemos los datos del formulario
        product_title = flask.request.form.get("edTitle", "").strip()
        product_description = flask.request.form.get("edDescription", "").strip()
        product_start_price = flask.request.form.get("edStartPrice", "").strip().replace(",", ".")
        product_start_date = flask.request.form.get("edStartDate", "").strip()
        product_end_date = flask.request.form.get("edEndDate", "").strip()
        new_files = flask.request.files.getlist('edFiles[]')
        delete_files = flask.request.form.getlist('delete_files')

        # Comprueba si se han rellenado todos los campos obligatorios
        if (not product_title
                or not product_description
                or not product_start_price
                or not product_start_date
                or not product_end_date):
            flask.flash("Faltan datos del producto.")
            return flask.redirect(flask.url_for("product_blpr.edit", product_id=product_id))

        product_start_price = safe_float_conversion(product_start_price)
        if product_start_price is None:
            flask.flash("El precio de salida debe ser un número.")
            return flask.redirect(flask.url_for("product_blpr.edit", product_id=product_id))
        ...

        product_start_price = round(float(product_start_price), 2)

        if product_start_price <= 0:
            flask.flash("El precio de salida debe ser mayor que 0.")
            return flask.redirect(flask.url_for("product_blpr.edit", product_id=product_id))
        ...

        # Eliminar archivos marcados para eliminarse
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

        # Añadir nuevos archivos
        for file in new_files:
            if file and file.filename != '':
                try:
                    if allowed_file(file.filename):
                        file_extension = file.filename.rsplit('.', 1)[1].lower()
                        file_name_add = secure_filename(f'{uuid.uuid4()}.{file_extension}')
                        file_path = os.path.join('.' + load_config()['MULTIMEDIA_DATA_FOLDER'], file_name_add)
                        file.save(file_path)
                        product.add_media_file_name(file_name_add)
                    else:
                        flask.flash("Tipo de archivo no permitido.")
                        return flask.redirect(flask.url_for("product_blpr.edit", product_id=product_id))
                except OSError:
                    flask.flash(f"Error al añadir el archivo {file.filename}")
                    return flask.redirect(flask.url_for("product_blpr.edit", product_id=product_id))
        ...

        # Limpia posible XSS de los campos de texto
        clean_title = bleach.clean(product_title)
        clean_description = bleach.clean(product_description)

        start_date = datetime.strptime(product_start_date, '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(product_end_date, '%Y-%m-%dT%H:%M')

        # Guardar producto, sustituyendo los datos antiguos por los nuevos
        product.title = clean_title
        product.description = clean_description
        product.price = product_start_price
        product.auction_open_date = start_date
        product.auction_close_date = end_date

        srp.save(product)
        flask.flash(f"Subasta de '{product_title}' editada.")
        return flask.redirect(flask.url_for("product_blpr.detail", product_id=product_id))


@product_blpr.route("<product_id>/delete", methods=["GET", "POST"])
@flask_login.login_required
def delete(product_id):
    product = get_product(product_id)
    if product is None:
        flask.abort(404)
    ...
    if product.email_owner != User.current().email:
        flask.abort(403)
    ...

    if flask.request.method == "GET":
        sust = {
            "title": f"Borrar subasta de {product.title}",
            "usr": User.current(),
            "product": product,
            "srp": srp
        }

        return flask.render_template("product_delete_form.jinja2", **sust)
    else:
        product_oid = srp.oid_from_safe(product_id)

        if srp.exists(product_oid):

            # Elimina los archivos multimedia
            for file_name in product.media_file_names:
                file_path = os.path.join('.' + load_config()['MULTIMEDIA_DATA_FOLDER'], file_name)
                try:
                    os.remove(file_path)
                except OSError:
                    flask.flash(f"Error al eliminar el archivo {file_name}")
            ...

            # Elimina los comentarios
            for comment_oid in product.get_comments_oid():
                if srp.exists(comment_oid):
                    srp.delete(comment_oid)
            ...

            # Elimina las pujas
            for bid_oid in product.bids_oid:
                if srp.exists(bid_oid):
                    srp.delete(bid_oid)
            ...

            # Elimina la subasta
            srp.delete(product_oid)

            flask.flash("Subasta borrada.")
        else:
            flask.flash("Subasta no encontrada.")
        ...

        return flask.redirect(flask.url_for("product_blpr.list_products"))


@product_blpr.route('<product_id>/', methods=['GET'])
def detail(product_id):

    product = get_product(product_id)
    if product is None:
        flask.abort(404)

    # Obtén todos los elementos que cumplen la condición
    bids = srp.multi_load(product.bids_oid)

    # Ordena los elementos por precio en orden descendente
    bids_sorted_by_price = sorted(bids, key=lambda b: b.amount, reverse=True)

    # Obtén los últimos 10 elementos
    last_10_bids = bids_sorted_by_price[:10]

    for bid in last_10_bids:
        try:
            user = srp.filter(User, lambda u: u.email == bid.email_owner)
            if user:
                bid.name_owner = next(user).name
        except StopIteration:
            bid.name_owner = "Usuario eliminado"

    total_bids = len(bids_sorted_by_price)

    remaining_time = product.auction_close_date - datetime.now()
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Comentarios
    product_oid = srp.oid_from_safe(product_id)
    comments = srp.filter(Comment, lambda c: c.product_oid == product_oid)

    sust = {
        "title": product.title,
        "usr": User.current(),
        "product": product,
        "bids": last_10_bids,
        "total_bids": total_bids,
        "multimedia_data_folder": load_config()['MULTIMEDIA_DATA_FOLDER'] + '/',
        "remaining_time": f"{days} días, {hours} horas y {minutes} minutos",
        "open_date": format(product.auction_open_date, "%d/%m/%Y %H:%M"),
        "close_date": format(product.auction_close_date, "%d/%m/%Y %H:%M"),
        "srp": srp,
        "comments": comments
    }
    return flask.render_template('product_detail.jinja2', **sust)


def safe_float_conversion(s):
    try:
        return float(s)
    except ValueError:
        return None


def get_product(product_id):
    product_oid = srp.oid_from_safe(product_id)
    if product_oid is None:
        return None
    product = srp.load(product_oid)
    if product is None:
        return None
    return product


def allowed_file(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    else:
        return None


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}