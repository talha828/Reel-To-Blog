import os
import tempfile
import random
import yt_dlp
import speech_recognition as sr
import ollama
import imageio
from datetime import datetime
import subprocess
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# Constants
SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate_blogger():
    """Authenticate with Google Blogger API and return the service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('blogger', 'v3', credentials=creds)
    return service

def get_blog_id(service):
    """Retrieve the blog ID for the user's default blog."""
    blogs = service.blogs().listByUser(userId='self').execute()
    if 'items' in blogs:
        return blogs['items'][0]['id']  # Return the ID of the first blog
    else:
        print("No blogs found.")
        return None

def create_blog_post(service, blog_id, title, content, image_base64):
    """Create a new blog post on Google Blogger with proper formatting."""
    # Remove underscores from the main title
    main_title = title.replace("_", " ")

    # Extract the subheading and body from the content
    if "**Title:**" in content and "**Body:**" in content:
        subheading = content.split("**Title:**")[1].split("**Body:**")[0].strip()
        body = content.split("**Body:**")[1].strip()
    else:
        subheading = ""
        body = content

    # HTML template for the blog post
    blog_content = f"""
    <h1 style="text-align: center; font-size: 2em; margin-bottom: 20px;">{main_title}</h1>
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="data:image/jpeg;base64,{image_base64}" alt="Thumbnail" style="max-width: 100%; height: auto; border-radius: 10px;"/>
    </div>
    <h2 style="text-align: center; font-size: 1.5em; margin-bottom: 20px;">{subheading}</h2>
    <p>\n</p>
    <div style="font-size: 1.2em; line-height: 1.6;">
        {body}
    </div>
    """

    body = {
        'kind': 'blogger#post',
        'blog': {'id': blog_id},
        'title': main_title,  # Use the cleaned main title
        'content': blog_content,
    }
    post = service.posts().insert(blogId=blog_id, body=body).execute()
    print(f"Blog post created: {post['url']}")
    return post

def download_video(link):
    """Download video from YouTube or Instagram and return the file path and title."""
    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prefer MP4 format
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            video_path = ydl.prepare_filename(info)
            title = info.get("title", "untitled_video")
            video_id = info.get("id", "no_id")
        print(f"Downloaded video: {title}")
        return video_path, title, video_id
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None, None

def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from a video file and save it as a .wav file using FFMPEG."""
    try:
        command = [
            'ffmpeg',
            '-i', video_path,  # Input video file
            '-q:a', '0',       # Best audio quality
            '-map', 'a',       # Extract only audio
            output_audio_path  # Output audio file
        ]
        subprocess.run(command, check=True)
        print(f"Audio extracted to {output_audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")

def resize_and_crop_image(image_path, output_path, target_width=768, target_height=432):
    """
    Resize and crop an image to fit a landscape aspect ratio.
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the resized and cropped image.
        target_width (int): Target width for the landscape image.
        target_height (int): Target height for the landscape image.
    """
    with Image.open(image_path) as img:
        # Calculate the aspect ratio of the target dimensions
        target_aspect_ratio = target_width / target_height

        # Calculate the aspect ratio of the original image
        original_width, original_height = img.size
        original_aspect_ratio = original_width / original_height

        # Resize the image to fit the target aspect ratio
        if original_aspect_ratio > target_aspect_ratio:
            # If the original image is wider, resize based on height
            new_height = target_height
            new_width = int(new_height * original_aspect_ratio)
        else:
            # If the original image is taller, resize based on width
            new_width = target_width
            new_height = int(new_width / original_aspect_ratio)

        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate cropping coordinates to center the image
        left = max(0, (new_width - target_width) // 2)
        top = max(0, (new_height - target_height) // 2)
        right = min(new_width, left + target_width)
        bottom = min(new_height, top + target_height)

        # Crop the image
        cropped_img = resized_img.crop((left, top, right, bottom))

        # Save the cropped image
        cropped_img.save(output_path)
        print(f"Resized and cropped image saved to {output_path}")

def extract_random_frames(video_path, num_frames=5):
    """Extract random frames from the video and return their file paths."""
    reader = imageio.get_reader(video_path)
    frame_count = reader.count_frames()
    frame_indices = sorted(random.sample(range(frame_count), min(num_frames, frame_count)))
    frame_paths = []

    for idx in frame_indices:
        frame = reader.get_data(idx)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        imageio.imwrite(temp_file.name, frame)

        # Resize and crop the frame to landscape
        resized_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        resize_and_crop_image(temp_file.name, resized_file)

        frame_paths.append(resized_file)

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
                       f"It should have two things: title and body. Use easy English and write in a friendly way with some emoji."
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

def encode_image_to_base64(image_path):
    """Encode an image to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def read_links_from_file(file_path):
    """Read YouTube Shorts links from a file."""
    with open(file_path, "r") as file:
        links = [line.strip() for line in file if line.strip()]
    return links

def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    # Replace invalid characters with an underscore
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    # Remove emojis and other non-ASCII characters
    sanitized = sanitized.encode('ascii', 'ignore').decode('ascii')
    return sanitized

def process_video(video_link):
    """Process a single video link."""
    video_path, title, video_id = download_video(video_link)

    if not video_path or not title:
        print(f"Error: Could not download video from {video_link}.")
        return

    title = sanitize_filename(title.replace(" ", "_")).replace(" ", "_")  # Sanitize title for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Add timestamp for uniqueness
    unique_id = f"{title}_{video_id}_{timestamp}"  # Combine title, video ID, and timestamp

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
            blog_file = f"output/blogs/{unique_id}_blog.txt"
            save_to_file(blog, blog_file)

            # Step 5: Save frames to a folder named after the unique ID
            frames_folder = f"output/images/{unique_id}_frames"
            save_frames_to_folder(frames, frames_folder)

            # Step 6: Encode the first frame as base64
            thumbnail_path = os.path.join(frames_folder, "thumbnail_1.jpg")
            base64_image = encode_image_to_base64(thumbnail_path)

            # Step 7: Post to Google Blogger with the embedded image
            print("Authenticating with Google Blogger API...")
            service = authenticate_blogger()

            print("Fetching blog ID...")
            blog_id = get_blog_id(service)
            if not blog_id:
                print("Error: Could not retrieve blog ID.")
                return

            print("Creating blog post...")
            create_blog_post(service, blog_id, title, blog, base64_image)

    # Cleanup temporary files
    os.remove(audio_path)
    os.remove(video_path)

    print(f"Process completed for video: {video_link}")

def scrape_shorts_links(channel_url, max_links=100):
    """Scrape YouTube Shorts links from a channel."""
    # Set up Selenium WebDriver
    option = Options()
    option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

    # Open the channel's Shorts page
    driver.get(f"{channel_url}/shorts")

    # Scroll to load more videos
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    shorts_links = []

    while len(shorts_links) < max_links:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)  # Wait for new videos to load

        # Extract video links using the specific class
        videos = driver.find_elements(By.CSS_SELECTOR, "a.shortsLockupViewModelHostEndpoint.reel-item-endpoint")
        for video in videos:
            href = video.get_attribute("href")
            if href and "/shorts/" in href and href not in shorts_links:
                shorts_links.append(href)
                if len(shorts_links) >= max_links:
                    break

        # Break if no new content is loaded
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    return shorts_links

def save_links_to_file(links, filename="shorts_links.txt"):
    """Save the list of links to a file."""
    with open(filename, "w") as file:
        for link in links:
            file.write(link + "\n")
    print(f"Saved {len(links)} links to {filename}")

def main():
    print("Welcome to the YouTube Shorts to Blog Converter!")
    choice = input("Do you want to scrape a YouTube channel for Shorts links or create a single blog post? (scrape/single): ").strip().lower()

    if choice == "scrape":
        channel_url = input("Enter the YouTube channel URL (e.g., https://www.youtube.com/@zackdfilms): ").strip()
        max_links = int(input("Enter the maximum number of Shorts links to scrape (e.g., 50): ").strip())
        print("Scraping Shorts links...")
        shorts_links = scrape_shorts_links(channel_url, max_links=max_links)
        save_links_to_file(shorts_links)
        print("Starting blog creation process...")
        for video_link in shorts_links:
            print(f"Processing video: {video_link}")
            process_video(video_link)
    elif choice == "single":
        video_link = input("Enter the YouTube Shorts link: ").strip()
        if "/shorts/" not in video_link:
            print("Error: Please provide a valid YouTube Shorts link.")
            return
        print("Starting blog creation process...")
        process_video(video_link)
    else:
        print("Invalid choice. Please enter 'scrape' or 'single'.")

if __name__ == "__main__":
    main()