# Growth_X_bot(tarma)

## 概要

**Growth_X_bot(tarma)**は、自己成長型のAIエージェント「Growth_X_bot」を中心とした、人工知能による自律的な知識生成・共有システムです。

このプロジェクトは、マズローの人間性心理学に基づいた「自己実現」の概念をAIエージェントとして実装し、継続的な学習と成長を通じて質の高いコンテンツを生成することを目指しています。

## プロジェクト構造

```
├── Growth_X_bot/           # メインのAIエージェントシステム
│   ├── src/               # ソースコード
│   ├── data/              # データファイル
│   ├── test/              # テストコード
│   ├── docs/              # ドキュメント
│   ├── config.py          # 設定ファイル
│   ├── requirements.txt   # 依存関係
│   └── README.md          # Growth_X_bot詳細README

```

## Growth_X_bot(tarma) - 自己成長型X投稿エージェント

### 特徴

- **自己成長ループ**: 活動記録から学び、高次概念を構築し、次の活動計画を自ら更新
- **2段階思考プロセス**: 客観的調査とペルソナ反映による質の高いツイート生成
- **自律稼働**: GitHub Actionsによるサーバーレス実行
- **マズロー理論ベース**: 人間性心理学に基づいた成長モデル

### 主要機能

1. **知識ベースからのテーマ発見**
   - DOCXファイルと過去の学習結果を統合
   - クラスタリングによる活動テーマの自律発見

2. **Web調査と要約**
   - Gemini APIのGoogle Search機能を使用
   - リアルタイム情報収集・分析

3. **自己成長サイクル**
   - **通常サイクル**: 日々のツイート活動
   - **概念化サイクル**: 活動記録の統合・分析
   - **再計画**: 新しい高次概念に基づく活動計画更新

### 技術スタック

- **Python 3.10+**
- **Google Gemini API**: AI生成・Web検索
- **Tweepy**: X（旧Twitter）投稿
- **python-docx**: ドキュメント処理
- **GitHub Actions**: 自動実行

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/AI_Calendar_Assistant2.git
cd AI_Calendar_Assistant2
```

### 2. 仮想環境の作成とアクティベート

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. 依存関係のインストール

```bash
cd Growth_X_bot
pip install -r requirements.txt
```

### 4. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成：

```env
GEMINI_API_KEY="your_gemini_api_key"
X_API_KEY="your_x_api_key"
X_API_SECRET="your_x_api_secret"
X_ACCESS_TOKEN="your_x_access_token"
X_ACCESS_TOKEN_SECRET="your_x_access_token_secret"
```

### 5. 初期データの準備

`Growth_X_bot/data/knowledge_base/`に以下が必要：
- `persona.txt`: AIキャラクターのペルソナ定義
- 初期知識ベース（DOCXファイル）

## 使用方法

### ローカル実行

```bash
cd Growth_X_bot
python src/main.py
```

### 特定の質問への回答

```bash
python src/main.py --ask "AIとカルマの関係は？"
```

### 強制概念化サイクル

```bash
python src/main.py --force
```

### GitHub Actionsでの自動実行

1. リポジトリのSecretsにAPIキーを設定
2. `.github/workflows/`にワークフローファイルを配置
3. スケジュール実行を設定

## アーキテクチャ

### 主要モジュール

- **`main.py`**: メインコントローラー
- **`research_topic.py`**: 2段階調査・ツイート生成
- **`cluster_document.py`**: ドキュメントクラスタリング
- **`concept_generator.py`**: 高次概念生成
- **`x_poster.py`**: X投稿機能
- **`from_docx_import_Document.py`**: ドキュメントインポート

### データフロー

1. **知識ベース統合** → **テーマクラスタリング**
2. **Web調査** → **ペルソナ反映** → **ツイート生成**
3. **活動記録蓄積** → **概念化** → **新計画生成**

## テスト

```bash
cd Growth_X_bot
python -m pytest test/
```

### テスト構造

- **単体テスト**: 各モジュールの機能テスト
- **統合テスト**: エンドツーエンドテスト
- **フィクスチャ**: テストデータ

## 開発・コントリビューション

### 開発環境

1. 仮想環境をアクティベート
2. 開発用依存関係をインストール
3. テストを実行して動作確認

### コントリビューション

1. Issueを作成して問題や改善点を報告
2. ブランチを作成して開発
3. テストを追加・実行
4. プルリクエストを作成

## ライセンス

このプロジェクトは[MIT License](Growth_X_bot/LICENSE)の下で公開されています。

## 関連リンク

- [Growth_X_bot詳細README](Growth_X_bot/README.md)
- [概念モデル図](Growth_X_bot/docs/conceptual_model.png)
- [テスト結果](Growth_X_bot/test/)

## サポート

問題や質問がある場合は、GitHubのIssuesページからお問い合わせください。

---

**注意**: このプロジェクトは研究・開発目的で作成されています。商用利用の際は適切なライセンス確認をお願いします。 