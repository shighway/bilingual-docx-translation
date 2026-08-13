# KIX1 プロジェクト固有ルール

KIX1データセンターEOP（VDCテンプレート）。共通ルールは `../references/common-rules.md`、本ファイルはKIX1固有の差分のみ。

## 詳細スキル

`eop-translation`（`~/.agents/skills/eop-translation/`）にツールと実績あり。本ファイルは要点。完全なワークフロー・注入パターン・用語集は同スキルの `SKILL.md` と `rules/` を参照。

## テンプレート構造

- VDCテンプレート。文書種別：BLDG-EOP / FIRE-EOP / MVAC-EOP / VDC-KIX1-EOP。
- ファイル名形式：`KIX1 <TYPE>-EOP-<NNN>- <Title>.docx`。
- 出力：`<同>_JP_EN.docx`。
- 主なセクション：Description of Work / Important Criteria / Control & Action Symbols / Pre-condition / Emergency Procedure（Required Action / Expected Outcome 列） / Verification Procedure / Back-out Procedures / EOP Flow Chart。

## 翻訳スタイル（KIX1固有）

- **だ・である調**（手順体、丁寧語なし）。
- カンマ = **半角 `,`**（`、` を使わない）。
- 括弧 = **全角 `（）`**。
- スラッシュ = **全角 `／`**。
- 中点 = `・`。
- 数字 = 半角。
- 日本語文中の英数字の両側に**半角スペース**：「第二種主任電気技術者 の指揮」「BMS により」。

## 翻訳しない（KIX1固有）

- Location/Equipment列値：NOC/SOC/FOC/CFM/SITE/DB Panel/Pump Room/RH FLOOR/DOMESTIC COLD WATER PLANT 等。
- 略語：BMS/BAMS/CFM/FOC/PPE/LOTO/PTW/SLD/CMS/IOA/NetSuite/Teams。
- Document Control表（日付・版・署名）。
- Annual Review日付。
- BAMS画面パス（`BAMS > Alarm > Alarm List page` 等）。

## 標準用語（KIX1固定訳）

| English | Japanese |
|---|---|
| Description of Work | 作業内容（手順）/ 作業概要（概要） |
| Important Criteria | 重要事項 |
| Control and Action Symbols | 管理・操作記号 |
| Emergency Procedure | 緊急対応手順 |
| Pre-condition | 前提条件 |
| Verification Procedure | 確認手順 |
| Back-out Procedures | 切戻し手順 |
| EOP Flow Chart | EOPフロー図 |
| Handling Procedure | 取扱手順 |
| Document Control | 文書管理 |
| Chief Electrical Engineer | 第二種主任電気技術者 |
| Life Safety Step | 生命安全ステップ |
| Rollback from this point, if required | 必要に応じてこの時点から切戻し |
| Critical Step | 重要ステップ |
| Change of State | 状態変更 |
| Two Person Verification Rule (TPVR) | 2名確認ルール（TPVR） |
| Stop, Confirm, Escalate, Go/No go | 停止・確認・エスカレーション・実施可否判断 |
| Important Note | 重要事項 |
| Record required details (V, TH etc.) | 必要事項（V、TH等）を記録 |
| Open Position | 開位置 |
| Closed Position | 閉位置 |
| Lock Out / Tag Out | ロックアウト／タグアウト |
| Un-lock / Tag Off | ロック解除／タグ取り外し |

電気・火災・HVAC・水系統の完全用語集は `eop-translation/rules/03-glossary-and-style.md`。

## KIX1固有ワークフロー要素

### 空Expected Outcomeセルの自動補完（109パターン・KIX1固有）

Emergency Procedure / Verification / Back-out 表でExpected Outcome列が空の行は**自動補完**（109_JP_EN.docxの実績パターン）：

- 受動態完了状態を記述：「X is recorded」「Y is confirmed」「Z is ensured」。
- Required Action「Record the alarm」→ Expected Outcome「The alarm is recorded. / アラームが記録される。」
- 英語・日本語両方を新段落で追加。
- 段落フォーマット：`ind left=0` `sz=18`（9pt）。既存Expected Outcome段落に厳密一致。
- 実装：Required Action `w:tc` → 親 `w:tr` → 次 `w:tc`（Expected Outcomeセル）→ 英語段落→日本語段落の順で `append_to`。

参考：`eop-translation/examples/outputs/602_JP_EN.docx`（16行補完）、`603_JP_EN.docx`（23行補完）。

### インデント統一（KIX1固有・必須）

Expected Outcomeセル補完後、Expected Outcome列の `w:ind w:left` をRequired Action列と一致させる。不一致だとWord上で「不揃いな上余白」として視認される。

- Required Action列（C2）の支配的 `ind left` 値を検出。
- Expected Outcome列（C3）全段落を同値に設定。
- C2自体が行間で不整合ならC2/C3両方を文書全体の支配値に統一。

### JSON中間ファイル方式（KIX1固有）

KIX1は JSON翻訳マップ を経由するツール駆動：

1. `extract_translations.py input.docx analysis.json` で構造抽出。
2. `{ID}.json` を作成（`titles`/`section_headings`/`list_items`/`cell_texts`）。
3. `inject_ja.py input.docx output_JP_EN.docx {ID}.json` で注入。
4. `inject_diagram_ja.py` でフローチャート注入。

参考：`eop-translation/examples/translations/602.json`。

## 注入パターン（KIX1検証済み）

| 要素 | パターン |
|---|---|
| セクションタイトル | 見出し段落末尾に ` / ＜和訳＞` を新 `<w:r>` で追加 |
| Important Criteriaリスト項目 | EN段落後に新 `<w:p>`（pPr複製） |
| Control & Action Symbolsセル | セル内EN段落後に新 `<w:p>` |
| Required Action/Expected Outcome | 同上 |
| Description of Work散文 | 各EN段落後に新 `<w:p>` |
| SmartArtフローチャート | EN `</a:p>` 後に新 `<a:p>`（改行強制） |

日本語段落テンプレ（F6参照）：
```xml
<w:p>{cloned_pPr}<w:r><w:rPr>
  <w:rFonts w:eastAsia="Meiryo UI" w:cstheme="minorHAnsi"/>
  <w:sz w:val="20"/><w:szCs w:val="20"/>
</w:rPr><w:t xml:space="preserve">日本語訳</w:t></w:r></w:p>
```

見出しは `Yu Gothic` をeastAsiaに使用（Heading2スタイルがYu Gothicを使用）。

## 参照ペア（金標準）

- `eop-translation/references/109_EN↔JP_EN.docx`
- `eop-translation/references/202_EN↔JP_EN.docx`
- `eop-translation/references/306_EN↔JP_EN.docx`

## docx編集原則（KIX1固有）

- `.docx` はXMLのZIP。**`word/document.xml`（本文）と `word/diagrams/data1.xml`（フローチャート）のみ編集**。他パーツ（メディア/スタイル/テーマ/ヘッダ/フッタ）はバイト単位で同一保持。
- **スクラッチ再構築厳禁**。SmartArt/画像/VDCカスタムスタイル/ヘッダフッタは再生成不可。常に既存ファイルを編集。
