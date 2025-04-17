# choose compress video with options quality 240p 360p 480p 720p 1080p
def compress_video(
    input_file,
    output_file,
    quality="240p",
    progress_bar=None,
):
    import subprocess
    import re

    """Compress video using ffmpeg with specified quality and resolution."""

    resolution = ""
    video_bitrate = ""
    video_quality = ""

    # Define the ffmpeg command based on the selected quality
    if quality == "240p":
        resolution = "426:240"
        video_bitrate = "500k"
        video_quality = "31"
    elif quality == "360p":
        resolution = "640:360"
        video_bitrate = "800k"
        video_quality = "23"
    elif quality == "480p":
        resolution = "854:480"
        video_bitrate = "1000k"
        video_quality = "23"
    elif quality == "720p":
        resolution = "1280:720"
        video_bitrate = "2000k"
        video_quality = "23"
    elif quality == "1080p":
        resolution = "1920:1080"
        video_bitrate = "4000k"
        video_quality = "23"
    else:
        raise ValueError(
            "Invalid quality option. Choose from 240p, 360p, 480p, 720p, or 1080p."
        )
    # Construct the ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        video_quality,
        "-b:v",
        video_bitrate,
        "-vf",
        f"scale={resolution}",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        output_file,
    ]

    # Print the command for debugging
    # print("Running command:", " ".join(ffmpeg_cmd))

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
                        progress_bar.progress(
                            percent, text=f"{int(percent * 100)}% completed"
                        )
                        last_update_time = current_time

        progress_bar.progress(1.0, text="100% completed")


def get_duration(input_file):
    import subprocess

    """Get duration of video in seconds."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return float(result.stdout.strip())
