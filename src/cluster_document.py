# src/cluster_document.py
import os
import json
from docx import Document
from google import genai
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def read_text_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"エラー: ファイルが見つかりません - {file_path}")
    if file_path.lower().endswith('.docx'):
        from docx import Document
        try:
            document = Document(file_path)
            full_text = "\n".join([para.text for para in document.paragraphs if para.text.strip()])
            if not full_text:
                print("警告: ドキュメント内にテキストを含む段落が見つかりませんでした。")
            return full_text
        except Exception as e:
            raise IOError(f"docxファイルの読み込み中にエラーが発生しました: {e}")
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"txtファイルの読み込み中にエラーが発生しました: {e}")
    else:
        raise ValueError("対応していないファイル形式です。")

def get_clustered_json_from_gemini(text: str) -> str:
    """与えられたテキストをGemini APIを使ってクラスタリングし、結果をJSON形式の文字列で返す。"""
    api_key = config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("環境変数にGEMINI_API_KEYが設定されていません。")
    client = genai.Client(api_key=api_key)

    # Geminiへの指示をJSON形式での出力を要求するように変更
    prompt = f"""
    以下のテキストを分析し、主要なトピックやテーマで10個のクラスターに分類してください。
    各クラスターについて、テーマ名、要約、キーワードを抽出し、必ず以下のJSON形式で出力してください。

    ```json
    {{
      "clusters": [
        {{
          "cluster_id": 1,
          "theme": "テーマ名1",
          "summary": "要約1",
          "keywords": ["キーワード1", "キーワード2"]
        }},
        {{
          "cluster_id": 2,
          "theme": "テーマ名2",
          "summary": "要約2",
          "keywords": ["キーワード3", "キーワード4"]
        }},
        {{
          "cluster_id": 3,
          "theme": "テーマ名3",
          "summary": "要約3",
          "keywords": ["キーワード5", "キーワード6"]
        }},
        {{
          "cluster_id": 4,
          "theme": "テーマ名4",
          "summary": "要約4",
          "keywords": ["キーワード7", "キーワード8"]
        }},
        {{
          "cluster_id": 5,
          "theme": "テーマ名5",
          "summary": "要約5",
          "keywords": ["キーワード9", "キーワード10"]
        }},
        {{
          "cluster_id": 6,
          "theme": "テーマ名6",
          "summary": "要約6",
          "keywords": ["キーワード11", "キーワード12"]
        }},
        {{
          "cluster_id": 7,
          "theme": "テーマ名7",
          "summary": "要約7",
          "keywords": ["キーワード13", "キーワード14"]
        }},
        {{
          "cluster_id": 8,
          "theme": "テーマ名8",
          "summary": "要約8",
          "keywords": ["キーワード15", "キーワード16"]
        }},
        {{
          "cluster_id": 9,
          "theme": "テーマ名9",
          "summary": "要約9",
          "keywords": ["キーワード17", "キーワード18"]
        }},
        {{
          "cluster_id": 10,
          "theme": "テーマ名10",
          "summary": "要約10",
          "keywords": ["キーワード19", "キーワード20"]
        }}
      ]
    }}
    ```

    --- テキスト本文 ---
    {text}
    """

    print("\nGeminiによるクラスタリングを開始します...")
    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,  # configで指定したモデル名を使用
            contents=prompt,
        )
        return response.text
    except Exception as e:
        raise ConnectionError(f"Gemini APIとの通信中にエラーが発生しました: {e}")

if __name__ == "__main__":
    # 入力ファイルと出力ファイルのパスを定義
    INPUT_DOCX_PATH = "./data/knowledge_base/161217-master-Ryo.docx"
    OUTPUT_JSON_PATH = "./data/clustered_output.json"
    
    try:
        # 1. docxファイルからテキストを抽出
        document_text = read_text_from_docx(INPUT_DOCX_PATH)
        
        if document_text:
            # 2. Geminiでクラスタリングし、JSON形式のテキストを取得
            json_output_text = get_clustered_json_from_gemini(document_text)
            
            # 3. Geminiの出力からJSON部分を抽出
            #    (```json ... ``` のようなマークダウン形式で返されることがあるため)
            json_str = json_output_text.strip().lstrip("```json").rstrip("```")
            
            # 4. JSON文字列をPythonの辞書オブジェクトにパース
            data = json.loads(json_str)

            # 5. 辞書オブジェクトをJSONファイルに保存
            with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                # indent=2 で見やすく整形し、ensure_ascii=False で日本語の文字化けを防ぐ
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\nクラスタリング結果を {OUTPUT_JSON_PATH} に保存しました。")

        else:
            print("テキストが空のため、処理を終了します。")

    except (FileNotFoundError, ValueError, IOError, ConnectionError, json.JSONDecodeError) as e:
        print(f"\nエラーが発生しました: {e}")
