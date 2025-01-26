# youtuber_corpus
Create a document of transcripts of a youtubers videos

### Using the Project
Enter multiple youtuber handles in the pull_transcripts file to get the transcripts of all videos that have transcripts available.

Transcripts are saved to the Corpus directory for future use. Possibly for ingestion into AI. Could be good to get your favorite tips and techniques for a topic you are interested in.

Requires chrome webdriver to be installed for use with Selenium

### Missing transcripts
some videos will legitimately not have transcripts, others will and still fail. Some of this may be due to youtube_transcript_api failing for some reason. But I believe there may be some sort of throttling that is happening too. So I've added some random delays and retry attempts for getting the transcripts.

Something that could be tried is extending the script to go through the resulting json files and try to pull the transcripts where the transcript key is null. But the current script doesn't save the link to the videos, but that would be easy to change.