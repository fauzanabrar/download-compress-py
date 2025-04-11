# Streamlit Google Drive App

This project is a Streamlit web application that allows users to upload files to Google Drive and optionally compress video files before uploading. The application provides a user-friendly interface for entering a download link, selecting files, and managing uploads.

## Project Structure

```
streamlit-google-drive-app
├── src
│   ├── app.py                # Main entry point of the Streamlit application
│   ├── utils
│   │   ├── drive_utils.py    # Utility functions for Google Drive operations
│   │   └── compression_utils.py # Functions for compressing video files
├── requirements.txt          # List of dependencies for the project
├── README.md                 # Documentation for the project
└── .streamlit
    └── config.toml          # Configuration file for Streamlit
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd streamlit-google-drive-app
   ```

2. **Install dependencies:**
   It is recommended to create a virtual environment before installing the dependencies.
   ```bash
   pip install -r requirements.txt
   ```

3. **Obtain Google Drive API credentials:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and enable the Google Drive API.
   - Create credentials (OAuth 2.0 Client IDs) and download the `credentials.json` file.
   - Place the `credentials.json` file in the project root directory.

4. **Run the Streamlit application:**
   ```bash
   streamlit run src/app.py
   ```

## Usage Guidelines

- Enter the download link for the file you wish to upload.
- Select whether you want to compress the file before uploading.
- Click the "Upload to Google Drive" button to upload the file.
- Ensure that you have the `token.json` file for authentication. If you do not have it, the application will guide you through the authentication process.

## Additional Information

- The application uses the `ffmpeg` library for video compression. Make sure it is installed on your system.
- For any issues or feature requests, please open an issue in the repository.