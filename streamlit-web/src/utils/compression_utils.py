def compress_video(input_file, output_file, video_bitrate='1000k', video_quality='31', resolution='640:480'):
    import subprocess

    ffmpeg_cmd = [
        'ffmpeg', 
        '-i', input_file, 
        '-vf', f'scale={resolution}', 
        '-b:v', video_bitrate, 
        '-vcodec', 'libx265', 
        '-crf', video_quality, 
        '-preset', 'veryfast', 
        output_file
    ]

    subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

def should_compress_file(compress_option):
    return compress_option == 'Yes'