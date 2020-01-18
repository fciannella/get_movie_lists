import os
from google.cloud import firestore


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/fciannel/.ssh/fciannel-apps-62b24a3b535e.json"


# Add a new document
db = firestore.Client()

collection = db.collection(u'mubi_movies')

# data = {'movie_name':"yakuza"}
#
# collection.add(data)

def add_movie(data, id):
    movie_ref = collection.document(id)
    movie_ref.set(data, merge=True)
    return True


def check_if_exists(ids):

    docs = collection.where(u'capital', u'==', True).stream()