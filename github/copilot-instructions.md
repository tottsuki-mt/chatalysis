# 開発・依存関係管理について

このプロジェクトでは Python の依存関係管理・インストールに [uv](https://github.com/astral-sh/uv) を使用します。
GitHub への操作は [GitHub CLI](https://cli.github.com/) を使用します。

## 依存関係のインストール

requirements.txt を利用している場合:

```sh
uv pip install -r requirements.txt
```

pyproject.toml を利用している場合:

```sh
uv sync
```

## コミットメッセージの書き方

コミットメッセージは以下の指示に従って記述してください。

- 必ず日本語で記述してください。
- コミットメッセージは、最初にConventional Commitsに則って記述してください。
- その後、ファイルごとの詳細な変更内容を記述してください。

## GitHub へのアクセスについて
GitHub への操作（リポジトリのクローン、Issue/PR の作成・管理等）は [GitHub CLI](https://cli.github.com/) のコマンド（gh）を使用してください。
