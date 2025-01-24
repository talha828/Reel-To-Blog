import os
import tempfile
import random
from pytube import YouTube
import yt_dlp
import moviepy as mp
import speech_recognition as sr
import ollama
import imageio

def download_video(link):
    """Download video from YouTube or Instagram and return the file path and title."""
    try:
        ydl_opts = {'outtmpl': '%(title)s.%(ext)s', 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            video_path = ydl.prepare_filename(info)
            title = info.get("title", "untitled_video")
        print(f"Downloaded video: {title}")
        return video_path, title
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None


def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from a video file and save it as a .wav file."""
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path, logger=None)
    print(f"Audio extracted to {output_audio_path}")


def extract_random_frames(video_path, num_frames=1):
    """Extract random frames from the video and return their file paths."""
    reader = imageio.get_reader(video_path)
    frame_count = reader.count_frames()
    frame_indices = sorted(random.sample(range(frame_count), min(num_frames, frame_count)))
    frame_paths = []

    for idx in frame_indices:
        frame = reader.get_data(idx)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        imageio.imwrite(temp_file.name, frame)
        frame_paths.append(temp_file.name)

    reader.close()
    print(f"Extracted {len(frame_paths)} random frames.")
    return frame_paths


def transcribe_audio(audio_path):
    """Convert audio file to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        print("Transcribing audio...")
        audio = recognizer.record(source)
        try:
            transcript = recognizer.recognize_vosk(audio)
            print("Transcription completed.")
            print("Transcript:\n", transcript)
            return transcript
        except sr.UnknownValueError:
            print("Speech Recognition could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""


def generate_blog_with_ollama(transcript, model_name="llama3.2"):
    """Generate a blog using the Ollama Python library."""
    print("Generating blog with Ollama...")
    response = ollama.chat(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': f"Create a short blog based on the following transcript:\n{transcript}. "
                       f"It should have two things: title and body. Use easy English and write in a friendly way."
        }],
    )
    if response and response.message:
        print("Blog generation completed.")
        return response.message.content
    else:
        print("Error: Unable to generate blog.")
        return ""


def save_to_file(content, file_path):
    """Save text content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Content saved to {file_path}")


def save_frames_to_folder(frame_paths, folder_name):
    """Save extracted frames to a folder."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for i, frame_path in enumerate(frame_paths):
        frame_filename = os.path.join(folder_name, f"thumbnail_{i + 1}.jpg")
        os.rename(frame_path, frame_filename)
        print(f"Saved frame to {frame_filename}")


def main():
    # Input: YouTube or Instagram link
    video_link = "https://www.instagram.com/p/DFK7X0PNpA_/"
    video_path, title = download_video(video_link)

    if not video_path or not title:
        print("Error: Could not download video.")
        return

    title = title.replace(" ", "_")  # Sanitize title for file naming
    audio_path = "temp_audio.wav"

    # Step 1: Extract audio from the video
    extract_audio_from_video(video_path, audio_path)

    # Step 2: Extract random frames
    frames = extract_random_frames(video_path)

    # Step 3: Transcribe the audio to text
    transcript = transcribe_audio(audio_path)

    if transcript:
        # Step 4: Generate a blog using the Ollama model
        blog = generate_blog_with_ollama(transcript)

        if blog:
            blog_file = f"blog/{title}_blog.txt"
            save_to_file(blog, blog_file)

            # Step 5: Save frames to a folder named after the blog file
            frames_folder = f"{title}_frames"
            save_frames_to_folder(frames, frames_folder)

    # Cleanup temporary files
    os.remove(audio_path)
    os.remove(video_path)

    print("Process completed successfully!")


if __name__ == "__main__":
    main()