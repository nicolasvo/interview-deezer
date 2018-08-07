import pandas as pd
from pymongo import MongoClient
import json

client = MongoClient('mongo')
db = client['deezer']

df_artist = pd.read_table('res/artists.dat')
df_tag = pd.read_table('res/tags.dat', encoding='latin-1')
df_user_artist = pd.read_table('res/user_artists.dat')
df_user_friend = pd.read_table('res/user_friends.dat')
df_user_tagged_artist = pd.read_table('res/user_taggedartists.dat')
df_user_tagged_artist_timestamp = pd.read_table('res/user_taggedartists-timestamps.dat')

# Here I wanted clean IDs, so I inserted each document in a loop
for index, row in df_artist.iterrows():
    db['artist'].insert_one({'_id': row['id'], 'name': row['name'], 'url': row['url'], 'picture': row['pictureURL']})

for index, row in df_tag.iterrows():
    db['tag'].insert_one({'_id': row['tagID'], 'value': row['tagValue']})

# Here I wasn't interested in IDs
db['user_artist'].insert(json.loads(df_user_artist.to_json(orient='records')))
db['user_friend'].insert(json.loads(df_user_friend.to_json(orient='records')))

# I noticed the timestamps had 3 too many zeros, therefore I striped them before converting to the datetime format
df_user_tagged_artist_timestamp['timestamp'] = df_user_tagged_artist_timestamp['timestamp'].apply(lambda x: int(str(x)[:-3]))
df_user_tagged_artist_timestamp['timestamp_ok'] = pd.to_datetime(df_user_tagged_artist_timestamp['timestamp'], unit='s')

for index, row in df_user_tagged_artist_timestamp.iterrows():
    db['user_tagged_artist'].insert_one({
        'user_id': row['userID'],
        'artist_id': row['artistID'],
        'tag_id': row['tagID'],
        'timestamp': row['timestamp_ok'],
    })
