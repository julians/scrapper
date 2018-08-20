from flask import Flask, render_template
from models import Item, Metadata, ItemMetadata
from peewee import fn
from config import db
import arrow
import mistune
import arrow


def get_metadata(item):
    metadata_query = (
        Metadata.select().join(ItemMetadata).join(Item).where(Item.id == item.id)
    )
    metadata = [x for x in metadata_query]
    return metadata


app = Flask(__name__)
renderer = mistune.Renderer(hard_wrap=True)
markdown = mistune.Markdown(renderer=renderer)


@app.before_request
def _db_connect():
    db.connect()


@app.route("/")
def index():
    return "hello"


@app.route("/random")
@app.route("/view/<int:item_id>")
def random(item_id=None):
    if item_id:
        item = Item.select().where(Item.id == item_id).get()
    else:
        item = Item.select().order_by(fn.Random()).get()
    metadata = get_metadata(item)

    return render_template(
        "detail.jinja2",
        bucket=item.bucket,
        text=markdown(item.get_typographic_text()),
        created_at=arrow.get(item.created_at),
        metadata=metadata,
        language=item.language,
        id=item.id,
    )


# @app.route("/view/<int:item_id>")
# def view(item_id):
#     item = Item.select().where(Item.id == item_id)
#     metadata = get_metadata(item)

#     if not len(item):
#         return "404"


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()
