from pytube import YouTube
import time
import os
import storageGoogle as storage_engine

from VideoProgress import VideoProgress

class Video:
    video_id = ''
    def __init__(self, video_url, video_id, video_progress):
        self.video_url = video_url
        self.video_id = video_id
        self.video_local_path = f"tmp/{self.video_id}/input_video.mp4"
        self.video_progress = video_progress

        if (os.path.exists(self.video_local_path) == False):
            self.download_video(self.video_url)
        
        if (storage_engine.file_exists(f'reelify_ai/user_data/{self.video_id}/input_video.mp4') == False):
            storage_engine.upload_blob(self.video_local_path, f'reelify_ai/user_data/{self.video_id}/input_video.mp4')

        self.video_remote_path = storage_engine.generate_download_signed_url_v4(f'reelify_ai/user_data/{self.video_id}/input_video.mp4')

    def get_videoPath(self):
        return self.video_local_path

    def get_videoId(self):
        return self.video_id

    def download_video(self, url):
        self.video_progress.updateProgress(stage="Download", progress=1)
        yt = YouTube(url)
        video = yt.streams.filter(file_extension='mp4').get_highest_resolution()
        video.download(filename='input_video.mp4', output_path='tmp/'+self.video_id + '/')
        self.video_progress.updateProgress(stage="Download", progress=5)