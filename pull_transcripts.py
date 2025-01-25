import time

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

            video_data.append({"title": title, "link": link})
        except Exception as e:
            print(f"Error extracting video data: {e}")

    driver.quit()

    return video_data

if __name__ == "__main__":
    youtuber_name = "<youtuber_name>"
    channel_url = f"https://www.youtube.com/{youtuber_name}/videos"
    video_data = get_video_links_and_titles(channel_url)

    for video in video_data:
       print(f"Title: {video['title']}, Link: {video['link']}")