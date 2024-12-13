import base64
import os
import tempfile

import cv2
import streamlit as st
import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
API_KEY = os.getenv("API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")


client = AzureOpenAI(
    api_version="2024-10-21",
    api_key=API_KEY,
    azure_endpoint=AZURE_ENDPOINT
)

# Streamlitの設定
st.title("マルチモーダルチャットアシスタント")
st.write("テスト、画像、動画を扱えるマルチモーダルチャットアプリケーション")

# ユーザー入力
user_input = st.text_input("あなた : ", "")

# 画像アップロードとOCR機能
def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

uploaded_file = st.file_uploader("画像を選択", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    base64_image = encode_image(uploaded_file)
    user_input = "この画像を説明してください:"

# 動画アップロード
def extract_frames(video_bytes):
    with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
        temp_video_file.write(video_bytes)
        temp_video_file_path = temp_video_file.name

    video = cv2.VideoCapture(temp_video_file_path)
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames

def calculate_token_count(base64_frames):
    # 1トークンあたりの平均バイト数を考慮して計算
    average_bytes_per_token = 4
    total_bytes = sum(len(frame) for frame in base64_frames)
    return total_bytes // average_bytes_per_token

def calculate_map_token_count(base64_frames):
    enc = tiktoken.encoding_for_model("gpt-4o")
    total_tokens = sum(len(enc.encode(frame)) for frame in base64_frames[0::200])
    return total_tokens

uploaded_video = st.file_uploader("動画を選択", type=["mp4"])

if uploaded_video is not None:
    user_input = "この動画を説明してください:"


if st.button("Video"):
    base64Frames = extract_frames(uploaded_video.read())
    token_count = calculate_token_count(base64Frames)
    map_token_count = calculate_map_token_count(base64Frames)
    st.write(f"推定トークン数: {token_count}")
    st.write(f"map関数での推定トークン数: {map_token_count}")
    print(f"推定トークン数: {token_count}")
    print(f"map関数での推定トークン数: {map_token_count}")

# AOAIとの接続
if st.button("Send"):
    if user_input:
        if uploaded_file is not None:
            messages = [
                {"role": "system", "content": "あなたは画像やテキストにも対応したチャットアシスタントです。すべての質問に日本語で返答してください。"},
                {"role": "user", "content": [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ]
        elif uploaded_video is not None:
            base64Frames = extract_frames(uploaded_video.read())
            messages = [
                {"role": "system", "content": "あなたは画像やテキストにも対応したチャットアシスタントです。すべての質問に日本語で返答してください。"},
                {"role": "user", "content": [
                    {"type": "text", "text": "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video."},
                    *map(lambda x: {"image": x, "resize": 240}, base64Frames[0::200]),
                ]}
            ]
            print(messages)
        else:
            messages = [
                {"role": "system", "content": "あなたは画像やテキストにも対応したチャットアシスタントです。すべての質問に日本語で返答してください。"},
                {"role": "user", "content": user_input},
            ]

        # API呼び出し
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        # レスポンスを表示
        assistant_response = response.choices[0].message.content
        st.markdown("**アシスタント :**")
        st.write(assistant_response)
    else:
        st.write("メッセージを入力してください")