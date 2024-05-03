import requests
import os
import time

from Video import Video
import storageGoogle as storage_engine

class Transcript:
    def __init__(self, video, video_progress):
        self.video = video
        self.transcription_file = f"results/{self.video.get_videoId()}/transcription.txt"
        self.video_progress = video_progress
        self.transcript = None

    def get_transcription(self):
        if self.transcript != None:
            return self.transcript

        if (os.path.exists(self.transcription_file) == False):
            vid = storage_engine.generate_download_signed_url_v4(f"reelify_ai/user_data/{self.video.get_videoId()}/input_video.mp4")
            print(vid)
            content = self.generate_transcript(vid, self.video.get_videoId())
        else:
            try:
                with open(self.transcription_file, 'r', encoding='utf-8') as file:
                    content = file.read()
            except IOError:
                print("Error: Failed to read the transcription file. Recreating it now.")
                os.remove(self.transcription_file)
                return self.get_transcription()

        self.transcript = content

        return content

    def generate_transcript(self, url, guid_hash):

        self.video_progress.updateProgress(stage="Transcription", progress=7)
        
        api_url = "https://yuvrajjsingh0--tawk2ai-transcription-fastapi-app.modal.run/api/transcribe"
        params = {"url": url, "guid_hash": guid_hash}
        response = requests.post(api_url, params=params)
        
        # Check if request was successful
        if response.status_code != 200:
            print("Error calling API:", response.text)
            return None
        
        # Extract call_id from response
        call_id = response.json().get("call_id")
        print(call_id)
        self.video_progress.updateProgress(stage="Transcription", progress=10)
        
        # Step 2: Call the second API to get status
        while True:
            status_url = f"https://yuvrajjsingh0--tawk2ai-transcription-fastapi-app.modal.run/api/status/{call_id}"
            status_response = requests.get(status_url)
            print(status_response.json())
            
            progress = 10

            totSegments = status_response.json().get("total_segments")
            donSegments = status_response.json().get("done_segments")

            calcProgress = ((totSegments/donSegments)*100 - 25)

            if calcProgress > progress:
                progress = calcProgress

            self.video_progress.updateProgress(stage="Transcription", progress=progress)

            # Check if request was successful
            if status_response.status_code != 200:
                print("Error calling status API:", status_response.text)
                return None
            
            # Check if transcription is finished
            if status_response.json().get("finished"):
                break  # Move to next step
            
            # If transcription is not finished, wait for 10 seconds and try again
            time.sleep(10)
        
        # Step 3: Call the third API to get episode
        episode_url = f"https://yuvrajjsingh0--tawk2ai-transcription-fastapi-app.modal.run/api/episode/{guid_hash}"
        episode_response = requests.get(episode_url)
        
        # Check if request was successful
        if episode_response.status_code != 200:
            print("Error calling episode API:", episode_response.text)
            return None
        
        # Return the result
        transcript = episode_response.json()
        try:
            with open(self.transcription_file, 'w', encoding='utf-8') as file:
                file.write(json.dumps(transcript, ensure_ascii=False))
        except IOError:
            print("Error: Failed to write the transcription file.")

        print(transcript)

        return transcript
