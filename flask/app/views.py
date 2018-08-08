##
from flask import render_template, request
from .forms import ArtistForm, TagForm

from app import app
from datetime import datetime
from collections import Counter
from pymongo import MongoClient

client = MongoClient("mongo")
db = client['deezer']


@app.route('/', methods=['GET', 'POST'])
def home():

    artist_form = ArtistForm()
    tag_form = TagForm()

    return render_template('index.html', artist_form=artist_form, tag_form=tag_form)


@app.route('/artist', methods=['POST'])
def artist():

    output = {}
    artist_form = ArtistForm()
    if artist_form.validate_on_submit():
        list_document = []

        dict_fetch = {}
        for x in ['artist', 'tag', 'date']:
            dict_fetch[x] = request.form.get(x, None)
        print("... here", dict_fetch)
        mongo_formatted_string = {}
        
        if dict_fetch.get('artist'):
            mongo_formatted_string.update({'name': {'$regex': "\\b" + dict_fetch['artist'], '$options': 'i'}})

        if mongo_formatted_string:
            for document in db["artist"].find(mongo_formatted_string):
                document_updated = {"redirect_app": "/artist/{0}".format(document["_id"])}
                document_updated.update({key: (document[key] if document.get(key) else "") for key in ("name", "url", "picture")})
                # The picture URLs do not work for most of them (if not all).
                document_updated.pop("picture")

                # Get artist tag preview
                has_tag = False
                list_tag = []
                for elt in db["user_tagged_artist"].find({'artist_id': document["_id"]}):
                    list_tag.append(elt['tag_id'])
                # If specific tag is wanted in addition to artist name
                if len(dict_fetch["tag"])>0:
                    if list_tag:
                        list_tag_name = []
                        for tag in list_tag:
                            list_tag_name.append(db['tag'].find_one({'_id': tag})['value'])
                        for tag in set(list_tag_name):
                            if dict_fetch["tag"] in tag:
                                has_tag = True
                                break
                        if has_tag:
                            list_tag_top = [elt[0] for elt in Counter(list_tag_name).most_common(3)]
                            document_updated.update({"tag_top": list_tag_top})
                            list_document.append(document_updated)
                else:
                    if list_tag:
                        list_tag_name = []
                        for tag in list_tag:
                            list_tag_name.append(db['tag'].find_one({'_id': tag})['value'])
                        list_tag_top = [elt[0] for elt in Counter(list_tag_name).most_common(3)]
                        document_updated.update({"tag_top": list_tag_top})
                    list_document.append(document_updated)
            output["list_document"] = list_document

    return render_template('artist.html', output=output)


@app.route('/tag', methods=['POST'])
def tag():

    output = {}
    tag_form = TagForm()
    if tag_form.validate_on_submit():
        list_document = []
        dict_fetch = {}
        for x in ['tag']:
            dict_fetch[x] = request.form.get(x, None)

        mongo_formatted_string = {}

        if dict_fetch.get('tag'):
            mongo_formatted_string.update({'value': {'$regex': "\\b" + dict_fetch['tag'], '$options': 'i'}})

        if mongo_formatted_string:
            for document in db["tag"].find(mongo_formatted_string):
                document_updated = {"redirect_app": "/tag/{0}".format(document["_id"])}
                document_updated.update({"value": document["value"]})
                list_document.append(document_updated)

                # Get top artists preview
                list_artist = []
                for elt in db["user_tagged_artist"].find({'tag_id': document["_id"]}):
                    list_artist.append(elt['artist_id'])
                if list_artist:
                    list_artist_name = []
                    for artist in list_artist:
                        if db['artist'].find_one({'_id': artist}):
                            list_artist_name.append(db['artist'].find_one({'_id': artist})['name'])
                        list_artist_top = [elt[0] for elt in Counter(list_artist_name).most_common(3)]
                        document_updated.update({"artist_top": list_artist_top})

    output["list_document"] = list_document

    return render_template('tag.html', output=output)


@app.route('/artist/<artist_id>')
def artist_id(artist_id):

    output = {}
    dict_tag = {}
    dict_tag_count = {}
    list_tag = []
    for elt in db["user_tagged_artist"].find({'artist_id': int(artist_id)}):
        list_tag.append(elt['tag_id'])

    for tag in set(list_tag):
        dict_tag.update({tag: db['tag'].find_one({'_id': tag})["value"]})
        dict_tag_count.update({tag: {'value': db['tag'].find_one({'_id': tag})["value"],
                               'count': list_tag.count(tag)}})

    output["dict_tag"] = dict_tag
    output["artist"] = db["artist"].find_one({'_id': int(artist_id)})
    output["dict_tag_count"] = dict_tag_count
    output["list_tag_sorted"] = sorted(dict_tag_count, key=lambda x: dict_tag_count[x]['count'], reverse=True)

    return render_template('artist_id.html', output=output)


@app.route('/tag/<tag_id>')
def tag_id(tag_id):

    output = {}

    list_artist = []
    for elt in db["user_tagged_artist"].find({'tag_id': int(tag_id)}):
        list_artist.append(elt['artist_id'])

    list_document = []
    for artist_id in list_artist:
        document_temp = db["artist"].find_one({'_id': artist_id})
        if document_temp:
            document_updated = {"redirect_app": f"/artist/{artist_id}"}
            document_updated.update({"name": document_temp["name"],
                                     "url": document_temp["url"]})

            list_document.append(document_updated)

    output["list_document"] = list_document
    output["tag"] = db["tag"].find_one({"_id": int(tag_id)})["value"]

    return render_template('tag_id.html', output=output)
