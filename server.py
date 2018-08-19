from flask import Flask, render_template
from models import Item, Metadata, ItemMetadata
from peewee import fn
from config import db
import mistune
from smartquotes import smartyPants
import arrow


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
def random():
    random_scrap = Item.select().order_by(fn.Random()).get()
    metadata_query = (
        Metadata.select()
        .join(ItemMetadata)
        .join(Item)
        .where(Item.id == random_scrap.id)
    )
    metadata = [x for x in metadata_query]

    typographic_languages = {"de": "de-x-altquot"}
    typographic_language = typographic_languages.get(
        random_scrap.language, random_scrap.language
    )
    text = smartyPants(random_scrap.text, language=typographic_language)

    return render_template(
        "random_scrap.jinja2",
        bucket=random_scrap.bucket,
        text=markdown(text),
        created_at=arrow.get(random_scrap.created_at),
        metadata=metadata,
        language=random_scrap.language,
    )


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()
