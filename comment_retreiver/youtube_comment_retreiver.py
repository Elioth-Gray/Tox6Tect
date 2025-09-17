from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import time
from tqdm import tqdm
import re
import requests
from bs4 import BeautifulSoup
import socket
import random

# ===== API KEYS (ISI DENGAN PUNYAMU) =====
API_KEYS = [
    ""  # ganti dengan key kamu
]

# ===== UTILITIES =====
def get_video_id_from_url(url_or_id):
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    match = re.search(r'(?:v=|/shorts/|/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url_or_id)
    if match:
        return match.group(1)
    return None

def get_youtube_client(index):
    return build("youtube", "v3", developerKey=API_KEYS[index])

def get_video_title(youtube, video_id):
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        if not response["items"]:
            print(f"⚠️ Video ID {video_id} not found or not public.")
            return None
        return response["items"][0]["snippet"]["title"]
    except HttpError as e:
        status = e.resp.status
        print(f"⚠️ Failed to fetch title via API (HTTP {status}). Trying scraping fallback...")
    except Exception as e:
        print(f"⚠️ Failed to fetch title via API. Error: {e}. Trying scraping fallback...")

    # Fallback: scrape the YouTube page
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/90.0.4430.93 Safari/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text.replace("- YouTube", "").strip()
            print(f"✅ Title scraped successfully: {title}")
            return title
    except Exception as e:
        print(f"❌ Failed to scrape video title. Error: {e}")

    return "Unknown Title"

def get_comment_replies(parent_id, youtube, seen_comments, video_id, video_title):
    replies = []
    next_page_token = None
    while True:
        try:
            response = youtube.comments().list(
                part="snippet",
                parentId=parent_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()
            for item in response["items"]:
                reply = item["snippet"]
                reply_id = item["id"]
                if reply_id not in seen_comments:
                    replies.append({
                        "video_id": video_id,
                        "video_title": video_title,
                        "comment_id": parent_id,
                        "type": "reply",
                        "author": reply["authorDisplayName"],
                        "text": reply["textDisplay"],
                        "like_count": reply.get("likeCount", 0),
                        "published_at": reply["publishedAt"]
                    })
                    seen_comments.add(reply_id)
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        except HttpError as e:
            if e.resp.status in [403, 429]:
                raise e
            else:
                print(f"⚠️ Error while fetching comment replies: {e}")
                break
    return replies

def get_video_comments(video_id, api_keys, max_retries=5):
    if not api_keys or api_keys[0] == "YOUR_API_KEY_HERE":
        print("❌ API key belum diisi! Tambahkan API key YouTube Data API v3 di bagian API_KEYS.")
        return []

    comments = []
    seen_comments = set()
    next_page_token = None
    api_index = 0
    youtube = get_youtube_client(api_index)

    video_title = get_video_title(youtube, video_id)
    if not video_title:
        print(f"❌ Skipping video {video_id} due to missing title.")
        return comments

    pbar = tqdm(desc=f"Fetching comments from {video_id}")

    retries = 0
    while retries < max_retries:
        try:
            response = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()
            for item in response["items"]:
                comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["snippet"]["topLevelComment"]["id"]
                if comment_id not in seen_comments:
                    comments.append({
                        "video_id": video_id,
                        "video_title": video_title,
                        "comment_id": comment_id,
                        "type": "main",
                        "author": comment_snippet["authorDisplayName"],
                        "text": comment_snippet["textDisplay"],
                        "like_count": comment_snippet.get("likeCount", 0),
                        "published_at": comment_snippet["publishedAt"]
                    })
                    seen_comments.add(comment_id)
                    pbar.update(1)
                if "replies" in item:
                    replies = get_comment_replies(comment_id, youtube, seen_comments, video_id, video_title)
                    comments.extend(replies)
                    pbar.update(len(replies))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
            time.sleep(0.1)
        except HttpError as e:
            if e.resp.status in [403, 429]:
                api_index += 1
                if api_index >= len(api_keys):
                    print("❌ All API keys have reached quota limits.")
                    break
                print(f"🔁 Switching to next API key (index {api_index})...")
                youtube = get_youtube_client(api_index)
                time.sleep(1)
                continue
            elif e.resp.status == 404:
                print(f"⚠️ Video {video_id} not found (404).")
                break
            elif e.resp.status == 403:
                print(f"⚠️ Comments are disabled for video {video_id}.")
                break
            else:
                print(f"⚠️ Unexpected HTTP error: {e}")
                break
        except (ConnectionResetError, socket.timeout) as e:
            retries += 1
            print(f"🔁 Network error ({e}). Retrying ({retries}/{max_retries})...")
            time.sleep(5 + random.uniform(1, 3))
            continue
        except Exception as e:
            print(f"❌ Unknown error while fetching comments: {e}")
            break

    pbar.close()
    return comments

# ===== VIDEO URLS / IDS =====
video_inputs = [
    "https://www.youtube.com/watch?v=dMywBOCoLiQ",
]

# ===== EXECUTE =====
all_comments = []
for url_or_id in video_inputs:
    vid = get_video_id_from_url(url_or_id)
    if vid:
        result = get_video_comments(vid, API_KEYS)
        all_comments.extend(result)
    else:
        print(f"❌ Failed to process input: {url_or_id}")

# ===== SAVE TO CSV =====
if all_comments:
    df = pd.DataFrame(all_comments)
    df.to_csv("multi_video_comments_with_title.csv", index=False, encoding="utf-8-sig")
    print("\n✅ All comments saved to multi_video_comments_with_title.csv")
else:
    print("\n⚠️ Tidak ada komentar yang berhasil diambil.")
