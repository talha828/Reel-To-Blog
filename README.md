
![CheatBoard 1](https://github.com/user-attachments/assets/3e6b96a1-eba8-459a-bd55-eb72ec5cadf7)


# YouTube Shorts to Blog Converter

This Python script allows you to convert YouTube Shorts videos into blog posts automatically. It downloads the video, extracts audio, transcribes it, generates a blog using the Ollama language model, and posts it to Google Blogger with an embedded thumbnail. This tool is perfect for micro-learning and micro-earning by leveraging free tools like Google Blogger for monetization.



## How the Script Works

The script follows a step-by-step process to convert YouTube Shorts videos into blog posts:

### 1. **Download the Video**
   - The script uses the `yt-dlp` library to download the YouTube Shorts video in MP4 format.
   - The video title and ID are extracted for naming and identification purposes.

### 2. **Extract Audio**
   - The script uses **MoviePy** to extract audio from the downloaded video.
   - The audio is saved as a `.wav` file for transcription.

### 3. **Transcribe Audio to Text**
   - The script uses the **Vosk** open-source speech recognition model to transcribe the audio into text.
   - Vosk supports multiple languages and provides accurate transcriptions.

### 4. **Generate Blog Content**
   - The transcribed text is passed to the **Ollama language model** (version 3.2) to generate a blog post.
   - The blog includes a title and body, written in a friendly and easy-to-understand style.

### 5. **Extract Random Frames**
   - The script extracts random frames from the video using the `imageio` library.
   - These frames are resized and cropped to fit a landscape aspect ratio.

### 6. **Post to Google Blogger**
   - The script authenticates with the Google Blogger API using OAuth 2.0.
   - It creates a new blog post with the generated content and embeds the first frame as a thumbnail.
   - The blog post is published to your Blogger account.

---

## Features

1. **Automated Blog Creation**:
   - Converts YouTube Shorts videos into blog posts with minimal user input.
   - Generates a blog title and body using the **Ollama language model**.

2. **Micro-Learning**:
   - Transcribes video content into text for easy reading and learning.
   - Ideal for creating educational content from short videos.

3. **Micro-Earning**:
   - Automatically posts blogs to Google Blogger, enabling monetization through ads.
   - Free to use with no additional costs for tools (except YouTube API if used).

4. **Customizable**:
   - Supports scraping multiple Shorts links from a YouTube channel.
   - Allows processing a single video link for quick blog creation.

5. **Open Source**:
   - Free to use, modify, and distribute.

---

## Prerequisites

Before using this script, ensure you have the following installed and set up:

### 1. **FFmpeg**
FFmpeg is required to extract audio from videos. Install it using the following steps:

- **Windows**:
  1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).
  2. Extract the downloaded zip file.
  3. Add the `bin` folder to your system's PATH environment variable.

- **Linux**:
  ```bash
  sudo apt update
  sudo apt install ffmpeg
  ```

- **macOS**:
  ```bash
  brew install ffmpeg
  ```

### 2. **Ollama 3.2**
Ollama is used to generate blog content from video transcripts. Install it as follows:

1. Visit the [Ollama GitHub repository](https://github.com/ollama/ollama) for installation instructions.
2. Download and install Ollama for your operating system.
3. Ensure the Ollama server is running locally.

### 3. **Python Dependencies**
Install the required Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

---

## How to Use

### Step 1: Set Up Google Blogger API
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Blogger API** for your project.
4. Create OAuth 2.0 credentials and download the `credentials.json` file.
5. Place the `credentials.json` file in the project directory.

### Step 2: Configure the Script
1. Clone this repository:
   ```bash
   git clone https://github.com/talha828/Reel-To-Blog.git
   cd Reel-To-Blog
   ```
2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Run the Script
1. Run the script:
   ```bash
   python main.py
   ```
2. Choose one of the following options:
   - **Scrape a YouTube Channel**:
     - Enter the YouTube channel URL (e.g., `https://www.youtube.com/@zackdfilms`).
     - Specify the number of Shorts links to scrape.
   - **Create a Single Blog Post**:
     - Provide a YouTube Shorts link directly.

3. The script will:
   - Download the video.
   - Extract audio using **MoviePy**.
   - Transcribe the audio using the **Vosk** open-source model.
   - Generate a blog using Ollama.
   - Post the blog to Google Blogger with an embedded thumbnail.

---

## Benefits

### 1. **Micro-Learning**
- Convert short, engaging videos into readable blog posts.
- Ideal for summarizing educational content or tutorials.

### 2. **Micro-Earning**
- Automatically post blogs to Google Blogger for monetization.
- Earn through Google AdSense by driving traffic to your blog.

### 3. **Free Tools**
- Uses free tools like Google Blogger, Ollama, MoviePy, and Vosk.
- No additional costs for software or APIs (except YouTube API if used).

### 4. **Time-Saving**
- Automates the entire process of downloading, transcribing, and posting.
- Focus on creating content while the script handles the rest.

---

## Example Workflow

1. **Scrape a YouTube Channel**:
   - Input: `https://www.youtube.com/@zackdfilms`
   - Output: 50 Shorts links scraped and processed into blog posts.

2. **Create a Single Blog Post**:
   - Input: `https://www.youtube.com/shorts/PZ3EInK8eRU`
   - Output: A blog post titled "Why Do Nose Bleeds Happen?" with transcribed content.

---

## Troubleshooting

### 1. **Invalid File Path Error**
- Ensure the video title does not contain invalid characters (e.g., `?`, `!`, emojis). The script automatically sanitizes file names.

### 2. **Ollama Not Running**
- Start the Ollama server locally before running the script.

### 3. **FFmpeg Not Found**
- Verify that FFmpeg is installed and added to your system's PATH.

### 4. **Google Blogger API Issues**
- Ensure the `credentials.json` file is correctly placed in the project directory.
- Authenticate using the OAuth flow when prompted.

---

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

If you find this project helpful, consider giving it a ⭐ on GitHub. For questions or issues, open an issue in the repository.

---

Happy blogging! 🚀

---

This version clearly explains how the script works, including the use of **MoviePy** and **Vosk**, while keeping the **Features** section concise. Let me know if you need further adjustments! 😊
