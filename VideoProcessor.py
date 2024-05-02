import cv2
import subprocess

from Video import Video
from Transcript import Transcript

from common import extract_json

import json

import storageGoogle as storage_engine

from VideoProgress import VideoProgress

class VideoProcessor:
    def __init__(self, video: Video, transcript: Transcript, video_progress: VideoProgress):
        self.video = video
        self.transcript = transcript
        self.video_progress = video_progress

    def generate_viral_gemini(self, transcript):
        import google.generativeai as genai
        GEMINI_API_KEY = 'AIzaSyC3DvzZIbU3s33bPsKFrMcgZpI5ljiQAmI'
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        json_template = '''
            { "segments" :
                [
                    {
                        "start_time": "00.00", 
                        "end_time": "00.00",
                        "description": "Description of the text",
                        "duration":"00",
                    },    
                ]
            }
        '''

        prompt = f"Given the following video transcript, analyze each part for potential virality and identify the 3 most viral segments from the transcript. Each segment should have nothing less than 120 seconds in duration. The provided transcript is as follows: {transcript}. Based on your analysis, return a JSON document containing the extremely accurate timestamps (start and end), the description of the viral part, and its duration. The JSON document should follow this format: {json_template}. Please replace the placeholder values with the actual results from your analysis. Maintain the data type and keep in mind that start and end time need to show seconds elapsed"
        system = f"System Prompt: You are a Viral Segment Identifier, an AI system that analyzes a video's transcript and predict which segments might go viral on social media platforms. You use factors such as emotional impact, humor, unexpected content, and relevance to current trends to make your predictions. You return a structured JSON document detailing the start and end times, the description, and the duration of the potential viral segments."
        
        chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": [{ "text": system}],
            },
            {
                "role": "model",
                "parts": [{ "text": "Understood."}],
            },
        ])

        response = chat.send_message(prompt)
        json_res = extract_json(response.text)
        if json_res == None:
            print("Error: Invalid response from Gemini. Retrying")
            print(response)
            print(response.text)
            return self.generate_viral_gemini(transcript)
        return json_res

    def generate_segments(self, response):
        for i, segment in enumerate(response):
            print(i, segment)

            start_time = int(segment.get("start_time", 0).split('.')[0])
            end_time = int(segment.get("end_time", 0).split('.')[0])

            # pt = datetime.datetime.strptime(start_time,'%H:%M:%S')
            # start_time = pt.second + pt.minute*60 + pt.hour*3600

            # pt = datetime.datetime.strptime(end_time,'%H:%M:%S')
            # end_time = pt.second + pt.minute*60 + pt.hour*3600

            if end_time - start_time < 50:
                end_time += (50 - (end_time - start_time))

            output_file = f"output{str(i).zfill(3)}.mp4"
            command = f"ffmpeg -y -hwaccel d3d11va -i tmp/{self.video.get_videoId()}/input_video.mp4 -vf scale='1920:1080' -qscale:v 3 -b:v 6000k -ss {start_time} -to {end_time} tmp/{self.video.get_videoId()}/{output_file}"
            subprocess.call(command, shell=True)

    def generate_short(self, input_file, output_file):
        try:

            # Interval to switch faces (in frames) (ex. 150 frames = 5 seconds, on a 30fps video)
            switch_interval = 150

            # Frame counter
            frame_count = 0

            # Index of the currently displayed face
            current_face_index = 0
            
            # Constants for cropping    
            CROP_RATIO_BIG = 1 # Adjust the ratio to control how much of the image (around face) is visible in the cropped video
            CROP_RATIO_SMALL = 0.5
            VERTICAL_RATIO = 9 / 16  # Aspect ratio for the vertical video

            # Load pre-trained face detector from OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Open video file
            cap = cv2.VideoCapture(f"tmp/{self.video.get_videoId()}/{input_file}")

            # Get the frame dimensions
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Image frame_height {frame_height}, frame_width {frame_width}")

            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(f"tmp/{self.video.get_videoId()}/{output_file}", fourcc, 30, (1080, 1920))  # Adjust resolution for 9:16 aspect ratio

            # success = False
            while(cap.isOpened()):
                # Read frame from video
                ret, frame = cap.read()

                if ret == True:
                    
                    # If we don't have any face positions, detect the faces
                    # Switch faces if it's time to do so
                    if frame_count % switch_interval == 0:
                        # Convert color style from BGR to RGB
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                        # Perform face detection
                        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(100, 100))
            
                        if len(faces) > 0:
                            # Initialize trackers and variable to hold face positions
                            trackers = cv2.legacy.MultiTracker_create()
                            face_positions = []
                            
                            for (x, y, w, h) in faces:
                                face_positions.append((x, y, w, h))
                                tracker = cv2.legacy.TrackerKCF_create()
                                tracker.init(frame, (x, y, w, h))
                                trackers.add(tracker, frame, (x, y, w, h))

                            # Update trackers and get updated positions
                            success, boxes = trackers.update(frame)

                        # Switch faces if it's time to do so
                        current_face_index = (current_face_index + 1) % len(face_positions)
                        x, y, w, h = [int(v) for v in boxes[current_face_index]]

                        print (f"Current Face index {current_face_index} heigth {h} width {w} total faces {len(face_positions)}")

                        face_center = (x + w//2, y + h//2)

                        if w * 16 > h * 9:
                            w_916 = w
                            h_916 = int(w * 16 / 9)
                        else:
                            h_916 = h
                            w_916 = int(h * 9 / 16)

                        #Calculate the target width and height for cropping (vertical format)
                        if max(h, w) < 345:
                            target_height = int(frame_height * CROP_RATIO_SMALL)
                            target_width = int(target_height * VERTICAL_RATIO)
                        else:
                            target_height = int(frame_height * CROP_RATIO_BIG)
                            target_width = int(target_height * VERTICAL_RATIO)

                    # Calculate the top-left corner of the 9:16 rectangle
                    x_916 = (face_center[0] - w_916 // 2)
                    y_916 = (face_center[1] - h_916 // 2)

                    crop_x = max(0, x_916 + (w_916 - target_width) // 2)  # Adjust the crop region to center the face
                    crop_y = max(0, y_916 + (h_916 - target_height) // 2)
                    crop_x2 = min(crop_x + target_width, frame_width)
                    crop_y2 = min(crop_y + target_height, frame_height)


                    # Crop the frame to the face region
                    crop_img = frame[crop_y:crop_y2, crop_x:crop_x2]
                    
                    resized = cv2.resize(crop_img, (1080, 1920), interpolation = cv2.INTER_AREA)
                    
                    out.write(resized)

                    frame_count += 1

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break

            # Release everything if job is finished
            cap.release()
            out.release()
            cv2.destroyAllWindows()

            # Extract audio from original video
            command = f"ffmpeg -y -hwaccel cuda -i tmp/{self.video.get_videoId()}/{input_file} -vn -acodec copy tmp/{self.video.get_videoId()}/output-audio.aac"
            subprocess.call(command, shell=True)

            # Merge audio and processed video
            command = f"ffmpeg -y -hwaccel cuda -i tmp/{self.video.get_videoId()}/{output_file} -i tmp/{self.video.get_videoId()}/output-audio.aac -c copy tmp/{self.video.get_videoId()}/final-{output_file}"
            subprocess.call(command, shell=True)

        except Exception as e:
            print(f"Error during video cropping: {str(e)}")

    def generate_subtitle(self, input_file, output_folder, results_folder):
        command = f"auto_subtitle tmp/{self.video.get_videoId()}/{input_file} -o {results_folder}/{output_folder} --output_srt True --model tiny"
        print (command)
        subprocess.call(command, shell=True)

    def start(self):
        self.video_progress.updateProgress(stage="Gemini", progress=82)
        viral_segments = self.generate_viral_gemini(self.transcript.get_transcription())
        parsed_content = json.loads(viral_segments)
        print(parsed_content)
        self.generate_segments(parsed_content['segments'])
        output_folder = f'tmp/{self.video.get_videoId()}/'
        
        progress = 85
        
        for i, segment in enumerate(parsed_content['segments']):  # Replace xx with the actual number of segments
            if i > 2:
                break
            input_file = f'output{str(i).zfill(3)}.mp4'
            output_file = f'output_cropped{str(i).zfill(3)}.mp4'
            self.generate_short(input_file, output_file)
            self.generate_subtitle(f"final-{output_file}", self.video.get_videoId(), output_folder)

            storage_engine.upload_blob(f'tmp/{self.video.get_videoId()}/{self.video.get_videoId()}/final-{output_file}', f'reelify_ai/user_data/{self.video.get_videoId()}/final-{output_file}')
            final_vid_url = storage_engine.generate_download_signed_url_v4(f'reelify_ai/user_data/{self.video.get_videoId()}/final-{output_file}')
            self.video_progress.addVideo(final_vid_url)
            self.video_progress.updateProgress(stage="Merging", progress=progress)
            progress += 5

        self.video_progress.updateProgress(finished=True, stage="Merging", progress=progress)