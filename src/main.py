# src/main.py
import os
import sys
import json
import random
import re
from datetime import datetime
import time

# --- モジュール検索パスの設定 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# --- 各機能モジュールのインポート ---
from src import from_docx_import_Document, cluster_document, research_topic, x_poster, concept_generator

# --- グローバル設定値 ---
CONCEPT_GENERATION_THRESHOLD = 20 # この投稿数に達したら概念化サイクルを実行

# --- ファイルパス定義 ---
KNOWLEDGE_BASE_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'persona.txt')
KNOWLEDGE_ENTRIES_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'knowledge_entries.json')
HIGH_LEVEL_CONCEPTS_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'high_level_concepts.json')
ACTIVITY_CLUSTERS_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'activity_clusters.json')
SUMMARY_MD_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'concept_summary.md')
ALL_KNOWLEDGE_LOG_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'all_knowledge_log.json')
RECENT_KNOWLEDGE_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'recent_knowledge.json')

def get_current_post_count() -> int:
    """短期記憶（recent_knowledge.json）の投稿数をカウントする"""
    try:
        with open(RECENT_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return len(data.get("knowledge_entries", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def run_normal_cycle():
    print("\n--- 通常サイクルを実行します ---")
    try:
        with open(ACTIVITY_CLUSTERS_PATH, 'r', encoding='utf-8') as f:
            clustered_data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: 活動計画({ACTIVITY_CLUSTERS_PATH})が見つかりません。先に概念化を実行します。")
        run_conceptualize_cycle()
        return
    selected_topic = random.choice(clustered_data["clusters"])
    print(f"調査対象テーマ: {selected_topic['theme']}")
    rich_content = research_topic.generate_rich_content_from_topic(selected_topic)
    tweet_text = rich_content.get("character_post", {}).get("tweet", "")
    print(f"tweet_text: {tweet_text} \n")
    if tweet_text:
        entry = {
            "topic_id": selected_topic.get('cluster_id'),
            "theme": selected_topic.get('theme'),
            "keywords": selected_topic.get('keywords'),
            "created_at": datetime.now().isoformat(),
            **rich_content # 生成されたリッチな情報をすべて結合
        }
        # 長期記憶に追記
        try:
            with open(ALL_KNOWLEDGE_LOG_PATH, 'r', encoding='utf-8') as f:
                all_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_log = {"knowledge_entries": []}
        all_log["knowledge_entries"].append(entry)
        with open(ALL_KNOWLEDGE_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_log, f, ensure_ascii=False, indent=2)
        print(f"長期ログを {ALL_KNOWLEDGE_LOG_PATH} に保存しました。")
        # 短期記憶に追記
        try:
            with open(RECENT_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
                recent_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            recent_log = {"knowledge_entries": []}
        recent_log["knowledge_entries"].append(entry)
        with open(RECENT_KNOWLEDGE_PATH, 'w', encoding='utf-8') as f:
            json.dump(recent_log, f, ensure_ascii=False, indent=2)
        print(f"短期ログを {RECENT_KNOWLEDGE_PATH} に保存しました。")
        print("ツイートを投稿しています...")
        x_poster.post_to_x(tweet_text)
    print("通常サイクル完了。")

def run_conceptualize_cycle():
    print(f"\n--- 概念化サイクルを実行します ---")
    # ステップA: 高次概念の生成と保存
    print("ステップA: 新しい高次概念を生成・保存しています...")
    new_concept_data = concept_generator.generate_new_concept(RECENT_KNOWLEDGE_PATH, SUMMARY_MD_PATH, HIGH_LEVEL_CONCEPTS_PATH)
    if not new_concept_data:
        print("エラー: 高次概念の生成に失敗したため、概念化サイクルを中断します。\nエラーが発生したため、処理を異常終了します。")
        sys.exit(1)
    # ステップB: 全知識の統合と再クラスタリング
    print("ステップB: 新しい活動クラスタを生成しています...")
    knowledge_text = from_docx_import_Document.get_combined_knowledge_text(KNOWLEDGE_BASE_PATH, HIGH_LEVEL_CONCEPTS_PATH)
    new_clusters_json_text = cluster_document.get_clustered_json_from_gemini(knowledge_text)
    json_str = new_clusters_json_text.strip().lstrip("```json").rstrip("```")
    new_clusters_data = json.loads(json_str)
    with open(ACTIVITY_CLUSTERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_clusters_data, f, ensure_ascii=False, indent=2)
    print(f"新しい活動クラスタを {ACTIVITY_CLUSTERS_PATH} に保存しました。")
    print("概念化サイクル完了。")

def run_question_cycle(question: str):
    print(f"\n--- 任意質問サイクルを実行します ---")
    print(f"調査質問: {question}")
    # テーマ・キーワード形式のダミーtopic_dataを作成
    topic_data = {
        'theme': question,
        'keywords': []
    }
    rich_content = research_topic.generate_rich_content_from_topic(topic_data)
    tweet_text = rich_content.get("character_post", {}).get("tweet", "")
    print(f"\n【AIの回答】\n{tweet_text}\n")
    print(f"--- 詳細な調査内容 ---\n{json.dumps(rich_content, ensure_ascii=False, indent=2)}\n")
    # 必要なら知識ログ保存も可能
    entry = {
        "theme": question,
        "created_at": datetime.now().isoformat(),
        **rich_content
    }
    try:
        with open(ALL_KNOWLEDGE_LOG_PATH, 'r', encoding='utf-8') as f:
            all_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_log = {"knowledge_entries": []}
    all_log["knowledge_entries"].append(entry)
    with open(ALL_KNOWLEDGE_LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_log, f, ensure_ascii=False, indent=2)
    print(f"知識ログを {ALL_KNOWLEDGE_LOG_PATH} に保存しました。\n")
    # Xにも投稿
    if tweet_text:
        print("ツイートを投稿しています...")
        x_poster.post_to_x(tweet_text)

def main():
    """このボットのメインコントローラー（1実行1アクションモデル）"""
    print(f"======== ボット処理開始 ({datetime.now()}) ========")

    # --- コマンドライン引数で強制実行・質問を判定 ---
    # 例: python src/main.py --ask "AIとカルマの関係は？"
    force_conceptualize = len(sys.argv) > 1 and sys.argv[1] in ['--force', '--conceptualize']
    ask_mode = len(sys.argv) > 2 and sys.argv[1] == '--ask'
    question = sys.argv[2] if ask_mode else None

    if ask_mode and question:
        run_question_cycle(question)
        print(f"======== 今回の処理は完了しました ({datetime.now()}) ========\n")
        return

    # 1. 現在の記録済み投稿数を取得
    post_count = get_current_post_count()
    print(f"現在の記録済み投稿数: {post_count}")

    # 2. 条件に応じて、どちらか「一つだけ」のサイクルを実行
    if force_conceptualize or post_count >= CONCEPT_GENERATION_THRESHOLD:
        if force_conceptualize:
            print(f">>> [強制実行] 新しいペルソナを反映するため、概念化サイクルを実行します。")
        else:
            print(f">>> 投稿数が閾値({CONCEPT_GENERATION_THRESHOLD})に達しました。")
        
        run_conceptualize_cycle()
        # 概念化後に短期記憶をリセット
        with open(RECENT_KNOWLEDGE_PATH, 'w') as f:
             json.dump({"knowledge_entries": []}, f)
        print("短期記憶（recent_knowledge.json）をリセットしました。")
    else:
        print(">>> 通常サイクルを実行します。")
        run_normal_cycle()
        
    print(f"======== 今回の処理は完了しました ({datetime.now()}) ========\n")

# このファイルが直接実行された時だけmain()を呼び出す
if __name__ == "__main__":
    main()
