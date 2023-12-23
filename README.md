# Download and Compress Video Python Script
This script is to download and compress video files from a given URL. 
The script will download the video file from the given URL and compress it to a given size. 
The script will also create a log file to keep track of the download and compression process.

This script use the following libraries:
- [FFmpeg](https://ffmpeg.org/)
- [YouTube-dl](https://ytdl-org.github.io/youtube-dl/)
- [Google Auth Python Client]()
- [Google Drive Python Client]()

## Installation
Get auth credentials for Google Drive API and YouTube API. 
Follow the instructions [here](https://developers.google.com/drive/api/v3/quickstart/python) to get the credentials. 
Save the credentials as `credentials.json` and add to the project root. 
Then setup and run the main.ipynb notebook to install the required libraries.