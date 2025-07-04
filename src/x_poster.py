# src/x_poster.py
import json
import requests
from requests_oauthlib import OAuth1
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

api_key = config.X_API_KEY
api_secret = config.X_API_SECRET
access_token = config.X_ACCESS_TOKEN
access_token_secret = config.X_ACCESS_TOKEN_SECRET

def trim_to_140_chars(text: str) -> str:
    """テキストをXの投稿制限（ここでは全角140字）に合わせて調整する。"""
    if len(text) <= 140:
        return text
    last_period = text[:140].rfind("。")
    if last_period != -1:
        return text[:last_period + 1]
    return text[:140]

def post_to_x(text: str, bearer_token=None):
    """
    指定されたテキストをXに投稿する。
    - bearer_token: OAuth2ユーザー認証で取得したアクセストークン（推奨）
    - OAuth1.0a認証もサポート（ただしAPI権限が必要）
    """
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
        auth = None
    else:
        # OAuth1.0a認証（API権限が必要）
        auth = OAuth1(api_key, api_secret, access_token, access_token_secret)
    try:
        response = requests.post(url, headers=headers, json=payload, auth=auth)
        if response.status_code == 429:
            print("警告: X (Twitter) APIのレート制限に達しました。今回の投稿はスキップします。")
            return
        if response.status_code == 403:
            print(f"警告: 投稿が拒否されました (403 Forbidden): {response.text}")
            print("ツイート内容が直近のものと重複している可能性があります。あるいはAPI権限不足です。")
            return
        if response.status_code not in (200, 201):
            raise Exception(f"Xへの投稿に失敗しました: {response.status_code} {response.text}")
        print(f"✅ Xに投稿しました: {text}")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"エラー: Xへの投稿中に予期せぬエラーが発生しました: {e}")
        # raise e  # 必要に応じて再スロー
def run_tests():
    """投稿モジュールの機能をテストする。"""
    print("--- `trim_to_140_chars` 関数のテスト ---")
    
    # テストケース
    long_text = "これは非常に長いテストツイートです。140字を超えますが、途中に句点があります。この句点でうまく切れるはずです。ここが140字のラインです。この後の文章は切り捨てられます。"
    short_text = "これは短いツイートです。"

    print(f"元テキスト（長い）: {long_text}")
    print(f"調整後: {trim_to_140_chars(long_text)}\n")
    
    print(f"元テキスト（短い）: {short_text}")
    print(f"調整後: {trim_to_140_chars(short_text)}\n")

    print("--- `post_to_x` 関数のテスト ---")
    test_tweet = "これはテストです。"
    
    # 念のため文字数調整をかけてから投稿
    final_tweet = trim_to_140_chars(test_tweet)
    print(f"投稿するテキスト: {final_tweet}")
    post_to_x(final_tweet)

def get_latest_tweet(json_path: str) -> str:
    """
    指定されたJSONファイルから、最新のツイート文を取得する。
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"知識ベースファイルが見つかりません: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # データが存在し、'knowledge_entries'リストが空でないことを確認
    if "knowledge_entries" not in data or not data["knowledge_entries"]:
        raise ValueError("知識ベースに投稿可能なエントリがありません。")

    # リストの最後の要素（最新のエントリ）を取得
    latest_entry = data["knowledge_entries"][-1]

    # 'generated_tweet'キーからツイート文を取得（キーが存在しない場合は空文字）
    tweet_text = latest_entry.get("generated_tweet", "")
    
    if not tweet_text:
        raise ValueError("最新のエントリにツイート文が見つかりませんでした。")
        
    return tweet_text

if __name__ == "__main__":
    # run_tests()
    JSON_FILE_PATH = "../data/knowledge_base/knowledge_entries.json"
    try:
        # 1. 最新のツイート文を取得
        latest_tweet = get_latest_tweet(JSON_FILE_PATH)
        
        # 2. ツイート文を140字以内に調整
        trimmed_tweet = trim_to_140_chars(latest_tweet)
        
        # 3. Xに投稿
        post_to_x(trimmed_tweet)

    except (FileNotFoundError, ValueError, Exception) as e:
        print(f"エラー: {e}")