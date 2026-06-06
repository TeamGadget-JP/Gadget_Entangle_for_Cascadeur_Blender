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
6. Saving and clearing Zero Calibration data.

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

GECB directly synchronizes raw skeletal bone poses.
It does not include a general-purpose rig conversion feature, 
so we recommend preparing the character’s bone setup using free software such as AccuRIG.

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

## Request for Feedback
The 'SampleCharacter' provided was created by taking my own mesh model through AccuRIG to perform CC-compatible skeleton generation and binding. Currently, 
this is the most efficient method I've found to build a CC-compatible skeleton without using Character Creator 4 or 5.
If you own CC4 or 5, I highly recommend using the official bridge add-on to import your characters. It achieves an incredibly high level of synchronization accuracy—virtually flawless.
Regarding bone configuration, the 'Hip' bone is the most critical. To ensure precision, it is an absolute requirement that the Hip's transform (Tail: X=0, Y=0) is maintained; please keep this in mind if you are building your own generic rigs.
In my case, the 'SampleCharacter' was exported from AccuRIG with a tilted Hip, so I had to manually correct it in Blender’s Edit Mode. As a result, the precision of the fingertip positions is slightly compromised.
If anyone knows of a more optimal workflow for this, I would greatly appreciate your feedback.
I am committed to making this tool even better in future versions by incorporating your suggestions and insights.

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

While I will do my best to address any bug reports and issues, please understand that my availability is irregular. Thank you for your patience and understanding.

---

## Disclaimer

GECB is an independent project developed by TeamGadget.

Cascadeur is a trademark and/or property of Nekki.  
Blender is a trademark and/or property of Blender Foundation.

This project is not affiliated with, endorsed by, sponsored by, or officially supported by Nekki or Blender Foundation.

---
# 日本語 #
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
6. Zero Calibration情報の保存と解除。

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
汎用リグ変換機能はありませんのでキャラクターのボーンセットアップは
無料ソフトウェアのAccuRIG等を使われる事を推奨します。

### GECBがCC互換のボーン階層・命名規則を採用している理由

GECBでは、以下の理由によりCC互換のボーン階層・命名規則を採用しています。

1. キャラクター制作ワークフローで広く使用されており、高い互換性が期待できるため。
2. Cascadeurのリギング機能がCC互換のキャラクター構造と相性が良く、セットアップ時のトラブルや同期不具合を減らしやすいため。

このため、GECBでは安定したリアルタイム同期を行うための推奨基準として、CC互換スケルトンを採用しています。

---

## 導入手順・使用方法

導入手順
1. `GECB_Sender_v1_0.pyc`をCascadeurのPythonプラグインフォルダに配置します。
   `[Cascadeurインストール先]\resources\scripts\python\commands\`
2. `GECB_Receiver_v1_0.zip`をBlenderのアドオン登録します。
3. `SampleCharacter.blend`と`SampleCharacter.casc`を開きます。
4. Cascadeurで`Commands -> GECB Sender(v1_0)`を選択する `Event log に[GECB] Sender Started (v1.0)`と表示されば準備完了です。
5. Blender側は`Nパネル -> GECB -> START SYNC`で接続開始します。
6. Cascadeur側を停止するにはもう一度`Commands -> GECB Sender(v1_0)`を選択してください。
   注意　シーンを閉じる時や終了する時は必ず接続を切ってください。

詳細な使用方法については、TeamGadgetのYouTubeチャンネルを参照してください。<br>
YouTube:[https://www.youtube.com/@TeamGadget](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

## フィードバックのお願い
SampleCharacterは自分のメッシュモデルをAccuRIGを通してCC互換スケルトン&バインドを行って作成したものです。<br>
いまのところCC4&5を使わずにCC互換スケルトンを最短で構築する方法はこれしか思いつきませんでした。<br>
CC4&5を所持されている方は公式ブリッジアドオンを使用してキャラクターをインポートしますとかなり高精度な同期キャラクターを実現できます。<br>
(狂いは全く無いと言って良いレベルです)<br>
ボーン構成で特に重要なのはHipです。HipのTransformでTail:X=0 Y=0が精度を確保する上で絶対の仕様となりますので、汎用を組まれる方はここに注意してください。<br>
SampleCharacterはHipが傾いた状態でAccuRIGから出力されてたことから、仕方なくBlenderのエディットモードで修正を施しました。<br>
その影響で指先等の位置精度が若干悪くなっています。この辺は最適なフローがありましたら是非フィードバックを頂けるとありがたいです。<br>
今後のバージョンで皆様から頂いた意見を反映して、より一層良いツールになって行ければと思います。<br>

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

バグ不具合報告へはできる限り対応しますが不定期になります。ご理解ください

---

## 免責事項

GECBはTeamGadgetによる独立したプロジェクトです。

CascadeurはNekkiの商標または財産です。  
BlenderはBlender Foundationの商標または財産です。

本プロジェクトは、NekkiまたはBlender Foundationによる公式製品ではなく、承認、提携、スポンサー提供、または公式サポートを受けたものではありません。

