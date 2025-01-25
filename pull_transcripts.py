import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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

            video_data.append({"title": title, "link": link})
        except Exception as e:
            print(f"Error extracting video data: {e}")

    driver.quit()

    return video_data

def fetch_transcript(video_data):
    transcripts = []
    for video in video_data:
        video_id = video['link'].split("v=")[-1]
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            # drop start and duration keys from transcript and join text
            text_transcript = " ".join([line['text'] for line in transcript]).replace("\n", " ")
            transcripts.append({"video_title": video['title'], "transcript": text_transcript})
        except TranscriptsDisabled as e:
            transcripts.append({"video_title": video['title'], "transcript": None})
            print(f"Transcripts are disabled for {video['title']}")
        except NoTranscriptFound as e:
            transcripts.append({"video_title": video['title'], "transcript": None})
            print(f"No transcript found for {video['title']}")
        except Exception as e:
            transcripts.append({"video_title": video['title'], "transcript": None})
            print(f"Error fetching transcript: {e}")

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
        transcripts = fetch_transcript(video_data)
        
        print(f'Saving corpus for {youtuber_name}')
        save_corpus(youtuber_name, transcripts)