#src/research_topic.py
import re
import json
import random
import os
from datetime import datetime
from google import genai
import sys

# --- モジュール検索パスの設定 ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

# --- 定数定義 ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PERSONA_FILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'knowledge_base', 'persona.txt')
# config.pyにMODEL_NAME = 'gemini-2.5-pro' のように定義されていることを想定
MODEL_NAME = config.MODEL_NAME 


def load_json_file(file_path: str) -> dict:
    """JSONファイルを読み込み、Pythonの辞書として返す。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"エラー: ファイルが見つかりません - {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_gemini_response_to_json(response_text: str) -> dict:
    """Geminiの応答からマークダウン形式のJSONを抽出し、辞書にパースする。"""
    match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if not match:
        raise ValueError("Geminiの応答からJSONデータを抽出できませんでした。")
    return json.loads(match.group(1))

def generate_rich_content_from_topic(topic_data: dict) -> dict:
    """
    指定されたトピックについて2段階の思考プロセスで調査・ツイート生成を行い、
    リッチな情報を含む辞書を返す。
    """
    api_key = config.GEMINI_API_KEY
    client = genai.Client(api_key=api_key)
    
    theme = topic_data.get('theme', '')
    keywords = ", ".join(topic_data.get('keywords', []))
    
    # --- フェーズ1: 客観的な調査と要約 ---
    print("--- [フェーズ1] 調査アシスタントによるWeb調査を開始します... ---")
    
    prompt_phase1 = f"""
    あなたは専門的な調査アシスタントです。
    以下のテーマとキーワードに基づき、Webから信頼できる情報をリアルタイムで検索・収集し、その内容を客観的に要約してください。

    # 調査トピック
    - テーマ: {theme}
    - 関連キーワード: {keywords}

    # 出力形式
    必ず、以下のJSON形式で出力してください。他のテキストは一切含めないでください。
    ```json
    {{
      "overview": "(テーマについての簡潔な説明)",
      "details": "(背景や事例などの詳細な解説)",
      "trends": "(最新の動向や議論)"
    }}
    ```
    """
    try:
        # 【修正点1】調査用のチャットセッションを生成 (ツールを有効化)
        research_chat_session = client.chats.create(
            model=MODEL_NAME,
            config={'tools': [{'google_search': {}}]}
        )
        # 【修正点2】チャットセッションにメッセージを送信
        response_phase1 = research_chat_session.send_message(prompt_phase1)
        research_summary = parse_gemini_response_to_json(response_phase1.text)
        print("--- [フェーズ1] 調査完了。 ---")
    except (Exception, ValueError) as e:
        raise ConnectionError(f"[フェーズ1] Gemini APIとの通信または応答の解析中にエラーが発生しました: {e}")

    # --- フェーズ2: ペルソナの反映とツイート生成 ---
    print("\n--- [フェーズ2] キャラクターペルソナによる反応とツイート生成を開始します... ---")
    
    try:
        with open(PERSONA_FILE_PATH, 'r', encoding='utf-8') as f:
            persona_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"エラー: ペルソナファイルが見つかりません - {PERSONA_FILE_PATH}")
    
    prompt_phase2 = f"""
    あなたは、以下のペルソナを持つAIキャラクター「A-Kカルマ」です。
    あなたの調査チームがまとめた下記の「調査レポート」を読んでください。
    このレポート内容に対して、あなたがどう感じ、どう考えたか、そして最終的にどのようなツイートをするかを、あなたのキャラクターとしてシミュレートしてください。

    # あなたのペルソナ分析:
    {persona_text}

    # 調査レポート:
    {json.dumps(research_summary, ensure_ascii=False, indent=2)}

    # 出力指示:
    あなたの思考過程と最終的なツイートを、必ず以下のJSON形式で出力してください。他のテキストは一切含めないでください。
    ```json
    {{
      "tweet": "（ペルソナに基づいた100字程度のユニークなツイート本文）",
      "thought_process": {{
        "persona_element": "（調査レポートを読んで、あなたのペルソナのどの部分が特に刺激されたか）",
        "reasoning": "（なぜそのように感じ、最終的にそのツイート内容に行き着いたかの思考プロセス）",
        "tone_and_manner": "（A-Kカルマとしての口調や雰囲気。どんな時も必ず丁寧な男性のですます調で話します。冗談や真面目な話題でも一貫して丁寧な語尾を守っています。）"
      }}
    }}
    ```
    """
    try:
        # 【修正点3】ペルソナ反映用の新しいチャットセッションを生成 (ツールは不要)
        character_chat_session = client.chats.create(
            model=MODEL_NAME
        )
        # 【修正点4】チャットセッションにメッセージを送信
        response_phase2 = character_chat_session.send_message(prompt_phase2)
        character_post = parse_gemini_response_to_json(response_phase2.text)
        print("--- [フェーズ2] ツイート生成完了。 ---")
    except (Exception, ValueError) as e:
        raise ConnectionError(f"[フェーズ2] Gemini APIとの通信または応答の解析中にエラーが発生しました: {e}")

    # --- 最終的なリッチな情報を統合して返す ---
    final_result = {
        "research_summary": research_summary,
        "character_post": character_post
    }
    
    return final_result


def save_knowledge_as_json(file_path: str, data_to_add: dict):
    """生成された知識をJSONファイルに追記する。"""
    # (この関数の内容は変更なし)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {"knowledge_entries": []}
    else:
        all_data = {"knowledge_entries": []}
    
    all_data["knowledge_entries"].append(data_to_add)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"知識データを {file_path} に保存しました。")

    
if __name__ == "__main__":
    # (このブロックのロジックは変更なし)
    JSON_FILE_PATH = "./data/clustered_output.json"
    OUTPUT_JSON_PATH = "./data/knowledge_base/knowledge_entries.json"

    try:
        clustered_data = load_json_file(JSON_FILE_PATH)
        
        if clustered_data and "clusters" in clustered_data:
            selected_topic = random.choice(clustered_data["clusters"])
            
            print("--- 調査対象トピック ---")
            print(f"ID: {selected_topic.get('cluster_id')}")
            print(f"テーマ: {selected_topic.get('theme')}")
            print("------------------------\n")

            rich_content = generate_rich_content_from_topic(selected_topic)
            
            print("\n--- 最終生成結果（リッチJSON） ---")
            print(json.dumps(rich_content, ensure_ascii=False, indent=2))
            print("----------------------------------\n")

            tweet_text = rich_content.get("character_post", {}).get("tweet", "")
            if tweet_text:
                print("--- 抽出されたツイート文 ---")
                print(tweet_text)
                print("--------------------------\n")

            knowledge_entry = {
                "topic_id": selected_topic.get('cluster_id'),
                "theme": selected_topic.get('theme'),
                "keywords": selected_topic.get('keywords'),
                "created_at": datetime.now().isoformat(),
                **rich_content
            }
            save_knowledge_as_json(OUTPUT_JSON_PATH, knowledge_entry)
            
    except (FileNotFoundError, ValueError, ConnectionError, json.JSONDecodeError) as e:
        print(f"エラーが発生しました: {e}")