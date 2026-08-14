# KSW プロジェクト固有ルール

KSWデータセンターEOP/SOP（SOPテンプレート）。共通ルールは `../references/common-rules.md`、本ファイルはKSW固有の差分のみ。

## 詳細スキル

同僚のKSWスキル（`ksw-bilingual-docx-translation`）に完全なrulesリファレンスあり。本ファイルは要点。完全な用語集・標準文型・参照欠陥リストは同スキルの `references/ksw-translation-rules.md` を参照。

## テンプレート構造

- SOPテンプレート。文書種別：KSW-EOP / KSW-SOP（電気/機械/HVAC/制御/LOTO/化学物質取扱）。
- ファイル名形式：`KSW-<TYPE>-<NNN> <Title>.docx`。
- 主なセクション：General SOP Information / SOP Background / Reviews Prior to SOP Execution / Supplemental Documentation / SOP Technical Switching Team / PLANNED FIELD SWITCHING PLAN（手順表）/ BACKOUT PLAN OPTIONS / BACKOUT PROCEDURES / Work Complete / Sign Off。
- 手順表の `#` 列は **Part/item 形式**：`A1.` `A2.` `A3.` → `B1.` `B2.`（Partごとにリセット）。

## 翻訳スタイル（KSW固有）

- 非丁寧手順体の終止形：`〜する。` `〜ことを確認する。`。
- **日本語全角句読点**：`、。：（）`。**KIX1の半角カンマ規則を採用しない**。
- タグ・数式・単位・パス・表示ラベルの句読点は不変。
- 日本語文中の英略語の周りに人工スペースを挿入しない。自然KSW形式：`BMSにより` `PPEを着用する`。
- 数値とSI単位の間に1スペース（原文/テンプレが一貫してそうする場合）：`66 kV` `6.6 kV` `40 s` `100,000 L`。
- 挿入日本語本文は `Meiryo UI`（原文/承認KSWテンプレが別フォントを要求しない限り）。**KIX1の10pt本文/見出し設定をKSW文書に押し付けない**。

## 翻訳しない・英語維持（KSW固有）

以下の管理・事前実行セクションとその全フィールドは英語維持：

- `Information on this page should be completed prior to and during the approval process.`
- `Information on this page should be completed just prior to execution.`
- `General SOP Information` の一般管理フィールド（ただし**SOP Name値とActivity Description内容は翻訳**。`SOP Name:`/`Activity Description:`/`SOP No:`/`Revision No & Date:`/`Location of work:` 等のフィールドラベルは英語維持）。
- `Reviews Prior to SOP Execution Date`。
- `Supplemental Documentation` のフォームフィールド。
- `SOP Technical Switching Team`。
- `External Technicians and Support (If needed)`。
- `Reviews Immediately Preceding SOP Execution`。
- `END PLANNED FIELD SWITCHING PLAN` と完全 `BACKOUT PLAN OPTIONS` 表（表タイトル/`#`/`Scenario`/`General backout operations`/`N/A`/表内全内容）。※別の運用 `BACKOUT PROCEDURES` セクションはバイリンガル維持（ユーザー指示がない限り）。
- 赤の作業停止バナー `If unexpected indicator(s) are noted after a step...` で始まる完全ブロック。元の2つの赤英語段落とコンパクト行レイアウトを保持。日本語段落を追加しない。
- Document Control / Annual Review セクション。
- 最終完了/サインオフフォーム：`Work Complete / Sign Off` 見出しはバイリンガルだが、残りのフォームラベル/サインオフ欄/アーカイブ指示/日付/時刻/`Document turned into:` 欄は英語維持。
- 編集上のスクリーンショット挿入プレースホルダ `[Insert PME Screenshot ...]`/`[Insert ECMS Screenshot ...]` 等のかぎ括弧生成注記。日本語版を追加しない。フラグは完全英語指示＋日本語訳の後に配置。※スクリーンショット取得/記録する実際の操作指示は翻訳対象。

## 標準用語（KSW固有・KIX1と対立する点に注意）

KIX1と対立する主要項目：

| 項目 | KSW | KIX1（混入厳禁） |
|---|---|---|
| カンマ | 全角 `、` | 半角 `,` |
| 主任電気技術者 | **自動訳禁止**（`第二種主任電気技術者` はKSW任命/原文/プロジェクト記録で資格・役職確認時のみ） | `第二種主任電気技術者` 固定訳 |

KSW核心用語の抜粋（完全版は同僚スキル `references/ksw-translation-rules.md` Section 5）：

| English | Japanese | 備考 |
|---|---|---|
| utility power | 商用電源 | TEPCO供給 |
| utility power outage | 商用電源停電 | 完全外部供給停止 |
| utility power loss | 商用電源喪失 | トリップ/局所事象による |
| incoming supply | 受電電源 / 受電系統 | 文脈で選択 |
| main line | 本線 | |
| standby/spare line | 予備線 | 英語が交代しても1用語 |
| power restoration | 電源復旧 | |
| isolation | 電源隔離 / 隔離 / 切り離し | 運用範囲で選択。停止が別SOPで完了後の電源分離は `電源隔離`。`停止` を追加しない（現SOP自体が停止を実施しない限り） |
| maintenance | 保守 | 正式技術SOPの既定。公式名/固定ラベル/HMI選択/確定サイト用語の場合のみ `Maintenance`/`メンテナンス` |
| switchgear | 開閉装置 | 特定個別機器/位置の確立資産名の場合のみ `開閉器` |
| circuit breaker | 遮断器 | |
| VCB | VCB（真空遮断器） | 初回展開のみ有用な場合 |
| ACB | ACB（気中遮断器） | 初回展開のみ有用な場合 |
| isolator / disconnector | 断路器 | |
| three-position disconnector | ３点断路器 | 仮称。OEM/銘板用語が異なれば置換 |
| breaker trip | 遮断器トリップ | |
| open (breaker state) | 開放 | `開路` より優先（リテラル盤ラベルが別の場合を除く） |
| close (breaker state) | 投入 | `閉路` より優先 |
| energized | 充電状態 / 受電状態 | 機器か受電源かで選択 |
| de-energized / zero voltage | 無電圧 | |
| voltage detector | 検電器 | `電圧検出器` より優先（携帯工具の場合） |
| active alarm | 発報中アラーム | |
| clear an alarm | アラームをクリアする | システム動作。期待結果は `アラームがクリアされる` |
| generator start failure | 発電機始動失敗 | `起動失敗` は該当機器規格が「起動」を使用する場合のみ |
| hot standby | ホットスタンバイ | 技術的に正しい場合 `（無負荷運転）` 追加可 |
| load staging | 負荷の段階制御 | |
| back-out plan/procedure | バックアウト計画／バックアウト手順 | 根本原因調査と訳さない |
| pre-job brief | 作業前ブリーフィング | |
| PPE | PPE（個人用保護具） | 初回展開可 |
| LOTO | LOTO（ロックアウト・タグアウト） | 初回展開可、以降 `LOTO` |
| chiller | チラー | |
| CRAH | CRAH | 展開しない（読者/テンプレ要求がない限り） |
| setpoint | 設定値 | |
| chemical dosing system | 薬注システム | |
| chlorine dosing tank | 塩素薬注タンク | 実際の薬剤/資産名を確認 |
| leakage | 漏えい | 管理安全言語として `漏えい` 優先 |

## KSW固有の提示規則

- 見出し：`English heading / 日本語見出し`（全角スラッシュ `／` は用いず `/`）。
- 各 `#` セルは **Part/item形式**（`A1.` `A2.`、Partごとリセット）。原文の自動Wordナンバリングが既に正しいPart/item形式を生成する場合、それを優先：typed識別子テキストを全削除、`w:numPr` 保持、番号付き段落と該当 `numbering.xml` レベルを **通常（非太字）Meiryo UI 9pt** に設定。自動ナンバリングがない/信頼できない場合のみ明示的typed識別子を使用（その場合 `w:numPr` 削除）。**自動番号とtyped識別子を同一セルで併存させない**。`#D11–#D13` 等のクロスリファレンスは末尾ピリオドなし。
- 長い手順表はインライン化（`w:tblpPr`/`w:tblOverlap` 削除）。各Partが1回・全ステップIDが一意か確認。
- Activity Descriptionは完全英語ブロック→完全日本語ブロック。2言語をインターリーブしない。
- 写真付きステップ：英語指示→日本語訳→写真（元セル内、`wp:inline`）。表と写真両方ある場合は両言語ブロック後、元の相対順序で。
- 多分岐ステップ：`下線バイリンガル分岐見出し → 英語アクション → 日本語アクション` を各分岐で反復。`A系保守時：` 等の条件接頭辞は通常反復しない（真の曖昧性回避/確定参照意図の場合を除く）。全英語分岐を先に集めて日本語を下部にまとめない。
- target-equipment selectionセル（`Circle`/`Mark`/`Tick the target equipment / system`）は**保護原文データ**。当該SOP原文から完全セル構造をコピーし日本語指示のみ挿入。見出し/チェックボックス/機器名/資産タグ/順序/綴り/空白/ネスト表構造を保持。前SOPからコピーしない。
- Field Comments・notes・expected outcomes・サイドセルの操作内容を翻訳（除外がない限り）。
- フローチャートの**全意味ラベル**（箱外テキスト/分岐ラベル/経路キャプション/コネクタ注釈/凡例含む）を翻訳。日本語は対応英語の直下。
- 色強調保持（部分着色含む）。
- 手順ステップ段落は **1.0行間隔・前後0pt**。
- 通常操作アクションは明示的左揃え。中心はPart見出し/警告バナー/表ヘッダ等の明示的中心要素のみ。

## KSW固有の標準文型

| 機能 | パターン |
|---|---|
| Confirm/Check | `～ことを確認する。` |
| Record | `～を記録する。` |
| Record screenshot | `～のスクリーンショットを取得し、記録する。` |
| Report | `～へ報告する。` |
| Contact | `～へ連絡する。` |
| Instruct | `～するよう指示する。` |
| Monitor | `～を監視する。` |
| Open/Close panel | `パネルを開ける。／パネルを閉じる。` |
| Open breaker/isolator | `遮断器／断路器を開放する。` |
| Close breaker/isolator | `遮断器／断路器を投入する。` |
| Switch A→B | `～をAからBへ切り替える。` |
| Refer to | `～を参照する。` |
| Prohibit | `～を実施しないこと。` または `～を禁止する。` |
| Mandatory | `～しなければならない。` または（チェックリスト）`～すること。` |
| NOTE | `注記` または行タイプが固定なら `NOTE` 保持。文書内で交代させない。Location/type列に既に `NOTE`/`#NOTE` がある場合、日本語アクションに冗長な `注記：` を接頭しない。 |
| Warning | `⚠ ～の場合は、…する。` |
| Stop-work | `作業を直ちに停止し、CFMへ連絡する。` |
| Expected auto response | `～が投入される。` `～アラームがクリアされること。`（客観形） |

`確認する` を `チェックする`/`確認を行う` と交代させない（「チェックボックスにチェックを付ける」の字義場合を除く）。

## 参照SOP（KSW権威シリーズ）

- KSW-EOP-101/102/105/106/107、KSW-SOP-102/107 R13,R14/110 REV9/111 REV4/113/114/115/116/117/202/203/208/209/210。
- 各SOPフォルダの**最新ユーザー編集バイリンガルファイルを最高優先**の提示プレセデントとする。
- SOP-107 R13：状況分岐/直接英日ペア/スクリーンショットフラグ/インライン複数ページ手順表の支配的プレセデント。
- SOP-111 REV4：自動Part/itemナンバリングと中心揃え線形バイリンガルフローチャートの検証済み参照。

## 既知の参照欠陥（伝播させない）

完全リストは同僚スキル `references/ksw-translation-rules.md` Section 8。主なもの：

- `ramp`/`lamp` 誤記 → `ランプ` は原文誤記確認後のみ。
- `switchgear` の `開閉装置`/`開閉器` 混在 → 組立品と個別機器を区別。
- 遮断器操作の `開路／閉路` と `開放／投入` 交代 → 叙述は `開放／投入` に標準化。
- KSW-SOP-102：バックアウト手順を根本原因調査と誤訳（必須応答を変える）→ プレセデントとして使用しない。
- KSW-EOP-202：BMSベンダーエスカレーション注の視覚的に切り詰められた/破損した日本語文 → 翻訳メモリとして再使用しない。
- KSW-SOP-208 Step C33：日本語訳なしの英語タッチパネル指示 → 完全性チェックで英語のみの手順セルを検出すべき。
- KSW-SOP-209：`≤3°C` と `<3℃` の不一致 → 不等号と閾値は調整要の技術データ。
- `盤`/`パネル`/`盤の扉`/`パネルドア` の交代 → 実際の機器名称を使用し、同一手順内の同一対象は1用語に統一。
- KSW-SOP-306：フローチャート画像（`Flowchart:`セル）が英語のみで未翻訳のまま残っている → プレセデントとして使用せず、新規SOPでは必ずバイリンガル再作成する（上記「フローチャート画像バイリンガル再作成」参照）。

## 03→04ワークフローと実装パターン（SOP-306/309検証）

各KSW SOPのドラフト構造：`01 First Draft` → `02 First Draft Comments` → `03 Second Draft`（翻訳ベース）→ `04 Bilingual Procedure`（出力）。

- `04`は`03 Second Draft`から作成（`01`/`02`不可）。`02`コメントは`03`に取り込み済み。
- `04`フォルダ構造は参照SOP（SOP-306等）を踏襲：`00. Archive/`、`01. Reference drawings and documents/`、`02. Reference screenshots and photos/`、＋bilingual docx。参照PDF/写真は`03`から`04`へコピー。
- `03`投下→`04`完成をワンパスで：構造監査→インベントリ→翻訳→挿入→QA。

文書保持XML挿入（SOP-309検証）:

- **別段落形式**（SOP-306プレセデント）：英語段落の直後に、`deepcopy`した日本語段落（先頭runフォーマット・テキスト差替）を挿入。1ステップ内は完全英ブロック→完全日ブロック。
- **日本語内の`\n`は`w:br`に分割**（`w:t`内リテラル`\n`はWordで改行されない）。
- **下線内部見出し・Part見出し**：同段落に` / 日本語`を末尾runフォーマットで追記（下線・色維持）。第2の訳見出し段落を追加しない。
- **保護データは英語維持**：target-equipmentチェックボックス行（`□FP-1`等、指示段落のみ翻訳）、`[Attach Photo]`/`[Insert … Screenshot]`フラグ、写真（`wp:inline`）、赤stop-workバナー、`END PLANNED FIELD SWITCHING PLAN`、`BACKOUT PLAN OPTIONS`表全体、管理/事前実行セクション、Document Control。
- **フローチャート**：`Flowchart:`見出しのインライン` / フローチャート:`化に加え、**ラスター画像自体のバイリンガル再作成が必須**（Rule 34／全意味ラベル翻訳）。参照プレセデント（SOP-306等）がフローチャート英語のみでも踏襲せず、必ず英日バイリンガル画像を生成して差し替える。再作成は後述「フローチャート画像バイリンガル再作成」の手順に従う。これを「レビュー課題」に回さないこと。
- **ヘルパー**：`insert_jp_after(en_p, jp)`（段落クローン・run再構成・`w:br`分割挿入）、`append_inline(p, jp)`（見出し末尾に` / 日`追記）、`replace_text(p, text)`（見出し正規化）。挿入は段落インデックスではなく**要素参照**で（挿入で後続インデックスがずれるため）。`deepcopy`が`pPr`/`numPr`を保つので自動Part/itemナンバリングとリストレベルは保持される。
- **QA 3ゲート**：(1) `audit_docx.py SOURCE BILINGUAL` — tables/inline_shapes/media/自動番号セル/package_parts/クライアント名候補が原文と完全一致、上昇するのは`table_paragraphs`と`japanese_paragraphs`のみ。(2) 全手順セルの英日ペアダンプで、各英語アクションに日本語ペアがあるか・保護データ未処理・英語維持セクション維持を確認。(3) Word COM（`Documents.Open`（`OpenAndRepair=False`）＋`SaveAs` PDF）で再保存し、修復ダイアログ/例外が出ないことを確認。修復報告があればそのリビジョン破棄→`03`から再ビルド。

### 書式正規化（必須・ビルド直後）

挿入日本語ランは元英語ランの `rPr` を `deepcopy` で継承するため、フォント（宋体/メイリオ/Calibri混入）・太字（本文なのに太字）・サイズ（`w:sz val=220` = 110pt 等）が元ラン任せで破綻する。**全挿入完了後、納品前に必ず以下を実行**（べき等・再実行安全）：

```bash
# 本文フォントMeiryo UI・本文非太字・見出し（" / "区切り）太字維持・破損サイズ修正
python scripts/normalize_format.py "04 Bilingual Procedure/KSW-SOP-XXX.docx"
# 違反1件でもFAIL（exit 1）。0違反で合格
python scripts/audit_format.py  "04 Bilingual Procedure/KSW-SOP-XXX.docx"
```

`audit_format.py` が FAIL なら納品不可。`w:sz` は半ポイント（`val=18`→9pt、`val=22`→11pt）。`val>36` は機械的に異常扱い。本文は9pt（`val=18`）。

**部分色強調の継承（SOP-309事故対応・必須）**：原文ENに部分着色（赤のSOP参照 `EE0000`、緑のHMIパス `ECMS > Alarms` 等）がある場合、`deepcopy` 挿入JPは `runs[0]` の色しか継承せず色強調が落ちる。正規化後に `scripts/inherit_color_emphasis.py FILE.docx` を実行し、EN着色リテラル（SOP参照・HMIパス等の原文まま文字列）をJP内で同色（＋太字）に分割着色する。実行後は `audit_format.py`（色付き太字ランは正当な強調として許可）で再検証。

### フローチャート画像バイリンガル再作成（必須・SOP-309検証）

ラスター（画像）フローチャートは、画像内の全意味ラベルを英日で再描画し、同じパスの画像を差し替える。手順：

1. **原文画像を特定**：`document.xml`の`r:embed`出現順と`document.xml.rels`で、`Flowchart:`セル内の画像がどの`word/media/imageN.*`か決定（SOP-309では`rId13`→`image2.png`）。
2. **ラベル抽出**：画像の意味テキスト（ボックス内・分岐・キャプション・箱外）を全て書き出し（必要なら`analyze_image`等のOCR/視覚読取で）。
3. **配色・サイズ取得**：`Pillow`で元画像の`size`と`getcolors`上位色（背景・ボックス色・テキスト色）を抽出。SOP-309例：白背景・紫`(112,48,160)`・緑`(84,130,53)`・濃紺テキスト`(34,63,89)`、399×1053。
4. **同サイズで再描画**：元の縦横比・サイズを維持（`wp:extent`調整不要にするため）。工程区分ごとに元配色を再現（準備=薄紫・実行=薄緑 等）。各ボックスに英語（上）＋日本語（下）を `Meiryo`（`C:/Windows/Fonts/meiryo.ttc`）で中央寄せ。`\n`は`w:br`相当の改行で処理。ボックス間は元の矢印スタイル（下向き線＋三角等）で接続。**配色の落とし穴（SOP-309事故）**：`getcolors`で取得した原本の**飽和色をそのまま塗りに使う**。淡いパステル（`(243,235,248)` 等）に変換しない。原文が飽和色背景＋白文字なら再作成も同じ（白文字`(255,255,255)`on飽和色）。文字色を濃紺等に変えない。矢印色も原本からサンプリング（例：濃紺`(64,76,91)`）。箱の角丸半径も原本に合わせる（原本が直角〜radius≈3なら同じ）。
5. **画像差し替え**：`zipfile`でdocxを開き、該当`word/media/imageN.*`を新画像のバイト列で置換して再圧縮。ファイル名・パス・リレーションはそのまま（参照先変更不要）。
6. **QA**：差し替え後 `audit_docx.py`（`inline_shapes`/`media_parts`/`tables`が原文と同一・`zip_integrity:True`）、画像の視覚読取で全ボックス英日表示・切抜き/重複なしを確認、Word COM再保存で修復ダイアログなしを確認。**OCR検証必須**：再作成画像を `easyocr`（`pip install easyocr`）等で読み取り、全ボックスの英日テキストが欠損・切抜きなく描画されていることを確認する（目視・類推に頼らない）。フローチャート画像テキストの正確抽出に外部ビジョンAPIが使えない場合はOCRで代用。

**注意**：
- `wp:extent`（表示サイズEMU）を変えずに済むよう、元画像と同じ縦横比・サイズで再描画する。サイズを変える場合は `document.xml` の該当 `wp:extent` の `cx`/`cy` も同率で調整すること。
- 参照プレセデントがフローチャート英語のみ（SOP-306等）でも、それを「英語維持」の根拠にしない。必ず再作成する。
