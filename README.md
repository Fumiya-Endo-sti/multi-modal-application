# multi-modal-chat

# 初期作業

1. venv環境を作成
```
python -m venv myenv
```

2. パッケージのインストール
```
apt -y install libopencv-dev
pip install streamlit openai opencv-python python-dotenv
```

3. .env ファイルの作成
```
API_KEY=<AOAI APIキー>
AZURE_ENDPOINT=<AOAI エンドポイント>
```

# アプリケーションの実行方法
```
streamlit run app.py
```