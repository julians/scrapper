from flask import Flask, render_template, url_for
from models import Item, Metadata, ItemMetadata
from peewee import fn
from config import db
import arrow
import mistune
import arrow
import re

# from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


def get_metadata(item):
    metadata_query = (
        Metadata.select().join(ItemMetadata).join(Item).where(Item.id == item.id)
    )
    metadata = [x for x in metadata_query]
    return metadata


highlight_regex = re.compile(r"(?:\{==|\:\:)(.+)(?:==\}|\:\:)", re.DOTALL)


def highlight(text):
    highlight_match = highlight_regex.search(text)
    if highlight_match:
        replacement = '<em class="highlight">{}</em>'.format(highlight_match.group(1))
        return text.replace(highlight_match.group(0), replacement)

    return text


def render_item(item, force_random_bucket=None):
    metadata = get_metadata(item)
    text = None
    if item.text:
        text = highlight(markdown(item.get_typographic_text()))

    return render_template(
        "detail.jinja2",
        bucket=item.bucket,
        text=text,
        image=item.image,
        created_at=arrow.get(item.created_at),
        metadata=metadata,
        language=item.language,
        id=item.id,
        hashid=item.hashid,
        short_hashid=item.hashid[:7],
        base_url=format(url_for("index")),
        force_random_bucket=force_random_bucket,
    )


application = Flask(__name__)
# auth = HTTPBasicAuth()
renderer = mistune.Renderer(hard_wrap=True)
markdown = mistune.Markdown(renderer=renderer)

users = {"julian": generate_password_hash("pomepomepome")}


# @auth.verify_password
# def verify_password(username, password):
#     if username in users:
#         return check_password_hash(users.get(username), password)
#     return False


@application.before_request
def _db_connect():
    db.connect()


@application.route("/")
def index():
    return "hello juhu {}".format(url_for("index"))


@application.route("/random", defaults={"bucket": None})
@application.route("/random/<bucket>")
# @auth.login_required
def random_type(bucket):
    if bucket:
        item = Item.select().where(Item.bucket == bucket).order_by(fn.Random()).get()
    else:
        item = Item.select().order_by(fn.Random()).get()

    return render_item(item, bucket)


@application.route("/random-image", defaults={"bucket": None})
@application.route("/random-image/<bucket>")
# @auth.login_required
def random_image(bucket):
    if bucket:
        item = (
            Item.select()
            .where(Item.bucket == bucket)
            .where(Item.image != None)
            .order_by(fn.Random())
            .get()
        )
    else:
        item = Item.select().where(Item.image != None).order_by(fn.Random()).get()

    return render_item(item)


@application.route("/view/<string:item_hashid>")
# @auth.login_required
def view(item_hashid):
    item = Item.select().where(Item.hashid == item_hashid).get()

    return render_item(item)


@application.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


if __name__ == "__main__":
    application.run(host="0.0.0.0")

