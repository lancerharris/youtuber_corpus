import time
import json
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_links_and_titles(channel_url):
    driver = webdriver.Chrome()
    driver.get(channel_url)

    # wait for the page to load
    time.sleep(3)

    bottom_of_page = False
    while not bottom_of_page:
        # scroll to the bottom of the page to load more videos
        scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {scroll_height})")
        # wait for the next batch of videos to load
        time.sleep(2)
        new_scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_scroll_height == scroll_height:
            bottom_of_page = True

    video_elements = driver.find_elements(By.CSS_SELECTOR, 'ytd-rich-item-renderer.style-scope.ytd-rich-grid-renderer')
    video_data = []

    for video in video_elements:
        try:
            title = video.find_element(By.CSS_SELECTOR, 'yt-formatted-string#video-title').text
            link = video.find_element(By.CSS_SELECTOR, 'a#video-title-link').get_attribute('href')

            video_data.append({"video_title": title, "link": link})
        except Exception as e:
            print(f"Error extracting video data: {e}")

    driver.quit()

    return video_data

def fetch_transcript(video_data, retries=3):
    video_data_length = len(video_data)

    transcripts = []

    for i, video in enumerate(video_data):

        video_id = video['link'].split("v=")[-1]

        transcript_found = False
        loop_retries = retries
        while (not transcript_found) and loop_retries > 0:
            if loop_retries == retries:
                print(f"Fetching transcript for video {i} of {video_data_length}; {video['video_title']}, link {video['link']}")
            elif loop_retries < retries:
                # delay between requests to avoid getting blocked
                # increase the delay with each retry
                time.sleep(random.uniform(1 + (retries - loop_retries) // 2, 3 + retries - loop_retries))
                print(f"   Retries left: {loop_retries}; Uniform sleep between {1 + (retries - loop_retries) // 2} and {3 + retries - loop_retries} seconds")

            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                # drop start and duration keys from transcript and join text
                text_transcript = " ".join([line['text'] for line in transcript]).replace("\n", " ")
                transcripts.append({"video_title": video['video_title'], "transcript": text_transcript})
                transcript_found = True
            except Exception as e:
                # append None for transcript on last retry
                if loop_retries == 1:
                    transcripts.append({"video_title": video['video_title'], "transcript": None})
                loop_retries -= 1
                print(f"Error fetching transcript")

    return transcripts

def save_corpus(youtuber_name, transcripts):
    filename = f"./Corpus/{youtuber_name}_corpus.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(transcripts, file, ensure_ascii=False, indent=2)
    print(f"Corpus saved to {filename}")

if __name__ == "__main__":
    youtuber_names = ["<youtuber_name1>", "<youtuber_name2>", "<youtuber_name3>"]
    # distinct youtuber names
    youtuber_names = list(set(youtuber_names))
    
    for youtuber_name in youtuber_names:
        channel_url = f"https://www.youtube.com/{youtuber_name}/videos"
        
        video_data = get_video_links_and_titles(channel_url)
        
        print(f"Fetching transcripts for {youtuber_name} from {len(video_data)} videos")
        transcripts = fetch_transcript(video_data, retries=7)
        
        save_corpus(youtuber_name, transcripts)