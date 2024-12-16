# 概要
テキスト、画像、動画を扱えるマルチモーダルアプリケーションデモです。

# 事前準備
1. Azure Open AI のリソース
2. GPT-4o-miniのモデルのデプロイ
3. Python実行環境

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


# アプリケーションの使い方

## テキストを送るとき
1. 「あなた:」の欄にテキストを入力
2. 「送信」ボタンをクリック

## 画像を送るとき
1. 「画像を選択」のBrowse filesを選択し、画像を選ぶ
2. 合わせてテキストを送りたい場合は、「あなた:」の欄にテキストを入力
3. 「送信」ボタンをクリック


## 動画を送るとき
1. 「動画を選択」のBrowse filesを選択し、動画を選ぶ
2. 合わせてテキストを送りたい場合は、「あなた:」の欄にテキストを入力
3. 「送信」ボタンをクリック