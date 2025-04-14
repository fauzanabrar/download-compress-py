import streamlit as st
import os
from utils.drive_utils import (
    authenticate_drive,
    get_lists_of_folders,
    upload_large_file_to_drive,
    get_drive_quota,
    delete_all_drive_files,
)

# from utils.compression_utils import compress_video
from utils.download_utils import download_file


def download_video_UI():
    st.title("Video Upload to Google Drive")

    # Request download link
    download_link = st.text_input("Enter the download link for the video:")

    if st.button("Download file"):
        if download_link:
            download_file(download_link)
            refresh_file_list()
            st.success(f"File downloaded from {download_link}!")
        else:
            st.error("Please enter a valid download link.")


def compress_video_UI(download_file_path):
    # Compress selected file
    list_all_files = st.session_state.list_all_files
    selected_file = st.selectbox("Select a file to compress:", list_all_files)
    if st.button("Compress Video"):
        if selected_file:
            file_name = f"{os.path.splitext(selected_file)[0]}_compressed{os.path.splitext(selected_file)[1]}"
            file_path = f"{download_file_path}/{file_name}"
            with open(file_path, "wb") as f:
                # Simulate writing to file
                f.write(os.urandom(1024))

            refresh_file_list()
            st.success(f"File {file_name} compressed successfully!")
        else:
            st.error("Please select a file to compress.")


def google_drive_authentication_UI(token_file_path):
    st.divider()
    st.subheader("Authenticate to Google Drive")

    token_file_input = st.file_uploader(
        "Upload token.json or credentials.json", type=["json"]
    )
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
    if st.button("Show/Hide Token File Content"):
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

    # Choose file to upload from the downloaded file folder
    if st.button("Refresh File List"):
        list_all_files = refresh_file_list()
        st.success("File list refreshed!")

    if st.button("Get Google Drive Quota"):
        service = st.session_state.service
        print("Getting Google Drive quota...")
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
            print("Deleting all files in Google Drive...")
            with st.spinner("Deleting files..."):
                service = st.session_state.service
                deleted_count, error = delete_all_drive_files(service, dry_run=False)

                if deleted_count > 0:
                    st.toast(f"Deleted {deleted_count} files from Google Drive.")
                else:
                    st.error(
                        f"Failed to delete files from Google Drive. Errors: {error}"
                    )

            # Hide the button after it is clicked
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
                progress_text = st.empty()

                file_id = upload_large_file_to_drive(
                    service,
                    file_path,
                    file_name,
                    folder_id,
                    progress_bar,
                    progress_text,
                )

                if file_id:
                    st.success(
                        f"File {selected_file} uploaded to Google Drive with ID: {file_id}"
                    )
                else:
                    st.error("Failed to upload the file.")
            else:
                st.error(
                    "Google Drive service not authenticated. Please authenticate first."
                )
        else:
            st.error("Please select a file to upload.")


if __name__ == "__main__":
    # initialize variable
    DOWNLOAD_FILE_PATH = "downloaded-files"
    TOKEN_FILE_PATH = "credentials.json"
    IS_SERVICE_ACCOUNT = True
    ROOT_FOLDER_ID = "10514rVBAqv21ry4gvRK-EP2wAxq3cjU6"

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
    initialize_state("show_token_content", False)
    initialize_state("show_delete_all_files_button", False)

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

    # UI
    # video download
    download_video_UI()

    # video compress
    compress_video_UI(DOWNLOAD_FILE_PATH)

    # google drive authentication
    google_drive_authentication_UI(TOKEN_FILE_PATH)

    # upload to google drive
    upload_google_drive_UI(ROOT_FOLDER_ID, DOWNLOAD_FILE_PATH)
