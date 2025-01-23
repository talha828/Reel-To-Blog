import os
import moviepy as mp
import speech_recognition as sr
import ollama
from pyexpat.errors import messages


def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from a video file and save it as a .wav file."""
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    print(f"Audio extracted to {output_audio_path}")

def transcribe_audio(audio_path):
    """Convert audio file to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        print("Transcribing audio...")
        audio = recognizer.record(source)
        try:
            transcript = recognizer.recognize_vosk(audio)
            print("Transcription completed.")
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
        messages=[{'role': 'user', 'content': f"Create a short blog based on the following transcript:\n{transcript}. it suppose to have two things title and body use easy english and friendly way to write blog"}],
    )
    print(response.message)
    if response.message and response:
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

def main():
    # Input video file path
    video_path = 'C:\\Users\\talha\\PycharmProjects\\ReelToVlog\\video\\videoplayback.mp4'
    if not os.path.exists(video_path):
        print("Error: Video file not found.")
        return

    # Output paths
    audio_path = "extracted_audio.wav"
    transcript_path = "transcript.txt"
    blog_path = "blog.txt"

    # Step 1: Extract audio from the video
    extract_audio_from_video(video_path, audio_path)

    # Step 2: Transcribe the audio to text
    transcript = transcribe_audio(audio_path)
    if transcript:
        save_to_file(transcript, transcript_path)

        # Step 3: Generate a blog using the Ollama model
        blog = generate_blog_with_ollama(transcript)
        if blog:
            save_to_file(blog, blog_path)

if __name__ == "__main__":
    main()
