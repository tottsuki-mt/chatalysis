# Repo Conventions

## コーディング規約
- Python コードは PEP8 準拠とし、`black` を使用して整形してください。
- コメントやコミットメッセージは日本語で記述してください。
- コミットメッセージは Conventional Commits の形式で始めてください。

## ビルド手順
1. Python 3.11 以上を用意します。
2. [uv](https://github.com/astral-sh/uv) をインストールします。
3. 以下のコマンドで依存関係をインストールします。
   ```sh
   uv sync
   ```
4. アプリ起動例:
   ```sh
   uv run streamlit run app.py
   ```
   もしくは
   ```sh
   python main.py
   ```

## テスト実行
- テストを追加した場合は次のコマンドで実行してください。
  ```sh
  pytest
  ```

## PRフォーマット
- PR タイトル: 日本語で簡潔に要約してください。
- PR 本文には以下の項目を記載してください。
  - 変更内容
  - ビルド手順
  - テスト結果
  - その他伝達事項
