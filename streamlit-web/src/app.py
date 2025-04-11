import streamlit as st
import os
# from utils.drive_utils import authenticate_drive, upload_file
# from utils.compression_utils import compress_video


def main():
    if not os.path.exists("downloaded-files"):
        os.makedirs("downloaded-files")
        
    if "list_all_files" not in st.session_state:
        st.session_state.list_all_files = os.listdir("downloaded-files")
    
    list_all_files = st.session_state.list_all_files

    def refresh_file_list():
        st.session_state.list_all_files = os.listdir("downloaded-files")
        return st.session_state.list_all_files

    st.title("Video Upload to Google Drive")

    # Request download link
    download_link = st.text_input("Enter the download link for the video:")

    if "index" not in st.session_state:
        st.session_state.index = 1

    if st.button("Download file"):
        if download_link:
            # Simulate file download
            index = st.session_state.index
            file_name = f"downloaded-files/video_{index}.mp4"
            with open(file_name, "wb") as f:
                # Simulate writing to file
                f.write(os.urandom(1024))
            index += 1
            st.session_state.index = index
            list_all_files = refresh_file_list()
            
            st.success(f"File downloaded from {download_link}!")
        else:
            st.error("Please enter a valid download link.")

    # Compress selected file
    selected_file = st.selectbox("Select a file to compress:", list_all_files)
    if st.button("Compress Video"):
        if selected_file:
            file_name = f"{os.path.splitext(selected_file)[0]}_compressed{os.path.splitext(selected_file)[1]}"
            file_path = f"downloaded-files/{file_name}"
            with open(file_path, "wb") as f:
                # Simulate writing to file
                f.write(os.urandom(1024))
            st.success(f"File {file_name} compressed successfully!")
        else:
            st.error("Please select a file to compress.")
    
    # Google drive parts
    st.divider()
    st.subheader("Upload to Google Drive")

    # Upload token or credentials file
    if "token_file" not in st.session_state:
        # check if token file is already uploaded
        if os.path.exists("temp_credentials.json"):
            with open("temp_credentials.json", "r") as f:
                st.session_state.token_file = f.read()
        else:
            st.session_state.token_file = None
    
    token_file = st.file_uploader("Upload token.json or credentials.json", type=["json"])

    if token_file is not None:
        st.session_state.token_file = token_file

    token_file = st.session_state.token_file

    if st.button("Upload Token File"):
        if token_file is not None:
            # Save the uploaded token file temporarily
            with open("temp_credentials.json", "wb") as f:
                f.write(token_file.getbuffer())
            
            with open("temp_credentials.json", "r") as f:
                st.session_state.token_file = f.read()
                
            st.success("Token file uploaded successfully!")
        else:
            st.error("Please upload a valid token file.")
    
    # Show the content of the uploaded token file
    if st.button("Show/Hide Token File Content"):
        if "show_token_content" not in st.session_state:
            st.session_state.show_token_content = False

        st.session_state.show_token_content = not st.session_state.show_token_content

    if st.session_state.get("show_token_content", False):
        if token_file is not None:
            token_content = st.session_state.token_file
            st.text_area("Token File Content", token_content, height=200)
        else:
            st.error("No token file uploaded.")

    # Choose file to upload from the downloaded file folder
    selected_file = st.selectbox("Select a video file to upload:", list_all_files)
    if selected_file:
        st.success(f"Selected file: {selected_file}")
    # Simulate file upload
    if st.button("Upload File"):
        if selected_file:
            # Simulate file upload
            st.success(f"File {selected_file} uploaded to Google Drive!")
        else:
            st.error("Please select a file to upload.")
  

if __name__ == "__main__":
    main()