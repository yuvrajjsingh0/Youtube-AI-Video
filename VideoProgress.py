import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./service.json")
fire_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'reelsify-65e45.appspot.com'
})

db = firestore.client()

class VideoProgress:
    def __init__(self, video_id):
        self.data = {
            "finished": False,
            "generated_short_urls": "",
            "interesting_parts": "",
            "progress": 0,
            "stage": "Init",
            "transcription": "",
            "videos": []
        }
        self.fireDoc = db.collection("reels").document(video_id)
        self.fireDoc.set(self.data)
        print("init firebase firestore")

    def updateProgress(
        self,
        finished = False,
        generated_short_urls = "",
        interesting_parts = "",
        progress = 0,
        stage = "",
        transcription = ""
    ):
        self.fireDoc.set({"progress": progress, "stage": stage, "finished": finished}, merge=True)

    def addVideo(self, video_url):
        self.fireDoc.set({"videos": firestore.ArrayUnion([video_url])})