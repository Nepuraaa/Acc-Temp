````markdown
<p align="center">
  <img src="images/our_logo.svg" width="360" alt="Acc-Temp Logo" />
</p>

# Acc-Temp（暑熱順化くん）

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)

**Acc-Temp** は、OSHA（米国労働安全衛生局）の **20%ルール** を用いて「**暑熱順化（Heat Acclimatization）**」を計画的・データドリブンに実施／管理するための **Streamlit 製プロトタイプ**です。  
個人ごとの推奨作業割合を算出・可視化し、管理画面からパラメータを編集できます。

---

## 目次

- [背景](#背景)
- [主な機能](#主な機能)
- [技術スタック](#技術スタック)
- [セットアップ](#セットアップ)
- [画面の使い方](#画面の使い方)
- [OSHA 20% ルール（実装仕様）](#osha-20-ルール実装仕様)
- [テスト / 静的解析](#テスト--静的解析)
- [ディレクトリ構成](#ディレクトリ構成)
- [プロトタイプ上の注意点](#プロトタイプ上の注意点)
- [今後の課題（TODO）](#今後の課題todo)
- [ライセンス](#ライセンス)

---

## 背景

- 熱中症は、体温調節機能の破綻や水分・塩分バランスの崩れにより体内に熱が蓄積して発生。
- 漸進的に身体を暑熱環境へ慣らす「暑熱順化」は有効な対策として知られる一方、国内の認知度は十分ではありません。
- 本システムは、暑熱順化を **正しく・安全に・記録を残しながら** 運用することを目的に開発されました。

---

## 主な機能

1. **暑熱順化プラン管理**  
   - 個々の順化進捗に基づき、**推奨作業割合（%）** を自動算出  
   - 欠勤日数に応じた分岐（新規/経験者/再順化）を実装

2. **OSHA 20% ルール適用（パラメータは Admin 画面で変更可能）**  
   - 新規/完全非慣化: 20 → 40 → 60 → 80 → 100%  
   - 3〜6 日欠勤: 50 → 60 → 80 → 100%  
   - 7 日以上欠勤: 新規扱い（20% から再開）  
   - 1〜2 日欠勤: 慣化維持

3. **記録・可視化 UI**  
   - **ダッシュボード**：ユーザ × 日付のヒートマップ（色 + 数値表示）  
   - **ユーザ詳細**：月間カレンダー UI（登録・編集可）  
   - **KPI**：登録ユーザ数 / 本日の出勤・欠勤者数 / 平均実績割合

4. **管理機能**  
   - OSHA パラメータ編集（初期割合 / 増分 / 上限 / 欠勤閾値）  
   - ユーザ管理（追加 / 削除 / ロール変更 / パスワード更新）

---

## 技術スタック

- Python / Streamlit  
- SQLite + SQLModel（SQLAlchemy）  
- Poetry（依存管理）  
- pytest / mypy / flake8 / pre-commit

---

## セットアップ

```bash
# 1) Poetry（未導入なら）
pip install poetry

# 2) 依存インストール
poetry install

# 3) .env 作成
# Windows
copy /Y .env.example .env
# macOS / Linux
cp .env.example .env
````

`.env` 例:

```dotenv
DB_PATH=data/acc_temp.db
ADMIN_PASSWORD=changeme
```

```bash
# 4) DB 初期化
poetry run python scripts/create_tables.py

# 5) ダミーデータ投入
poetry run python scripts/seed.py

# 6) 起動
poetry run streamlit run app/home.py
```

---

## 画面の使い方

### Home（`app/home.py`）

* ロゴ・説明・ **Dashboard / User Detail / Admin** へのリンク

### Login（`app/pages/00_login.py`）

* ユーザ名 / パスワードでログイン
* 管理者（ADMIN）は `.env` の `ADMIN_PASSWORD` を使用

### Dashboard（`app/pages/01_dashboard.py`）

* **ユーザ × 日付のヒートマップ**（色 + 数値）
* KPI（登録ユーザ数 / 本日の出勤・欠勤 / 直近 14 日の平均実績割合）
* 期間 / ユーザフィルタ
* ※「推奨 vs 実績グラフ」は現状不要要件のため非表示

### User Detail（`app/pages/02_user_detail.py`）

* 月間カレンダー UI
* 出欠 / 実績割合 / 対策メモ の登録・編集
* OSHA 20% ルールに基づく推奨割合表示
* 保存後は `st.rerun()` により即時反映

### Admin（`app/pages/99_admin.py`）

* OSHA パラメータ編集（初期割合 / 増分 / 上限 / 欠勤閾値）
* ユーザ管理（追加 / 削除 / ロール変更 / パスワード更新）

---

## OSHA 20% ルール（実装仕様）

* 新規 / 完全非慣化：20 → 40 → 60 → 80 → 100%
* 3〜6 日欠勤復帰：50 → 60 → 80 → 100%
* 7 日以上欠勤：新規扱い
* 1〜2 日欠勤：慣化維持
* 休日・祝日の扱いなど厳密な仕様は今後パラメータ化・整備予定（`services/osha_rule.py` 参照）

---

## テスト / 静的解析

```bash
# ユニットテスト
poetry run pytest -q

# 型チェック（緩め設定）
poetry run mypy .

# コードスタイル（緩め設定）
poetry run flake8 .

# pre-commit
poetry run pre-commit install
poetry run pre-commit run --all-files
```

---

## ディレクトリ構成（抜粋）

```
app/
  home.py
  pages/
    00_login.py
    01_dashboard.py
    02_user_detail.py
    99_admin.py
services/
  dao/
  osha_rule.py
  settings.py
models/
  schema.py
  user.py
scripts/
  create_tables.py
  seed.py
images/
  our_logo.svg
data/
  acc_temp.db
tests/
  test_*.py
```

---

## プロトタイプ上の注意点

* `flake8` の一部ルール（E501/E302/E305/E402 など）を ignore。
* import 崩壊対策として `app/bootstrap.py` で `sys.path` を追加（本番では `src/` レイアウト等で整理推奨）。
* 例外は極力アプリを落とさず **安全側（1.0 返却 など）** に寄せた実装。
* **パスワードは平文保存（開発用）**。本番ではハッシュ化必須。

---

## 今後の課題（TODO）

* パスワードのハッシュ化（`passlib[bcrypt]` など）
* モバイル最適化
* データのエクスポート / インポート
* カレンダー UI の高度化（ドラッグ入力 / 週表示 など）
* 20% ルールの厳密仕様（休日・祝日、連続勤務/欠勤）の詰め
* `src/` レイアウト化・import 周り整理
* flake8 / mypy の厳格化と CI でのブロック

---

## ライセンス

MIT License

```

::contentReference[oaicite:0]{index=0}
```
