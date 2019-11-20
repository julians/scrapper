from flask import Flask, render_template, url_for
from models import Item, Metadata, ItemMetadata
from peewee import fn
from config import db
import arrow
import mistune
import arrow
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


def get_metadata(item):
    metadata_query = (
        Metadata.select().join(ItemMetadata).join(Item).where(Item.id == item.id)
    )
    metadata = [x for x in metadata_query]
    return metadata


def render_item(item, force_random_bucket=None):
    metadata = get_metadata(item)

    return render_template(
        "detail.jinja2",
        bucket=item.bucket,
        text=markdown(item.get_typographic_text()),
        created_at=arrow.get(item.created_at),
        metadata=metadata,
        language=item.language,
        id=item.id,
        base_url=format(url_for("index")),
        force_random_bucket=force_random_bucket,
    )


application = Flask(__name__)
auth = HTTPBasicAuth()
renderer = mistune.Renderer(hard_wrap=True)
markdown = mistune.Markdown(renderer=renderer)

users = {"julian": generate_password_hash("pomepomepome")}


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@application.before_request
def _db_connect():
    db.connect()


@application.route("/")
def index():
    return "hello juhu {}".format(url_for("index"))


@application.route("/random")
@auth.login_required
def random():
    item = Item.select().order_by(fn.Random()).get()

    return render_item(item)


@application.route("/random/<bucket>")
@auth.login_required
def random_type(bucket):
    item = Item.select().where(Item.bucket == bucket).order_by(fn.Random()).get()

    return render_item(item, bucket)


@application.route("/view/<int:item_id>")
@auth.login_required
def view(item_id):
    item = Item.select().where(Item.id == item_id).get()

    return render_item(item)


# @application.route("/view/<int:item_id>")
# def view(item_id):
#     item = Item.select().where(Item.id == item_id)
#     metadata = get_metadata(item)

#     if not len(item):
#         return "404"


@application.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


if __name__ == "__main__":
    application.run(host="0.0.0.0")

