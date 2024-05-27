import flask
import flask_login
import sirope
from datetime import datetime

from redis import Redis
from config import load_config

from model.Bid import Bid
from model.User import User


def get_blprint():
    bid_module = flask.blueprints.Blueprint("bid_blpr", __name__,
                                            url_prefix="/bid",
                                            template_folder="templates/bid",
                                            static_folder="static/bid")
    syrp = sirope.Sirope(Redis.from_url(load_config()['REDISCLOUD_URL']))
    return bid_module, syrp


bid_blpr, srp = get_blprint()


def create_dict_view(new_product, bid) -> dict:
    return {
        'product': new_product,
        'num_own_bids': 1,
        'num_bids': len(new_product.bids_oid),
        'main_bid': new_product.price == bid.amount,
        'your_last_bid': bid,
    }


def update_existing_dict(existing_dict, bid):
    if existing_dict['product'].price == bid.amount:
        existing_dict['main_bid'] = True
        existing_dict['your_last_bid'] = bid
    elif existing_dict['your_last_bid'].amount < bid.amount:
        existing_dict['your_last_bid'] = bid
    ...
    existing_dict['num_own_bids'] += 1


@bid_blpr.route("/", methods=["GET"])
@flask_login.login_required
def list():
    usr = User.current()
    bids = srp.filter(Bid, lambda b: b.email_owner == usr.email)

    bids_opened = []
    bids_closed = []

    for bid in bids:
        bid_list = bids_opened if not any(bid.product_oid == srp.oid_from_safe(d['product'].get_safe_id(srp)) for d in bids_closed) else bids_closed

        existing_dict = next((d for d in bid_list if srp.oid_from_safe(d['product'].get_safe_id(srp)) == bid.product_oid), None)

        if existing_dict:
            update_existing_dict(existing_dict, bid)
        else:
            new_product = srp.load(bid.product_oid)
            new_dict = create_dict_view(new_product, bid)
            if new_product.status == 'closed':
                bids_closed.append(new_dict)
            else:
                bids_opened.append(new_dict)

    sust = {
        "title": "Mis pujas",
        "usr": usr,
        "bids_opened": bids_opened,
        "bids_closed": bids_closed,
        "srp": srp,
        "no_bids": not (bids_opened or bids_closed)
    }

    return flask.render_template("bid_dashboard.jinja2", **sust)


@bid_blpr.route("add", methods=["POST"])
@flask_login.login_required
def add():
    usr = User.current()
    product_id = flask.request.form.get("edProductId", "").strip()
    bid_amount = float(flask.request.form.get("edAmount", "").strip())

    if product_id == "":
        flask.flash("Ha ocurrido un error al intentar pujar por el producto")
        return flask.redirect(flask.url_for('product_blpr.detail', product_id=product_id))

    product_oid = srp.oid_from_safe(product_id)
    product = srp.load(product_oid)
    if product is None:
        flask.flash("Producto no encontrado")
        return flask.abort(404)

    if bid_amount <= product.price:
        flask.flash(f"La cantidad a pujar debe ser mayor que {product.price}")
        return flask.redirect(flask.url_for('product_blpr.detail', product_id=product_id))

    if product.status != 'open':
        flask.flash("No puedes pujar porque la puja está cerrada en este momento")
        return flask.redirect(flask.url_for('product_blpr.detail', product_id=product_id))

    bid = Bid(product_oid, bid_amount, datetime.now(), usr.email)
    bid_oid = srp.save(bid)

    product.add_bid_oid(bid_oid)
    product.price = bid_amount
    srp.save(product)

    return flask.redirect(flask.url_for('product_blpr.detail', product_id=product_id))