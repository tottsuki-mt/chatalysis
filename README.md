# Chat Data Analyst (Streamlit + LangChain)

## 概要

アップロードしたCSV/Excel/JSONデータに対し、自然言語で集計・可視化を行うデータ分析チャットアプリです。

- Streamlit + LangChain による対話型データ分析
- pandas/matplotlib/seaborn/plotly による可視化
- OllamaサーバーやOpenAI APIキーに対応
- サンプルデータ（`data/` 配下）付き
- 音声入力対応（マイクからの音声で質問可能）

## セットアップ

1. Python 3.11 以上を用意してください。
2. [uv](https://github.com/astral-sh/uv) をインストールしてください。
3. 依存関係をインストールします。

```sh
uv sync
```

4. Ollamaサーバーを起動してください。
   - 例: `set OLLAMA_BASE_URL=...`

## 起動方法

```sh
uv run streamlit run app.py
```
または
```sh
python main.py
```

## 使い方

1. Webブラウザで表示される画面からデータファイル（CSV, Excel, JSON）をアップロードします。
2. チャット欄に日本語で質問や集計・可視化指示を入力します。
   - 例: 「月別売上を折れ線グラフで」「平均年齢は？」など
3. マイクボタンを押すことで音声入力も可能です（音声がテキストに変換されて入力欄に反映されます）。
4. LLMが自動でPythonコードを生成・実行し、結果やグラフを表示します。

## 注意事項

- `ALLOW_DANGEROUS_CODE=true` を設定すると、LLMが生成したPythonコードを自動実行します。安全性にご注意ください。
- 本番利用時はサンドボックス化や自動実行の無効化を推奨します。

## 依存パッケージ

主要な依存パッケージは `pyproject.toml` で管理しています。
- streamlit
- pandas
- langchain
- langchain-experimental
- matplotlib
- seaborn
- plotly
- python-dotenv

## サンプルデータ

- `data/titanic.csv` など、いくつかのサンプルデータが同梱されています。

## 開発・依存関係管理

- 依存関係管理・インストールには [uv](https://github.com/astral-sh/uv) を推奨します。
- 詳細は `github/copilot-instructions.md` も参照してください。

## テスト

現時点では自動テストは含まれていません。テストを追加した場合は次のコマンドで実行
します。

```sh
pytest
```
