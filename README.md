# Gadget Entangle for Cascadeur / Blender (GECB)

Gadget Entangle for Cascadeur / Blender (GECB) is a free real-time synchronization tool designed to connect Cascadeur and Blender.

GECB allows Cascadeur character animation to be previewed directly inside Blender in real time.

---

## Main Features

1. Real-time synchronization between Cascadeur and Blender.
2. Synchronization works regardless of Blender's Object Mode or Pose Mode.
3. Synchronization can also work while Blender's timeline animation is playing, as long as the target bones are not controlled by keyframes.
4. Up to 4 characters can be synchronized at the same time, depending on your PC performance.
5. Zero Calibration is used to align the character state between Cascadeur and Blender.
6. Zero Calibration data can be saved and reused.

---

## System Requirements

- Windows only  
  GECB uses Windows API internally.

- Tested versions  
  - Cascadeur 2026.1.3  
  - Blender 5.1

- Tested PC environment  
  - GPU: NVIDIA RTX 3060 12GB  
  - CPU: AMD Ryzen 7 8-Core  
  - RAM: 32GB

- Cascadeur License  
  GECB requires a valid paid Cascadeur license.  
  The free version of Cascadeur is not supported.

---

## Character Requirements

GECB is designed for characters that follow a CC-compatible bone hierarchy and naming convention.

Please refer to the sample character for the expected bone structure and bone naming rules.

### Important Notes

- Bone hierarchy must match the expected structure.
- Bone orientation must be consistent.
- Bone naming must follow the supported naming convention.

GECB synchronizes raw skeletal bones directly.  
It is not a universal rig conversion tool.

### Why GECB Uses a CC-Compatible Bone Hierarchy and Naming Convention

GECB adopts a CC-compatible bone hierarchy and naming convention for the following reasons:

1. It is widely used in character production workflows and provides high compatibility.
2. Cascadeur's rigging workflow works smoothly with CC-compatible character structures, which helps reduce setup issues and synchronization problems.

For this reason, GECB uses CC-compatible skeletons as the recommended standard for stable real-time synchronization.

---

## Installation and Usage

### Installation Steps

1. Place `GECB_Sender_v1_0.pyc` into the Cascadeur Python plugin folder:  
   `[Cascadeur installation folder]\resources\scripts\python\commands\`

2. Install `GECB_Receiver_v1_0.zip` as a Blender add-on.

3. Open `SampleCharacter.blend` and `SampleCharacter.casc`.

4. In Cascadeur, select `Commands -> GECB Sender(v1_0)`.  
   If `[GECB] Sender Started (v1.0)` appears in the Event Log, the sender is ready.

5. In Blender, start the connection from `N Panel -> GECB -> START SYNC`.

6. To stop the Cascadeur-side sender, select `Commands -> GECB Sender(v1_0)` again.  
   **Note:** Always disconnect before closing the scene or exiting the application.

For detailed usage instructions, please refer to the TeamGadget YouTube channel.

YouTube:  
[https://www.youtube.com/@TeamGadget](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

---

## Support Policy

GECB is provided completely free of charge and as-is.

The developer is an individual FA / factory automation engineer with a separate full-time profession.  
Because of this, providing technical support for individual environments is not realistically possible.

This tool is provided as:

- Free software
- No support
- No warranty
- Use at your own risk

Bug reports and feedback are welcome, but support, updates, or fixes are not guaranteed.

---

## Disclaimer

GECB is an independent project developed by TeamGadget.

Cascadeur is a trademark and/or property of Nekki.  
Blender is a trademark and/or property of Blender Foundation.

This project is not affiliated with, endorsed by, sponsored by, or officially supported by Nekki or Blender Foundation.

---
---
---

# Gadget Entangle for Cascadeur / Blender (GECB)

Gadget Entangle for Cascadeur / Blender（GECB）は、CascadeurとBlenderをリアルタイムで接続するための無料ツールです。

Cascadeurで作成・調整したキャラクターアニメーションを、Blender上でリアルタイムに確認することを目的としています。

---

## GECBの主要機能

1. CascadeurとBlenderをシームレスに繋ぐリアルタイム同期。
2. BlenderのObject Mode / Pose Modeに関係なく同期可能。
3. Blender側でタイムライン・アニメーションを再生している最中でも同期可能。  
   ただし、対象ボーンにキーフレームが打たれていないことが前提です。
4. 最大4体までのキャラクターを同時同期可能。  
   ただし、PCスペックに依存します。
5. Zero Calibrationにより、CascadeurとBlender間のキャラクター状態を補正。
6. Zero Calibration情報の保存・再利用に対応。

---

## 動作環境

- Windows専用  
  GECBはコード内でWindows APIを使用しています。

- 動作確認バージョン  
  - Cascadeur 2026.1.3  
  - Blender 5.1

- 動作確認PC  
  - GPU: NVIDIA RTX 3060 12GB  
  - CPU: AMD Ryzen 7 8-Core  
  - RAM: 32GB

- Cascadeurライセンスについて  
  GECBの利用には、有効なCascadeur有償ライセンスが必要です。  
  Cascadeur無料版では利用できません。

---

## 前提条件

GECBは、CC互換のボーン階層・命名規則を持つキャラクターを対象に設計しています。

想定されるボーン構造およびボーン命名規則については、サンプルキャラクターを参照してください。

### 重要事項

- ボーン階層が想定構造に一致していること。
- ボーンの向きが一致していること。
- ボーン命名規則が対応形式に沿っていること。

GECBは、生ボーンの姿勢を直接同期するツールです。  
万能リグ変換ツールではありません。

### GECBがCC互換のボーン階層・命名規則を採用している理由

GECBでは、以下の理由によりCC互換のボーン階層・命名規則を採用しています。

1. キャラクター制作ワークフローで広く使用されており、高い互換性が期待できるため。
2. Cascadeurのリギング機能がCC互換のキャラクター構造と相性が良く、セットアップ時のトラブルや同期不具合を減らしやすいため。

このため、GECBでは安定したリアルタイム同期を行うための推奨基準として、CC互換スケルトンを採用しています。

---

## 導入手順・使用方法

導入手順
1. `GECB_Sender_v1_0.pyc`をCascadeurのPythonプラグインフォルダに配置します。`[Cascadeurインストール先]\resources\scripts\python\commands\`
2. `GECB_Receiver_v1_0.zip`をBlenderのアドオン登録します。
3. `SampleCharacter.blend`と`SampleXharacter.casc`を開きます。
4. Cascadeurで`Commands -> GECB Sender(v1_0)`を選択する `Event log に[GECB] Sender Started (v1.0)`と表示されば準備完了です。
5. Blender側は`Nパネル -> GECB -> START SYNC`で接続開始します。
6. Cascadeur側を停止するにはもう一度`Commands -> GECB Sender(v1_0)`を選択してください。
   注意　シーンを閉じる時や終了する時は必ず接続を切ってください。

詳細な使用方法については、TeamGadgetのYouTubeチャンネルを参照してください。

YouTube:
[https://www.youtube.com/@TeamGadget](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

---

## サポートについて

GECBは完全無料・現状渡しで提供されます。

開発者は普段、別の本業を抱えるFA系個人エンジニアです。  
そのため、個別の環境に合わせた技術サポートを提供することは事実上不可能です。

本ツールは以下の条件で提供されます。

- 完全無料
- サポートなし
- 無保証
- 自己責任での利用

不具合報告やフィードバックは歓迎しますが、サポート、アップデート、修正対応を保証するものではありません。

---

## 免責事項

GECBはTeamGadgetによる独立したプロジェクトです。

CascadeurはNekkiの商標または財産です。  
BlenderはBlender Foundationの商標または財産です。

本プロジェクトは、NekkiまたはBlender Foundationによる公式製品ではなく、承認、提携、スポンサー提供、または公式サポートを受けたものではありません。

