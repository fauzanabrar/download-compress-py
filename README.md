# Download and Compress Video Python Script
This script is to download and compress video files from a given URL. 
The script will download the video file from the given URL and compress it to a given size. 
The script will also create a log file to keep track of the download and compression process.

This script use the following libraries:
- [FFmpeg](https://ffmpeg.org/)
- [YouTube-dl](https://ytdl-org.github.io/youtube-dl/)
- [Google Auth Python Client]()
- [Google Drive Python Client]()

## Features
- Download video from a given URL
- Compress video to a given size
- Upload the compressed video to Google Drive
- Create a log file to keep track of the download and compression process
- Download and merge all stream video in format .u3m8

## Installation
Get auth credentials for Google Drive API and YouTube API. You can use either OAuth 2.0 or Service Account.

### With OAuth 2.0
Follow the instructions [here](https://developers.google.com/drive/api/v3/quickstart/python) to get the credentials.
Save the credentials as `credentials.json` and add to the project root.

### With Service Account
if use service account, follow the instructions [here](https://developers.google.com/identity/protocols/oauth2/service-account#python) to get the credentials.
save the service account credentials as `service_account.json` and add to the project root.

### Usage
Choose one folder in the drive to save the compressed video files. Make sure the folder is public.
Then setup and run the main.ipynb notebook to install the required libraries.

#### For download stream
Need .u3m8 playlist url and run the download_stream.ipynb notebook to download and merge all the stream video.