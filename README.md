# bilingual-docx-translation

データセンターEOP/SOPのWord文書を、プロジェクト別フォーマットと翻訳ルールに従ってバイリンガル（EN→EN+JP）化するスキル。英語原文を保持したまま日本語を挿入し、書式・図・SmartArt・ヘッダ/フッタを保持。docx XMLを直接編集し、再構築しない。

## 特徴

- **プロジェクト別フォーマット管理**：KIX1/KSW/STACK等のプロジェクト固有フォーマットと翻訳ルールを `projects/` で別管理。プロジェクト間で対立する規則（句読点・主任技術者訳・空Expected Outcomeの扱い等）の混入を防止。
- **共通基盤**：全プロジェクト共通の運用ルール・QA手順を `references/common-rules.md` に集約。Word修復ファイルの扱い、idempotency、クライアント名の中和、参照階層等。
- **読み取り専用QAスクリプト**：構造監査と機器リスト照合を自動化。

## ディレクトリ構成

```
bilingual-docx-translation/
├── SKILL.md                       共通ワークフロー＋プロジェクト識別
├── README.md                      本ファイル
├── references/
│   └── common-rules.md            共通運用ルール・QA手順
├── projects/
│   ├── README.md                  プロジェクト別管理の手順・対立規則一覧
│   ├── kix1.md                    KIX1固有（VDCテンプレ・半角カンマ・第二種主任固定訳）
│   ├── ksw.md                     KSW固有（SOPテンプレ・全角句読点・Part/itemナンバリング）
│   └── stack.md                   STACK固有（原文待ちプレースホルダ）
├── scripts/
│   ├── audit_docx.py              読み取り専用 構造監査
│   └── audit_equipment_lists.py   読み取り専用 機器リスト照合
└── agents/
    └── openai.yaml                エージェントインターフェース定義
```

## 対応プロジェクト

| プロジェクト | テンプレート | 状態 |
|---|---|---|
| KIX1 | VDC（EOP中心） | 実績あり。`eop-translation`スキルと連携 |
| KSW | SOP（EOP/SOP両方） | 同僚スキル準拠 |
| STACK | （原文待ち） | 原文受領後に `projects/stack.md` へ判読・記録 |

## 依存

Python 3.10+ および以下のパッケージ：

```bash
pip install python-docx lxml
```

## スクリプト使い方

### 構造監査

```bash
python scripts/audit_docx.py SOURCE.docx OUTPUT_JP_EN.docx
```

ZIP整合性、パッケージパーツ数、メディア/図パーツ数、表・インラインシェイプ数、自動番号セル、自動+typed競合、ステップID、ナンバリングモード、クライアント名候補を報告。

**クライアント名検出の設定**：`scripts/audit_docx.py` の `CLIENT_NAME_RE` に既知のクライアント企業名（現在 `Microsoft`/`Google`）を設定済み。別プロジェクトで異なるクライアント名を検出する場合は正規表現を追加。

### 機器リスト照合

```bash
python scripts/audit_equipment_lists.py SOURCE.docx BILINGUAL.docx
```

target-equipment selectionセル（`Circle`/`Mark`/`Tick the target equipment`）を原文と出力で照合。不一致は exit 1（必須FAIL）。該当ステップがない場合は not-applicable で exit 0。

## 新プロジェクト追加手順

1. 原文DOCXとテンプレート参照を入手。
2. 原文を判読し、以下を抽出：テンプレート構造、句読点規則、用語集、英語維持セクション、ナンバリング方式、固有の注意事項。
3. `projects/<project>.md` を作成。`projects/stack.md` をテンプレートとして使用可。
4. `projects/README.md` のプロジェクト間対立表を更新。
5. KIX1/KSWと対立する規則（句読点・主任技術者訳等）を明記し混入を防止。

## プロジェクト間で対立する規則（混入厳禁）

| 項目 | KIX1 | KSW | STACK |
|---|---|---|---|
| カンマ | 半角 `,` | 全角 `、` | （判読後記入） |
| 括弧 | 全角 `（）／・` | 全角 `、。：（）` | |
| 主任電気技術者 | 第二種主任電気技術者（固定訳） | 自動訳禁止・要確認 | |
| テンプレート | VDC（EOP中心） | SOP（EOP/SOP両方） | |
| ナンバリング | 手順表の行ベース | Part/item `A1.` `A2.` | |
| 空Expected Outcome | 109パターンで自動補完 | 自動補完せずレビューに回す | |

## 運用元スキル

- KIX1：`eop-translation`スキル（ツール・実績ペア・完全用語集を保持）
- KSW：同僚の `ksw-bilingual-docx-translation`スキル（完全ルールリファレンス・標準文型・参照欠陥リストを保持）

本スキルは両者の共通要素を抽象化した汎用基盤。固有要素の完全版は各運用元スキルを参照。
