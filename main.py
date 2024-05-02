import time
from fastapi import BackgroundTasks, FastAPI

from Video import Video
from Transcript import Transcript
from VideoProcessor import VideoProcessor
from VideoProgress import VideoProgress

app = FastAPI()

def make_shorts_from_video(video_url: str, video_id: str):
    video_progress = VideoProgress(video_id)

    video = Video(video_url, video_id, video_progress)
    transcript = Transcript(video, video_progress)

    video_processor = VideoProcessor(video, transcript, video_progress)

    video_processor.start()

@app.post("/make_shorts")
async def make_shorts(video_url: str, background_tasks: BackgroundTasks):
    video_id = str(time.time()) + ""
    #video_id = "1714556148.3930402"
    background_tasks.add_task(make_shorts_from_video, video_url, video_id)
    return {"message": "Video added to queue", "video_id": video_id}