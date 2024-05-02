import sys
import numpy as np
from pytube import YouTube
import cv2
import subprocess
import openai
import json
import datetime
import os
from os import path
import shutil
import time

import argparse

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

cred = credentials.Certificate("./service.json")
fire_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'reelsify-65e45.appspot.com'
})

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("./service.json")

from google.cloud import storage

# Instantiates a client
storage_client = storage.Client(credentials=credentials)
bucket_name = "reelsify-65e45.appspot.com"
bucket = storage_client.bucket(bucket_name)


def generate_download_signed_url_v4(blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )

    print("Generated GET signed URL:")
    print(url)
    print("You can use this URL with any user agent, for example:")
    print(f"curl '{url}'")
    return url

def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )



# Download video
def download_video(url, filename):
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').get_highest_resolution()

    # Download the video
    # video.download(filename=filename, output_path='tmp/')
    upload_blob(f'tmp/{filename}', filename)



#Segment Video function
def generate_segments(response):
  
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
        command = f"ffmpeg -y -hwaccel d3d11va -i tmp/input_video.mp4 -vf scale='1920:1080' -qscale:v 3 -b:v 6000k -ss {start_time} -to {end_time} tmp/{output_file}"
        subprocess.call(command, shell=True)

def generate_short(input_file, output_file):
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
        cap = cv2.VideoCapture(f"tmp/{input_file}")

        # Get the frame dimensions
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Image frame_height {frame_height}, frame_width {frame_width}")

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f"tmp/{output_file}", fourcc, 30, (1080, 1920))  # Adjust resolution for 9:16 aspect ratio

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
        command = f"ffmpeg -y -hwaccel cuda -i tmp/{input_file} -vn -acodec copy tmp/output-audio.aac"
        subprocess.call(command, shell=True)

        # Merge audio and processed video
        command = f"ffmpeg -y -hwaccel cuda -i tmp/{output_file} -i tmp/output-audio.aac -c copy tmp/final-{output_file}"
        subprocess.call(command, shell=True)

    except Exception as e:
        print(f"Error during video cropping: {str(e)}")

def extract_json(string):
    # Find the start and end positions of the JSON data
    start_pos = string.find('{')
    end_pos = string.rfind('}') + 1
    
    if start_pos != -1 and end_pos != -1:
        # Extract the JSON data substring
        json_str = string[start_pos:end_pos]
        
        try:
            # Attempt to parse the extracted substring as JSON
            json_data = json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            # If parsing fails, return None or handle the error as needed
            return None
    else:
        return None


def generate_viral_gemini(transcript):
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

    prompt = f"Given the following video transcript, analyze each part for potential virality and identify the most viral segments from the transcript. Each segment should have nothing less than 120 seconds in duration. The provided transcript is as follows: {transcript}. Based on your analysis, return a JSON document containing the extremely accurate timestamps (start and end), the description of the viral part, and its duration. The JSON document should follow this format: {json_template}. Please replace the placeholder values with the actual results from your analysis."
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
    print(response.text)
    json_res = extract_json(response.text)
    if json_res == None:
        generate_viral_gemini(transcript)
    return json_res




def generate_viral(transcript): # Inspiredby https://github.com/NisaarAgharia/AI-Shorts-Creator 

    json_template = '''
        { "segments" :
            [
                {
                    "start_time": 00.00, 
                    "end_time": 00.00,
                    "description": "Description of the text",
                    "duration":00,
                },    
            ]
        }
    '''

    prompt = f"Given the following video transcript, analyze each part for potential virality and identify 3 most viral segments from the transcript. Each segment should have nothing less than 50 seconds in duration. The provided transcript is as follows: {transcript}. Based on your analysis, return a JSON document containing the timestamps (start and end), the description of the viral part, and its duration. The JSON document should follow this format: {json_template}. Please replace the placeholder values with the actual results from your analysis."
    system = f"You are a Viral Segment Identifier, an AI system that analyzes a video's transcript and predict which segments might go viral on social media platforms. You use factors such as emotional impact, humor, unexpected content, and relevance to current trends to make your predictions. You return a structured JSON document detailing the start and end times, the description, and the duration of the potential viral segments."
    messages = [
        {"role": "system", "content" : system},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        max_tokens=512,
        n=1,
        stop=None
    )
    return response.choices[0]['message']

def generate_subtitle(input_file, output_folder, results_folder):
    command = f"auto_subtitle tmp/{input_file} -o {results_folder}/{output_folder} --output_srt True --model tiny"
    print (command)
    subprocess.call(command, shell=True)

def generate_transcript(url, guid_hash):
    # command = f"auto_subtitle tmp\input_video.mp4 --srt_only True --output_srt True -o tmp\ --model tiny"
    # subprocess.call(command, shell=True)
    
    # # Read the contents of the input file
    # try:
    #     print(os.path.basename(input_file).split('.')[0] + ".srt")
    #     with open(f"D:\\Reelify\\reels-clips-automator-main\\tmp\\{os.path.basename(input_file).split('.')[0]}.srt", 'r', encoding='utf-8') as file:
    #         transcript = file.read()
    # except IOError:
    #     print("Error: Failed to read the input file.")
    #     sys.exit(1)
    # return transcript
    # Step 1: Call the first API
    import requests
    api_url = "https://yuvrajjsingh0--tawk2ai-transcription-fastapi-app.modal.run/api/transcribe"
    params = {"url": url, "guid_hash": guid_hash}
    response = requests.post(api_url, params=params)
    print(guid_hash)
    print(response)
    
    # Check if request was successful
    if response.status_code != 200:
        print("Error calling API:", response.text)
        return None
    
    # Extract call_id from response
    call_id = response.json().get("call_id")
    
    # Step 2: Call the second API to get status
    while True:
        status_url = f"https://yuvrajjsingh0--tawk2ai-transcription-fastapi-app.modal.run/api/status/{call_id}"
        status_response = requests.get(status_url)
        print(status_response)
        
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
    return episode_response.json()

def __main__():

    transcript = '''
{'segments': [{'text': ' DeeR DC battle Watch  Copy andorus  Follow Rh pitched  Like a bell  To prepare 4 weeks  renewable chocolate  Oh  Sweetness frequently ranked as one of the best, if not the best countries to live in based', 'start': 0.0, 'end': 51.914294999999996}, {'text': ' on things like overall happiness, productivity, health and overall quality of life.  Now much of this is due to things that are bigger than just the individual.  You know, we have amazing parent to leave, free education among other things, clean tap water.', 'start': 51.914294999999996, 'end': 68.254295}, {'text': " And the best pizza in the world, and yes, I have been to Italy.  With that being said, I do also realize that no place in the world is perfect, Sweden isn't perfect,  Swedes are not perfectly happy or healthy, there are plenty of problems here as well.", 'start': 68.254295, 'end': 82.43429499999999}, {'text': " But now I'm not here to talk about, you know, the macro things.  So I want to look at the individual and...  and the habits and the rituals that I personally think might contribute to some of those statistics", 'start': 82.454295, 'end': 95.15563999999999}, {'text': " because you guys are from all over the world and I want you to feel inspired by the end  of this conversation to feel like you can apply these things to your own life no matter  where you live.  But first thing I said, okay, the heart is so beautiful and I'm very happy to be here", 'start': 95.15563999999999, 'end': 110.51563999999999}, {'text': " and I'm very happy to be here and I'm very happy to be here and I'm very happy to be here  and I'm very happy to be here and I'm very happy to be here.  to jump to them. Now some background in case you are new. I'm Swedish, born here, raised here,", 'start': 110.51563999999999, 'end': 127.70189500000001}, {'text': " have lived this Stockholm for almost my entire life, lived in the US for two years. All right,  let's dive into some of the habits, rituals that I think contribute to the statistics on the individual", 'start': 127.70189500000001, 'end': 139.621895}, {'text': " level. Productivity. Sweden ranks as one of the most productive countries in the world.  As for how productivity is being defined and measured in this context, I can leave a link to  an article for you for further reading if you are interested. It's kind of a long article, one", 'start': 139.621895, 'end': 154.501895}, {'text': " that I am not personally super interested in, although I am interested in the key takeaway. So I just  used short forms AI tool to quickly summarize it. Oh, you didn't know? Yeah, you can do that. And", 'start': 154.501895, 'end': 166.021895}, {'text': " a lot more with short form are a sponsor for today's video. If you're not familiar, short form  offers, book summaries, but on steroids, because you can do a lot more than simply  up book summaries. As I mentioned, for example, you can use their AI tool to", 'start': 166.021895, 'end': 180.61110499999998}, {'text': " quickly generate high-quality summaries of articles, emails, blogs, and even  YouTube videos. Now personally, I enjoy reading, you know, entire books from  beginning to end most of the time. However, I don't really like focusing on", 'start': 180.61110499999998, 'end': 194.811105}, {'text': " taking notes while reading and or thinking too hard about, you know, what  the key points are. And so once I have finished a book, I like going to  short form to sort of get a comprehensive  overview of what I've read and that way I also remember it better. I also like", 'start': 194.811105, 'end': 212.44629}, {'text': ' doing that because within short form when you go and look up a book within the  book summary they add insight to you certain parts and this is genuinely one  of my favorite features. So for example since we are on the topic of productivity', 'start': 212.44629, 'end': 226.76629}, {'text': " I recently read Feel Good Productivity by Aliebdahl and then I went to look it up  on short form and here let's see so Abdul's final type of burnout mismatch  happens when your work does not line up with your interests and principles and", 'start': 226.76629, 'end': 241.08629}, {'text': " then short form has added a little insight to that and I'll just read the  first  I've also advised you to match what you do and what you want closely resembles the concept  of ikigai, a Japanese word that roughly translates to life's purpose.", 'start': 241.08629, 'end': 254.13466}, {'text': " I think that's really cool and this is what I mean when I say that it's more than just  a summary platform, like you're literally learning more things and being introduced  to new concepts and ideas too.", 'start': 254.13466, 'end': 264.69466}, {'text': ' And the final reason for why I really like short form that I would like to highlight  here, even though there is more and you should definitely check the mat for yourself, is  that you can simply use it for inspiration.', 'start': 264.69466, 'end': 274.93466}, {'text': " So sometimes I'll be like, hmm, I want to read a book on the topic of communication.  And so I can simply go to short form, pick the category and many of the most popular  books will pop up.  And so I may randomly pick one, start reading the summary and then I'll kind of get an idea", 'start': 274.93466, 'end': 288.09466}, {'text': " of what the book is about and if I think I will enjoy it and if I do, I'll go and buy  the book.  Now you can go to short form.com slash lana to try it out for free and to get a 20% discount  annual description. Thank you again so much to your short form.", 'start': 288.09466, 'end': 301.86852500000003}, {'text': " Motkun or Vodak's Motkun very much encouraged here in Sweden. It must come from the word motion  and it means regular physical activity to maintain your health and bodily functions.  Basically staying physically active but doesn't need to be high intensity like lifting weights at", 'start': 302.74852500000003, 'end': 319.30852500000003}, {'text': ' the gym but rather even low intensity things like walking or doing work in the garden all count  as Motkun. You guys know that I love my walks. Exploring on foot is how I make sense of things.  I want to feel the air. I want to...', 'start': 319.30852500000003, 'end': 335.388525}, {'text': " to you smell the different places. That's why when I'm writing a car, I always like opening  the window because I'm like, what does this place smell like? So I'll always walk if I can,  unless, unless it's too humid outside because by the time that I get to my destination,", 'start': 335.05036, 'end': 350.09036000000003}, {'text': " my hair is going to be an absolute mess. And if my hair is a mess, I will be in a bad mood.  And I would rather have good hair. And speaking of walking, this is one of the things that I,  it was a bit of a colder shock when I lived in LA in the US because there weren't nearly as many", 'start': 350.65036000000003, 'end': 368.57036}, {'text': " people on the streets as there were people in cars, not even in popular places like  per day drive or even Beverly Hills.  I mean that isn't Beverly Hills, but you know what I mean. I come to think of this one instance that", 'start': 368.57036, 'end': 381.36948499999994}, {'text': " Truly shocked me. So let me share a little story. So I was living near campus at UCLA  And I wanted to get to Beverly Hills. And so I thought okay, I'll just walk there  I think it was like an hour and 45 minutes to walk or something like that on one hand that walk was lovely", 'start': 381.92948499999994, 'end': 396.009485}, {'text': ' You know, obviously you have the amazing and lay weather the beautiful palm trees on the other hand  I barely saw any other people on that entire walk the streets were so empty  There were tons of cars, but no people and I even remember feeling', 'start': 396.08948499999997, 'end': 409.28948499999996}, {'text': " Strange being the only one walking on the streets everyone in cars  I was like are people looking at me thinking that I'm lost or that I'm a weirdo?  Anyway, let's not make this conversation about LA versus Stockholm", 'start': 409.92948499999994, 'end': 421.04948499999995}, {'text': " I think the point here is just that if your city allows it if you can  walk more get all the matoom that you can get  logum  the Swedish concept of  Logum roughly translates to you not a little not too much. Just right. There's actually a couple books on this concept", 'start': 421.209485, 'end': 440.72948499999995}, {'text': " One is called logum. It's written by  at dun. I read it recently and it was quite fun. I cannot tell you how often I will speak to  an English speaking person and they'll ask me a question or say something and I'm trying to find", 'start': 440.96948499999996, 'end': 455.249065}, {'text': " the word to describe logon in English because I want to say not too little, not too much, but who  says that? No one really uses that phrase in English and that's where logon is the perfect word.  Like when someone asks how much multi-wannier coffee you say logon when someone says,", 'start': 455.249065, 'end': 472.529065}, {'text': " oh how far is the walk to that restaurant? And you're like it's just logon, like it's not too far,  it's not super close either. Or someone says how much cheese you want on your pasta, you want to  say logon. I want a satisfactory amount, not too little, not too much. And I think it's a cozy", 'start': 472.529065, 'end': 487.809065}, {'text': " word to you. Like being logon tired is nice, you know? Like you're a little bit tired,  you're starting to feel your body kind of getting a bit heavy. You're also not too tired, you can  still watch a movie and eat a snack and get cozy. And I think anyone can embrace logon to have a", 'start': 487.809065, 'end': 507.489065}, {'text': ' little bit more logon in your life, whether that is in your home or...  or how much you choose to socialize,  or how much you work, how much you go out,  how healthy you eat, anything that is log on  is just the perfect amount.', 'start': 507.489065, 'end': 524.250535}, {'text': " Fili kiao.  Did you know that sweets are in the top three  of the biggest coffee consumers in the world?  Personally, I am not at all a genuine coffee drinker.  I'll have about one espresso shot  and the rest has to be milk.", 'start': 524.250535, 'end': 540.4505350000001}, {'text': " That's besides the point, Fili kiao is basically when you...  take a break from doing by having a small bite, usually something sweet like a  piece of cake and a coffee. Now you might listen to this and think, okay so", 'start': 540.4505350000001, 'end': 553.188695}, {'text': " ficca basically means a coffee break. Yeah, but no, it's more than a coffee  break. It's not even about the coffee really. It's about taking a moment or an  hour or longer to pause, to relax, to connect with yourself, your loved ones,", 'start': 553.188695, 'end': 571.848695}, {'text': " with a colleague or a book. Ficca is oftentimes how we socialize here. It is  perfectly acceptable to ask someone out on some ficca or to meet up a friend  over some ficca that you haven't seen in a long time or even taking a ficca", 'start': 571.848695, 'end': 588.2686950000001}, {'text': " pause at work. Ficca is a love language, all sweets and  It's about unplugging, disconnecting, being present, and coffee.  I mean, it's about the coffee, too.  We don't wear shoes inside.  Can someone strain this out for me?", 'start': 588.2686950000001, 'end': 605.80197}, {'text': " Do Americans wear shoes to bed?  And if they don't, why do they wear shoes to bed in all the movies and commercials and  such?  Please, if you're an American, help us all understand.  Nixon, the art of doing nothing.", 'start': 605.80197, 'end': 622.60197}, {'text': " I actually recently learned that there is a Danish concept or word niksen.  It is the Dutch lifestyle concept of doing nothing.  Now here's what this article said that I found.  Practicing niksen could be a simple ask just hanging around, looking at your surroundings", 'start': 622.65974, 'end': 639.81974}, {'text': " or listening to music.  As long as it's without purpose and not done in order to achieve something or to be productive.  Think simply sitting in a chair or looking out the window, whereas mindfulness is about", 'start': 639.81974, 'end': 650.93974}, {'text': ' being present in the moment, niksen is more about carving out time to just be.  Even letting your mind wander off rather than focusing on the details of an action.  I love this. This is one of my new favorite words. It feels very', 'start': 650.93974, 'end': 664.192715}, {'text': " Scandy and I think we can all use a bit more Nixon in our lives  Traditions when I think of Sweden  I think of a place where people want to find the reasons to celebrate life and they do  There's a lot of traditions a lot of holidays. We have mid-summer", 'start': 664.692715, 'end': 681.852715}, {'text': ' We have all-bory and a ton of other little holidays  And then we have all the days where we celebrate  Different foods and pastries like the day of the cinnamon bun, which is when people  Will meet up with a friend or someone and stand in long lines to all the cafes to get a cinnamon bun', 'start': 682.0127150000001, 'end': 703.172715}, {'text': " And where most workplaces offer their employees cinnamon buns  Similarly, we have the day of the samla and we have  crefte viva, which is I think crayfish in English, which is when you throw a  party or attend a party once a year and just eat crayfish. And there's a long", 'start': 703.172715, 'end': 722.203275}, {'text': ' list of celebrations that take place each year here in Sweden and I love that.  I think traditions create togetherness and I think no matter where you are in  the world you can absolutely find reasons to celebrate life and I think', 'start': 722.203275, 'end': 738.8032749999999}, {'text': ' Swedes prove that it can be something small, simple, even, seemingly silly, like  celebrating cinema months.', 'start': 738.8032749999999, 'end': 750.0032749999999}]}
    '''
    #generate_viral_gemini(transcript)
    #return

    # Check command line argument    
    parser = argparse.ArgumentParser(description='Create 3 reels or tiktoks from Youtube video')
    parser.add_argument('-v', '--video_id', required=False, help='Youtube video id. Ex: Cuptv7-A4p0 in https://www.youtube.com/watch?v=Cuptv7-A4p0')
    parser.add_argument('-f', '--file', required=False, help='Video file to be used')
    args = parser.parse_args()
    
    if not args.video_id and not args.file: 
        print('Needed at least one argument. <command> --help for help')
        sys.exit(1)
    
    if args.video_id and args.file:
        print('use --video_id or --file')
        sys.exit(1)

    # Create temp folder
    # try: 
    #     if os.path.exists("tmp"):
    #         shutil.rmtree("tmp")
    #     os.mkdir('tmp') 
    # except OSError as error: 
    #     print(error)

    filename = 'input_video.mp4'
    if args.video_id:
        video_id=args.video_id
        url = 'https://www.youtube.com/watch?v='+video_id  # Replace with your video's URL
        # Download video
        # download_video(url,filename)
    
    if args.file:
        video_id = os.path.basename(args.file).split('.')[0]
        print(video_id)
        if (path.exists(args.file) == True):
            command = f"copy {args.file} tmp\input_video.mp4"
            subprocess.call(command, shell=True)
        else:
            print(f"File {args.file} does not exist")
            sys.exit(1)

    output_folder = 'results'
    
    # Create outputs folder
    video_id = str(time.time()) + ""
    try: 
        os.mkdir(f"{output_folder}") 
    except OSError as error: 
        print(error)
    try: 
        os.mkdir(f"{output_folder}/{video_id}") 
    except OSError as error: 
        print(error)

    # Verifies if output_file exists, or create it. If exists, it doesn't call OpenAI APIs
    video_id = "1713996500.510655"
    output_file = f"{output_folder}/{video_id}/content.txt"
    if (path.exists(output_file) == False):
        # generate transcriptions
        guid_hash = video_id
        #transcript = generate_transcript(generate_download_signed_url_v4(filename), guid_hash)
        #print (transcript)
        
        viral_segments = generate_viral_gemini(transcript)
        #content = viral_segments["content"]
        content = viral_segments
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(content)
        except IOError:
            print("Error: Failed to write the output file.")
            sys.exit(1)
        print("Full transcription written to ", output_file)
    else:
        # Read the contents of the input file
        try:
            with open(output_file, 'r', encoding='utf-8') as file:
                content = file.read()
        except IOError:
            print("Error: Failed to read the input file.")
            sys.exit(1)

    parsed_content = json.loads(content)
    generate_segments(parsed_content['segments'])
    # import autocrop
    # Loop through each segment
    for i, segment in enumerate(parsed_content['segments']):  # Replace xx with the actual number of segments
        if i == 0:
            continue
        input_file = f'tmp/output{str(i).zfill(3)}.mp4'
        output_file = f'tmp/output_cropped{str(i).zfill(3)}.mp4'
        generate_short(input_file, output_file)
        # faces = autocrop.detect_faces(input_file)
        # autocrop.crop_video(faces, input_file, output_file)
        generate_subtitle(f"final-{output_file}", video_id, output_folder)

__main__()
