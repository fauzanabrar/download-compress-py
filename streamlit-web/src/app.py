from dotenv import load_dotenv
import streamlit as st
import os
from utils.drive_utils import (
    authenticate_drive,
    get_lists_of_folders,
    upload_large_file_to_drive,
    get_drive_quota,
    delete_all_drive_files,
)

from mycomponent import mycomponent
from components.download_button_api import download_button_api

from utils.compression_utils import compress_video
from utils.file_utils import download_file, delete_file


load_dotenv()


def download_video_UI():
    st.title("Video Upload to Google Drive")

    # Request download link
    download_link = st.text_input("Enter the download link for the video:")
    if st.button("Download file"):
        if download_link:

            progress_bar = st.progress(0)

            download_file(download_link, progress_bar=progress_bar)
            refresh_file_list()
            st.success(f"File downloaded from {download_link}!")
        else:
            st.error("Please enter a valid download link.")


def compress_video_UI(download_file_path, host_api):
    st.divider()
    st.subheader("Compress Video")

    if st.button("Refresh File List", key="refresh_file_list"):
        refresh_file_list()
        st.success("File list refreshed successfully!")

    # Compress selected file
    list_all_files = st.session_state.list_all_files
    selected_file = st.selectbox("Select a file to compress:", list_all_files)

    # Select video quality
    resolution = st.selectbox(
        "Select video quality:",
        ["240p", "360p", "480p", "720p", "1080p"],
        index=2,
    )

    file_path = f"{download_file_path}/{selected_file}"

    compress_progress_bar = st.empty()

    col1, col2, col3 = st.columns([0.35, 1, 0.25])

    with col1:
        st.button(
            "Compress Video",
            on_click=compress_file,
            args=(selected_file, resolution),
            key="compress_video",
        )

    with col2:
        download_button_api(my_input_value=f"{host_api}/download/{selected_file}")

    with col3:
        st.button(
            "Delete File",
            on_click=deleted,
            args=(file_path, selected_file),
            key="delete_file",
        )

    if st.session_state.get("file_alert", False):
        st.success(st.session_state.get("alert_message"))
        update_state("file_alert", False)


def google_drive_authentication_UI(token_file_path):
    st.divider()
    st.subheader("Authenticate to Google Drive")

    token_file_input = st.file_uploader(
        "Upload token.json or credentials.json", type=["json"]
    )

    col1, col2 = st.columns([0.7, 0.25])

    with col1:
        if st.button("Upload Token File"):
            if token_file_input is not None:
                # Save the uploaded token file temporarily
                with open(token_file_path, "wb") as f:
                    f.write(token_file_input.getbuffer())

                token_file_content = check_token_file_content()

                st.success("Token file uploaded successfully!")
            else:
                st.error("Please upload a valid token file.")

    # Show the content of the uploaded token file
    with col2:
        if st.button("Show/Hide Token File"):
            update_state("show_token_content", not st.session_state.show_token_content)

    if st.session_state.get("show_token_content", False):
        token_file_content = check_token_file_content()
        if token_file_content is not None:
            st.text_area("Token File Content", token_file_content, height=200)
        else:
            st.error("No token file uploaded.")

    # Authenticate Google Drive
    if st.button("Authenticate Google Drive"):
        token_file_content = check_token_file_content()
        if token_file_path is not None and token_file_content is not None:
            service = authenticate_drive(
                token_file_path, token_file_path, is_service_account=True
            )
            if service:
                service = update_state("service", service)

                st.success("Google Drive authenticated successfully!")
            else:
                st.error("Failed to authenticate Google Drive.")
        else:
            st.error("Please upload a valid token file.")


def upload_google_drive_UI(root_folder_id, download_file_path):
    st.divider()
    st.subheader("Upload to Google Drive")

    col1, col2 = st.columns([0.25, 1])

    # Choose file to upload from the downloaded file folder
    with col1:
        if st.button("Refresh File List", key="refresh_file_list_2"):
            refresh_button()

    with col2:
        if st.button("Get Google Drive Quota"):
            service = st.session_state.service
            if service:
                quota = get_drive_quota(service)
                if quota:
                    # format the response to human readable limit, usage, usageInDrive, and usageInDriveTrash
                    limit = f"{int(quota.get('limit')) / (1024 ** 3):.2f} GB"
                    usage = f"{int(quota.get('usage')) / (1024 ** 3):.2f} GB"
                    usage_in_drive = (
                        f"{int(quota.get('usageInDrive')) / (1024 ** 3):.2f} GB"
                    )
                    usage_in_drive_trash = (
                        f"{int(quota.get('usageInDriveTrash')) / (1024 ** 3):.2f} GB"
                    )

                    st.success(
                        f"Google Drive Quota:\n- Limit: {limit}\n- Usage: {usage}\n- Usage in Drive: {usage_in_drive}\n- Usage in Drive Trash: {usage_in_drive_trash}"
                    )

                    if (
                        int(quota.get("usageInDriveTrash")) > 0
                        or int(quota.get("usageInDrive")) > 0
                    ):
                        st.session_state.show_delete_all_files_button = True

                else:
                    st.error("Failed to retrieve Google Drive quota.")
            else:
                st.error(
                    "Google Drive service not authenticated. Please authenticate first."
                )

        if st.session_state.get("show_delete_all_files_button"):
            delete_all_files_button = st.button(
                "Delete All Files", key="delete_all_files_button"
            )

            if delete_all_files_button:
                with st.spinner("Deleting files..."):
                    service = st.session_state.service
                    deleted_count, error = delete_all_drive_files(
                        service, dry_run=False
                    )

                    if deleted_count > 0:
                        st.toast(f"Deleted {deleted_count} files from Google Drive.")
                    else:
                        st.error(
                            f"Failed to delete files from Google Drive. Errors: {error}"
                        )

                # Hide the button after it is clicked
                update_state("show_delete_all_files_button", False)

    if st.session_state.get("show_list_alert", False):
        st.success(st.session_state.get("alert_message"))
        update_state("show_list_alert", False)
        update_state("show_delete_all_files_button", False)

    list_all_files = st.session_state.list_all_files
    selected_file = st.selectbox("Select a video file to upload:", list_all_files)

    # add folder id or select folder
    folder_id_input = st.text_input("Enter the Google Drive folder ID (optional):")
    folder_id_input = sanitize_input(folder_id_input)

    # Get list of folders in Google Drive
    service = st.session_state.service
    if service:
        folders = get_lists_of_folders(service, root_folder_id)

        folder_names = [folder["name"] for folder in folders]
        folder_ids = [folder["id"] for folder in folders]

        selected_folder = st.selectbox(
            "Select a folder to upload the file:", folder_names
        )

        if selected_folder:
            folder_id = folder_ids[folder_names.index(selected_folder)]
            folder_id = sanitize_input(folder_id)
        else:
            folder_id = None
    else:
        st.error("Google Drive service not authenticated. Please authenticate first.")

    if st.button("Upload File"):
        if selected_file:
            file_path = f"{download_file_path}/{selected_file}"
            file_name = selected_file

            # Upload the file to Google Drive
            service = st.session_state.service

            if service:
                if folder_id_input:
                    folder_id = folder_id_input.strip()

                progress_bar = st.progress(0)

                file_id = upload_large_file_to_drive(
                    service,
                    file_path,
                    file_name,
                    folder_id,
                    progress_bar,
                )

                if file_id:
                    file_link = f"https://drive.google.com/file/d/{file_id}/view"
                    st.success(
                        f"File {selected_file} uploaded to Google Drive with ID: {file_id}.\n\n"
                        f"[View File]({file_link})"
                    )
                else:
                    st.error("Failed to upload the file.")
            else:
                st.error(
                    "Google Drive service not authenticated. Please authenticate first."
                )
        else:
            st.error("Please select a file to upload.")


def list_download_from_google_drive_UI(root_folder_id):
    st.divider()
    st.subheader("List and Download Files from Google Drive")

    # open google drive folder button
    folder_url = f"https://drive.google.com/drive/folders/{root_folder_id}"

    st.link_button("Open Google Drive Folder", url=folder_url)


if __name__ == "__main__":
    # initialize variable
    DOWNLOAD_FILE_PATH = "downloaded-files"
    TOKEN_FILE_PATH = "credentials.json"
    IS_SERVICE_ACCOUNT = True
    ROOT_FOLDER_ID = "10514rVBAqv21ry4gvRK-EP2wAxq3cjU6"

    HOST_WEB = os.getenv("HOST_WEB", "http://localhost:8501")
    HOST_API = os.getenv("HOST_API", "http://localhost:8000")

    if not os.path.exists(DOWNLOAD_FILE_PATH):
        os.makedirs(DOWNLOAD_FILE_PATH)

    def initialize_state(state_name, default_value=None):
        if state_name not in st.session_state:
            st.session_state[state_name] = (
                default_value if default_value is not None else []
            )

    def update_state(state_name, new_value):
        st.session_state[state_name] = new_value
        return st.session_state[state_name]

    initialize_state("list_all_files", os.listdir(DOWNLOAD_FILE_PATH))
    initialize_state("service", None)
    initialize_state("token_file_path", TOKEN_FILE_PATH)
    initialize_state("token_file_content", None)
    initialize_state("resolution", "480p")
    initialize_state("show_compress_progress_bar", False)
    initialize_state("show_token_content", False)
    initialize_state("show_delete_all_files_button", False)
    initialize_state("show_list_alert", False)
    initialize_state("file_alert", False)
    initialize_state("alert_message", None)
    initialize_state("compress_progress", 0)

    list_all_files = st.session_state.list_all_files
    service = st.session_state.service
    token_file_path = st.session_state.token_file_path
    token_file_content = st.session_state.token_file_content
    show_token_content = st.session_state.show_token_content

    def refresh_file_list():
        return update_state("list_all_files", os.listdir("downloaded-files"))

    def check_token_file_content():
        if os.path.exists(TOKEN_FILE_PATH):
            with open(TOKEN_FILE_PATH, "r") as f:
                update_state("token_file_content", f.read())

            return st.session_state.token_file_content

    def sanitize_input(input_value):
        return input_value.strip() if input_value and input_value.strip() else None

    def check_service():
        if st.session_state.service:
            service = st.session_state.service
        else:
            service = authenticate_drive(
                TOKEN_FILE_PATH, TOKEN_FILE_PATH, is_service_account=IS_SERVICE_ACCOUNT
            )

        return service

    # Compress video
    def compress_file(selected_file, resolution, progress_bar=None):
        file_name = f"{os.path.splitext(selected_file)[0]}_compressed_{resolution}{os.path.splitext(selected_file)[1]}"

        input_file = os.path.join(DOWNLOAD_FILE_PATH, selected_file)
        output_file = os.path.join(DOWNLOAD_FILE_PATH, file_name)

        if progress_bar:
            update_state("show_compress_progress_bar", True)
            update_state("compress_progress", 0)

        compress_video(
            input_file,
            output_file,
            quality=resolution,
            progress_bar=progress_bar if progress_bar else None,
        )

        refresh_file_list()

        update_state("file_alert", True)
        update_state("alert_message", f"File {selected_file} compressed successfully!")

    # Delete file
    def deleted(file_path, selected_file):
        delete_file(file_path)
        refresh_file_list()
        update_state("file_alert", True)
        update_state("alert_message", f"File {selected_file} deleted successfully!")

    def refresh_button():
        refresh_file_list()
        update_state("show_list_alert", True)
        update_state("alert_message", "File list refreshed successfully!")

    # UI
    # video download
    download_video_UI()

    # video compress
    compress_video_UI(DOWNLOAD_FILE_PATH, HOST_API)

    # google drive authentication
    google_drive_authentication_UI(TOKEN_FILE_PATH)

    # upload to google drive
    upload_google_drive_UI(ROOT_FOLDER_ID, DOWNLOAD_FILE_PATH)

    # download file from Google Drive
    list_download_from_google_drive_UI(ROOT_FOLDER_ID)
