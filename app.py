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

# ユーザー入力欄を作成
user_input = st.text_input("あなた : ", "")

# 画像をbase64にエンコードする
def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

# 画像入力欄を作成
uploaded_image = st.file_uploader("画像を選択", type=["jpg", "jpeg", "png"])


# 動画をフレームに分割する
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

# 動画入力欄を作成
uploaded_video = st.file_uploader("動画を選択", type=["mp4"])

# 一リクエストあたりに使用するトークン数の推定を出す
def calculate_map_token_count(base64_frames):
    enc = tiktoken.encoding_for_model("gpt-4o")
    total_tokens = sum(len(enc.encode(frame)) for frame in base64_frames[0::200])
    return total_tokens


# ローカルでトークン数の推定を行う
if st.button("トークン数の推定"):
    base64Frames = extract_frames(uploaded_video.read())
    map_token_count = calculate_map_token_count(base64Frames)
    st.write(f"map関数での推定トークン数: {map_token_count}")
    print(f"map関数での推定トークン数: {map_token_count}")

# AOAIへリクエストを送る
if st.button("送信"):
    if user_input:
        if uploaded_image is not None:
            base64_image = encode_image(uploaded_image)
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