def compress_video(
    input_file,
    output_file,
    video_bitrate="1000k",
    video_quality="31",
    resolution="640:480",
    progress_bar=None,
):
    import subprocess
    import re

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-vf",
        f"scale={resolution}",
        "-b:v",
        video_bitrate,
        "-vcodec",
        "libx265",
        "-crf",
        video_quality,
        "-preset",
        "veryfast",
        output_file,
    ]


    process = subprocess.Popen(
        ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    current_time = 0.0
    progress_update_interval = 0.5  # Update progress every 0.5 seconds
    last_update_time = 0.0

    if progress_bar:
        duration = get_duration(input_file)
        for line in process.stdout:
            print(line.strip())  # Print the ffmpeg output for debugging
            if "out_time_ms=" in line:
                match = re.search(r"out_time_ms=(\d+)", line)
                if match:
                    out_time_ms = int(match.group(1))
                    current_time = out_time_ms / 1_000_000  # convert to seconds
                    percent = min(current_time / duration, 1.0)

                    # Only update the progress bar at defined intervals
                    if current_time - last_update_time >= progress_update_interval:
                        progress_bar.progress(percent, text=f"{int(percent * 100)}% completed")
                        last_update_time = current_time

        progress_bar.progress(1.0, text="100% completed")



def get_duration(input_file):
    import subprocess

    """Get duration of video in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_file],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return float(result.stdout.strip())