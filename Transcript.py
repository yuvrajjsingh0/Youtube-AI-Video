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
'''
{'segments': [{'text': ' How do you know if you have low self-confidence? You might find that you avoid doing things out of  fear of failing, not performing well, like changing jobs, doing a presentation, trying a new sport,', 'start': 0.0, 'end': 10.16}, {'text': ' or speaking up about something that you feel. You may not really try new things at all because  unfamiliar situations might bring you a lot of fear and anxiety more so than excitement and  curiosity. You die your own ability to do well, to succeed, to be accomplished, to be good, to be', 'start': 10.16, 'end': 25.04}, {'text': ' beautiful, to be desired, or at least to be perceived as so. You may struggle with trusting  yourself, trusting your judgment, perhaps...  you find yourself always looking to others for answers rather than looking inward because', 'start': 25.04, 'end': 36.528385}, {'text': " you just don't believe that you're capable of making good decisions for yourself.  And it's not that you believe that you don't deserve good things, that would be you having  low self-esteem which is different although often correlated.", 'start': 36.528385, 'end': 48.808385}, {'text': " Now confidence isn't usually a across the board thing, we all feel confident in some  areas and less than others and I don't think that's necessarily a bad thing.  You know I sure would not want a bus driver to feel confident about landing a plane or", 'start': 48.808385, 'end': 63.308385}, {'text': " an accountant to feel confident about.  performing surgery. Sometimes there's actually a very good reason to believe  that we wouldn't succeed at something, but with low self-confidence there's  usually not. You just have self-limiting beliefs about yourself, beliefs that aren't", 'start': 63.308385, 'end': 78.567805}, {'text': " really based on much truth, if any truth at all. And so you hide in this world  feeling inferior, afraid to take up space, and you know this, you know that  something is holding you back from fully blooming. Let's do a little quick test", 'start': 78.567805, 'end': 93.807805}, {'text': " to see where you believe that you land on the confidence scale. Don't take this  too seriously, don't overthink it, it's more so for fun, but it could potentially  also be used as some food for thought data for yourself. Now ask yourself, when", 'start': 93.807805, 'end': 110.007805}, {'text': " I'm faced with something unfamiliar or and challenging, does my attitude tend to  be I will not be able to figure this out or is it usually sure I can figure this  out. So let's say for example that I were to ask you, hey, can you help me", 'start': 110.007805, 'end': 128.527805}, {'text': " film something for a video and you have absolutely no camera experience, what do  you think you would think? Let me give you three options. One, do you immediately  decide for yourself that you will probably do a crappy job that you can't?", 'start': 128.527805, 'end': 145.247805}, {'text': " Well that might indicate that you have a low confidence. Two, do you think I'm about  to feel the best effing sequence she's ever seen in her life? Well that might be  you being a bit overconfident. Or three, do you think something like, okay, this is", 'start': 145.247805, 'end': 164.36780499999998}, {'text': " something new, but let's see how I can figure it out. I personally believe that  this would be a healthy level of confidence. Comment down below please what  you got, I'm so curious. Now before we get into the deep stuff, we've all heard", 'start': 164.36780499999998, 'end': 179.847805}, {'text': " about, you know, the typical become more confident, things like fix your posture,  take care of your skin, dress better and they're all true. Especially for me, the  dress better part. The way that I dress can absolutely take me from feeling down", 'start': 179.847805, 'end': 197.30780500000003}, {'text': " here to up here. So let me actually show you some looks that make me feel up here  as opposed to down here.  I'm so happy that Vivaya wanted to sponsor this portion of the video, as they provide,  in my opinion, some of the most comfortable shoes that I've ever worn.", 'start': 197.30780500000003, 'end': 213.71116}, {'text': ' All their products are made by using recycled materials.  Each pair of shoes is made using six plastic bottles that come from city waste and the  ocean.  Their products have been worn by people like Selena Gomez, Katie Holmes, and Emma Roberts.', 'start': 213.71116, 'end': 225.79116000000002}, {'text': " Here I am wearing the Melody Pro.  Look, I'm not a heel girl anymore.  She retired years ago, but these are the perfect height for me and I can walk in them for hours  without my feet hurting.  They are timeless and sophisticated and go with a variety of outfits.", 'start': 225.79116000000002, 'end': 240.39116}, {'text': " This look here is something that I would...  wear to lick a brunch or dinner.  As it's getting colder,  I would probably add some stockings.  For the second look, I'm wearing the market mary Jane.  I've definitely worn these the most,", 'start': 240.39116, 'end': 253.09111499999997}, {'text': ' again, super comfortable,  and they work to dress up or down.  This is something that I would wear for casual day out,  like running errands or meeting up a friend,  or if I worked in an office,  I would definitely wear this to work.', 'start': 253.09111499999997, 'end': 265.851115}, {'text': " For this final look, I'm wearing the market too,  another versatile shoe.  I think this look works for a more casual day,  as well as a nice,  sort of like, lunch or dinner or, perhaps...  even date. I also decided to get their Wallace bag. I'm definitely a small bag", 'start': 265.851115, 'end': 281.935885}, {'text': " person really but they just don't work with my lifestyle. It's not realistic. I  always carry so much with me so this size is perfect. As for the sizing of the  shoes I got my normal size and I have pretty narrow feet. But hey if you do", 'start': 281.935885, 'end': 297.175885}, {'text': ' end up getting a shoe that does not fit you, Vivaya offers a 30-day return  exchange policy worldwide. Now if you want to check out Vivaya you can now get  15% off your purchase using the code LON of 15. Thank you again to Vivaya.', 'start': 297.175885, 'end': 314.715885}, {'text': ' Confidence? It seems so easy for others. Why not for me? You might have thought to yourself  at some point.  Now it does in fact seem like it is easier for some than for others. But why? Is it nature?', 'start': 313.425645, 'end': 329.06564499999996}, {'text': " Nurture? Are some people destined to lack confidence? Or is it a skill that anyone can  acquire? There seems to be some disagreement actually amongst researchers. Obviously no  one wants to believe that they're destined to lack confidence and although some have", 'start': 329.06564499999996, 'end': 344.405645}, {'text': " claimed that genetics play quite a big role, most researchers seem to have found that it's  probably a mix of things. Some believe that it is in fact a skill. But one factor that  seems to be widely agreed upon is that childhood and how we grow up does seem to play a role", 'start': 344.405645, 'end': 361.24564499999997}, {'text': " in how our confidence develops as we grow up. Some things that could lead to a child  grow up with low self-confidence is things like having a wetful parents, abuse, parents  being supportive, making your child believe that they're not good enough, being overly", 'start': 361.24564499999997, 'end': 376.605645}, {'text': ' critical or undermining of the child, making them believe that they are not capable, not  being accepting a failure, having parents with unrealistic.  expectations growing up in a highly competitive environment where there was a lot of comparison.', 'start': 376.605645, 'end': 392.95182}, {'text': ' Other than our parents or whatever family structure we grew up with, our peers also play a role.  Things like being bullied or rejected by people in school or feeling like you did not get the  support needed from teachers might lead to lower levels of confidence. Some other things that might', 'start': 392.95182, 'end': 411.99181999999996}, {'text': " affect our confidence are things like social expectations and society standards, whether we're  talking accomplishments, beauty, money, body image, career, you know, the whole social media topic  and how it's caused this new generation with serious self-confidence and self-esteem issues", 'start': 412.07182, 'end': 431.51182}, {'text': " is a monster on its own if you want a separate video on that topic.  Let me know.  Now what do you do about it?  Okay, we get it.  We've established that there is some confidence work  that can be done.", 'start': 431.51182, 'end': 442.275755}, {'text': " How do you go about it?  You might ask.  Of course there's not one answer.  You know, that's going to work for everyone.  We've all been through different things.  We're all dealing with different things", 'start': 442.275755, 'end': 452.675755}, {'text': " and might need help and guidance in different ways.  What works for me, we not work for you,  we not work for him, we not work for her.  But to summarize most of the research  that I've read, confidence is built by doing", 'start': 452.675755, 'end': 468.515755}, {'text': " through active action, by learning through experience,  by putting yourself in situations  that are challenging, get realistic,  situations that put you out of your comfort zone.  You're open and curious about new situations and time.", 'start': 468.515755, 'end': 483.795755}, {'text': " tasks, you challenge that ghost in your head that default setting that says, no, I can't,  you know, like a damn bot. It could be things like, I'm going to finish reading this book  to prove to myself that I can finish reading a book, let it be a very small book, or I'm", 'start': 483.63422, 'end': 500.39422}, {'text': " going to run a marathon, you know, let it be the shortest marathon that you can find  in the country. If that is what is realistic, yet challenging enough for you, or I'm going  to ask this person out on a date, well, maybe you are already struggling socially, so maybe", 'start': 500.39422, 'end': 518.35422}, {'text': " start small by seeing.  high to a stranger or calling up a friend. And then the more you do something and the better you become at it, the more confident you'll become.  You know, there's the well-known confidence, competence loop that illustrates basically that the more competent we become, the more confident we become,", 'start': 518.35422, 'end': 537.0674}, {'text': ' because as we become more skilled our fears shrink while our confidence  grows. And that is the confidence, competence loop. And the way to overcome that initial fear is by taking action.  that very first step. But what are some things that can help us take that action', 'start': 537.0674, 'end': 558.531705}, {'text': " since action seems to be the answer? One way is to feel the fear and do it anyway.  Another way that I have found is to sort of curate or build your life in a way so  that failure isn't that big of a deal. So as an example, when I quit my corporate", 'start': 558.531705, 'end': 576.191705}, {'text': " job to pursue YouTube, sure it was a big deal in that I had to resign and  fully commit to this  you know, different lifestyle and whatnot, but other than that, it wasn't that scary.  You know, I had a place to live, I had some money saved up, I had a pretty okay resume,", 'start': 576.191705, 'end': 592.6119749999999}, {'text': ' and I had my university degrees to fall back on, I had a safety net, which is just another word  for options. I had very little competence, I think I had, you know, a few videos that I reached a few  thousand views, so there was some hope, but I guess I was super eager so that that glimmer of hope', 'start': 592.6119749999999, 'end': 612.691975}, {'text': " was enough, was all the confidence, I guess, that I needed. But also when you think about it,  you know, going to school and getting educated and all those things, we're also me taking action.  to create that safety net. And also I had supported people around me. Now,", 'start': 612.7719749999999, 'end': 629.48395}, {'text': ' to be clear, no one was raving at this point. They absolutely had their doubts,  but they gave me enough space to prove to them that I could. And that was all the  support that I could honestly ask for at that point. And I know not everyone has', 'start': 629.48395, 'end': 645.06395}, {'text': " that. And now here's where I would like to share with you this article that I  read and I will link it below where the writer centrally introduces a  different way of looking at the confidence competence loop. He calls it the", 'start': 645.06395, 'end': 657.20395}, {'text': ' connection  He says that there is a difference between task success and relationship success.  And gives the example of, will I win this game that is a task success question?  Will you still be here if I lose this relationship success question?', 'start': 657.20395, 'end': 676.950835}, {'text': " Basically sometimes it's not the lack of confidence that holds us back in life.  It is the genuine fear of losing, for example, an important relationship.  So let's say that your mom is.  being or saying she's going to be very disappointed in you if you decide to not pursue your", 'start': 676.950835, 'end': 693.67615}, {'text': " masters and become a photographer instead or something like that.  So you might actually feel quite confident in your ability to become a well-paid photographer,  but you're fearful of the risk of damaging your relationship with your mom, so essentially", 'start': 693.67615, 'end': 709.69615}, {'text': " that is what's holding your back, not the confidence.  And so he encourages us to, instead of encouraging others by saying, hey, you got this, to instead  say I got you, to let people know that even if they don't succeed, you will still be there.", 'start': 709.69615, 'end': 727.29615}, {'text': " He writes through confidence is the freedom to fail and the expectation that our relationships  won't be damaged when we do.  So I think the takeaway from that is...  Who do you surround yourself with? Do you have an unconditional supporter as he calls it in your life?", 'start': 727.29615, 'end': 741.49839}, {'id': 1, 'seek': 0, 'start': 741.49839, 'end': 746.13839, 'text': " And are you an unconditional supporter in someone else's life?", 'tokens': [50695, 843, 389, 345, 281, 42423, 15525, 287, 2130, 2073, 338, 1204, 30, 50927], 'temperature': 0.0, 'avg_logprob': -0.22177297190616005, 'compression_ratio': 1.4864864864864864, 'no_speech_prob': 0.02104981057345867}]}
        '''

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