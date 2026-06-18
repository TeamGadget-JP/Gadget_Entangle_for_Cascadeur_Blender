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
https://actorcore.reallusion.com/auto-rig/accurig

### Why GECB Uses a CC-Compatible Bone Hierarchy and Naming Convention

GECB adopts a CC-compatible bone hierarchy and naming convention for the following reasons:

1. It is widely used in character production workflows and provides high compatibility.
2. Cascadeur's rigging workflow works smoothly with CC-compatible character structures, which helps reduce setup issues and synchronization problems.

For this reason, GECB uses CC-compatible skeletons as the recommended standard for stable real-time synchronization.

---

## Installation and Usage

## Installation Steps

1. Place `GECB_Sender_v1_0.pyc` into the Cascadeur Python plugin folder:  
   `[Cascadeur installation folder]\resources\scripts\python\commands\`
2. Install `GECB_Receiver_v1_0.zip` as a Blender add-on.
3. Open `SampleCharacter.blend` and `SampleCharacter.casc`.
4. In Cascadeur, select `Commands -> GECB Sender(v1_0)`.  
   If `[GECB] Sender Started (v1.0)` appears in the Event Log, the sender is ready.
5. In Blender, start the connection from `N Panel -> GECB -> START SYNC`.
6. To stop the Cascadeur-side sender, select `Commands -> GECB Sender(v1_0)` again.  
   **Note:** Always disconnect before closing the scene or exiting the application.

## How to Use<br>
Step 1: Prepare the character you wish to synchronize (original models, CC4/5, free models, etc.).<br>
Step 2: Import the character into Blender. Set Blender’s units to 1cm to ensure the character is at real-world scale.<br>
Step 3: Ensure the bone structure, orientation, and naming are CC-compatible. You can use tools like AccuRIG to achieve this.<br>
Step 4: Export the character as an FBX to Cascadeur. For FBX settings, please refer to the following<br> 
　　　　URL:https://cascadeur.com/help/getting_started/import_fbxdae/import_from_blender<br>
Step 5: Import into Cascadeur and complete the rigging process. <br>
        Then, run Box Controller Mode -> Select All -> Commands -> Go to T-Pose to set the character to the base pose.<br>
　　　　(Note: Do not move the character from this pose.)<br>
Step 6: In Cascadeur, select Commands -> GECB Sender (v1_0) to start the connection.<br>
Step 7: Open the GECB panel in Blender and set your character to 'Slot 0'.<br>
Step 8: Click the 'START SYNC' button. The character may deform momentarily, but this is normal.<br>
Step 9: Click the 'Zero Calib (Live Stream)' button and then 'OK'. <br>
　　　　If the character matches the pose in Cascadeur, the synchronization is successful.<br>
　　　　(If the poses do not match, please double-check your bone structure, orientation, and naming.) <br>
Step 10: Sync complete! Welcome to the world of real-time previz!<br>

## Further Details<br>
When synchronizing custom characters or those processed through AccuRIG, the most important factor is ensuring that the Hip bone has no unintended rotation.<br>
<img width="300" height="391" alt="image" src="https://github.com/user-attachments/assets/865c8cc6-78d1-44ed-b8d9-1e71e8c946eb" /><br>
Please strictly ensure the following Hip bone coordinates: Head: X=0 Y=0, Tail: X=0 Y=0, and Roll = 0.<br>
Characters imported via AccuRIG have a high probability of importing with a tilted Hip bone.<br>
I have provided a script that fixes this issue with a single click.<br>
`accurig_hip_fix_addon.py`<br>
Please use it as needed. Once installed as an add-on, it will be integrated directly into the GECB UI.<br>

**About Synchronizing Multiple Characters**<br>
<img width="300" height="457" alt="image" src="https://github.com/user-attachments/assets/c4485158-1033-415a-86c2-b270fbd6729c" /><br>
GECB supports the simultaneous connection of up to 4 characters.<br>
GECB identifies characters by checking for a prefix attached to their bone names.<br>
Example: `CC_Base_Hip` -> `character1:CC_Base_Hip`<br>
In Blender, Slot 0 uses no prefix. From Slot 1 onwards, prefixes such as `character1:`, `character2:`, etc., are automatically assigned based on the slot.<br>

**How to Setup Multiple Characters in Cascadeur**<br>
Example: Setting up 2 characters<br>
1. Create a scene, import the 1st character normally, and complete the rigging.<br>
2. Create a new, separate scene for the 2nd character. Import and rig the 2nd character normally.<br>
3. Save and close the scene containing the 2nd character.<br>
4. Return to the scene with the 1st character, and select `File -> Import -> Import Scene To Current...` to import the 2nd character's scene.<br>
5. The prefix `character1:` will automatically be added to the 2nd character's bone names.<br>
6. Follow the exact same procedure for a 3rd character and so on.<br>

## Applying the Final Motion Created in Cascadeur to a Blender Character via FBX<br>
First, it must be explained that the bone animation data used for real-time synchronization and the bone animation data exported to FBX are completely different.<br>
The requirement for real-time synchronization is that the character is in a T-pose or A-pose, and has been zero-calibrated immediately after syncing.<br>
Conversely, a character in a state ready to accept an FBX must be in a T-pose or A-pose, with its zero-calibration cleared.<br>
Therefore, you must follow the steps below.<br>

1. **Return to T-Pose (Reset to Origin)**<br>
   Return the character to the T-pose (initial pose/rest pose) in both Cascadeur and Blender.<br>
2. **Stop Synchronization (Disconnect Communication)**<br>
   Click `STOP SYNC` on the Blender-side GECB panel to completely cut off real-time communication.<br>
3. **Clear Calibration (Memory Initialization)**<br>
   Click `Clear Calibrate` on the GECB panel.<br>
4. **Apply FBX (Inject Production Data)**<br>
   Export the animation as an FBX from Cascadeur, and import (or retarget) it into the Blender character.<br>

If you find GECB useful, please consider subscribing to my channel and liking the video!<br>
YouTube: https://www.youtube.com/@TeamGadget<br>

## Request for Feedback
The 'SampleCharacter' provided was created by taking my own mesh model through AccuRIG to<br>
perform CC-compatible skeleton generation and binding.<br>

Currently, this is the most efficient method I've found to build a CC-compatible skeleton without<br>
using Character Creator 4 or 5.

If you own CC4 or 5, I highly recommend using the official bridge add-on to import your characters.<br>
It achieves an incredibly high level of synchronization accuracy—virtually flawless.<br>
Regarding bone configuration, the 'Hip' bone is the most critical.<br>

To ensure precision, it is an absolute requirement that the Hip's transform (Head and Tail: X=0, Y=0) is<br>
maintained; please keep this in mind if you are building your own generic rigs.<br>

In my case, the 'SampleCharacter' was exported from AccuRIG with a tilted Hip, so I had to manually<br>
correct it in Blender’s Edit Mode.<br>

As a result, the precision of the fingertip positions is slightly compromised.If anyone knows of a<br>
more optimal workflow for this, I would greatly appreciate your feedback.<br>

I am committed to making this tool even better in future versions by incorporating your suggestions<br>
and insights.

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

While I will do my best to address any bug reports and issues, please understand that my availability is irregular.<br>
Thank you for your patience and understanding.

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
https://actorcore.reallusion.com/auto-rig/accurig

### GECBがCC互換のボーン階層・命名規則を採用している理由

GECBでは、以下の理由によりCC互換のボーン階層・命名規則を採用しています。

1. キャラクター制作ワークフローで広く使用されており、高い互換性が期待できるため。
2. Cascadeurのリギング機能がCC互換のキャラクター構造と相性が良く、セットアップ時のトラブルや同期不具合を減らしやすいため。

このため、GECBでは安定したリアルタイム同期を行うための推奨基準として、CC互換スケルトンを採用しています。

---

## 導入手順・使用方法

## 導入手順<br>
1. `GECB_Sender_v1_0.pyc`をCascadeurのPythonプラグインフォルダに配置します。<br>
   `[Cascadeurインストール先]\resources\scripts\python\commands\`<br>
2. `GECB_Receiver_v1_0.zip`をBlenderのアドオン登録します。<br>
3. `SampleCharacter.blend`と`SampleCharacter.casc`を開きます。<br>
4. Cascadeurで`Commands -> GECB Sender(v1_0)`を選択する `Event log に[GECB] Sender Started (v1.0)`と表示されば準備完了です。<br>
5. Blender側は`Nパネル -> GECB -> START SYNC`で接続開始します。<br>
6. Cascadeur側を停止するにはもう一度`Commands -> GECB Sender(v1_0)`を選択してください。<br>
   注意　シーンを閉じる時や終了する時は必ず接続を切ってください。<br>

## 使用方法<br>
step1: ご自身で同期させたいキャラクターを用意してください。(自作、CC4&5、フリーモデル等)<br>
step2: まずBlenderへキャラクターをインポートします、BlenderのUnitを1cmに設定してキャラサイズを実サイズにします。<br>
step3: ボーン構成、向き、命名をCC互換にしてください、またはAccuRIG等を使用してCC互換にしてください。<br>
step4: CascadeurへFBXでエクスポート。FBX設定は下記のURLを参照<br>
　　　　https://cascadeur.com/help/getting_started/import_fbxdae/import_from_blender<br>
step5: Cascadeurでインポート、リギングまで完了した後、`Box Controller Mode -> 全選択 -> Commands -> Go to T-Pose`を実施して基準姿勢にします。<br>
　　　　(この姿勢から絶対に動かさないでください)<br>
step6: Cascadeurで`Commands -> GECB Sender(v1_0)`を選択して通信開始。<br>
step7: BlenderでGECBパネルを開きSlot0へキャラクターをセットします。<br>
step8: START SYNCボタンを押します、キャラクターが変形しますが問題ありません。<br>
step9: Zero Calib (Live Stream)ボタン -> OK でキャラクターがCascadeur側と同じポーズになったら成功です。<br>
　　　　(この時、同じポーズにならない場合はボーン構成、向き、命名を再確認してください)<br>
step10: 同期完了です！リアルタイム・プレビズの世界へようこそ！<br>

## 更に詳細な説明<br>
自作キャラクターやAccuRIGを通したキャラクター等で同期する上で最も重要な事はHipボーンに余計な角度がついて無い事です。<br>
<img width="300" height="391" alt="image" src="https://github.com/user-attachments/assets/865c8cc6-78d1-44ed-b8d9-1e71e8c946eb" /><br>
HipボーンのHead : X=0 Y=0 Tail : X=0 Y=0 Roll = 0 は絶対に守って下さい。<br>
AccuRIGを通してインポートしたキャラクターは高確率でHipボーンに傾きが入ります。<br>
それをボタン一つで修正するスクリプトも用意しました。<br>
`accurig_hip_fix_addon.py`<br>
必要に応じてお使いください。アドオン登録しますとGECBのUIに統合されます。<br>

複数キャラクターの同期について<br>
<img width="300" height="457" alt="image" src="https://github.com/user-attachments/assets/c4485158-1033-415a-86c2-b270fbd6729c" /><br>
GECBでは最大4体までのキャラクターを同時接続できます。<br>
GECBではボーン名の前にプレフィックスを付ける事でキャラクター識別を行っています。<br>
例 : CC_Base_Hip -> character1:CC_Base_Hip<br>
Blender側ではSlot 0:がプレフィックス無し、Slot 1:から順にcharacter1: Character2:...の様に自動的に付与されるようになっています。<br>

Cascadeurでの複数キャラクターセットアップ方法<br>
例 : 2体セットアップ<br>
1. シーンを作成、最初の1体目を通常通りインポート -> リギング。<br>
2. 2体目用に更にシーンを作ります。そのまま2体目を通常通りインポート -> リギング。<br>
3. 2体目が居るシーンを保存して閉じます。<br>
4. 1体目が居るシーンに戻って、File -> Import -> Import Scene To Current...で2体目のシーンをインポート。<br>
5. 2体目のボーン名に自動でcharacter1:のプレフィックスが付与されます。<br>
6. 3体目も同じ手順となります。<br>

## Cascadeurで作ったモーションの最終版をFBXを通じてBlenderのキャラクターに適用する場合<br>
まず説明して置かなければならないのが、リアルタイム同期で使われているボーンアニメーションのデータと<br>
FBXにエクスポートされたボーンアニメーションデータは全く別物です。<br>
リアルタイム同期をする時の条件はTポーズもしくはAポーズであること、同期直後にゼロキャリブレーションされたキャラクターであることです。<br>
逆にFBXを適用できる状態のキャラクターはTポーズもしくはAポーズであること、ゼロキャリブレーションを解除されたキャラクターであることです。<br>
したがって下記の手順を踏むことになります。<br>
1. Tポーズへ戻す（原点復帰）<br>
   CascadeurとBlenderの両方で、キャラクターをTポーズ（初期姿勢/レストポーズ）に戻します。<br>
2. 同期の停止（通信切断）<br>
   Blender側のGECBパネルで `STOP SYNC` をクリックし、リアルタイム通信を完全に遮断します。<br>
3. キャリブレーションの消去（メモリ初期化）<br>
   GECBパネルで `Clear Calibrate` をクリックします。<br>
4. FBXの適用（本番データの流し込み）<br>
   CascadeurからアニメーションをFBXとしてエクスポートし、Blenderのキャラクターにインポート（またはリターゲティング）します。<br>

GECBを使用されてもし良かったらチャネル登録、高評価お願いします。<br>
YouTube:[https://www.youtube.com/@TeamGadget](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

## フィードバックのお願い
SampleCharacterは自分のメッシュモデルをAccuRIGを通してCC互換スケルトン&バインドを行って作成したものです。<br>
いまのところCC4&5を使わずにCC互換スケルトンを最短で構築する方法はこれしか思いつきませんでした。<br>

CC4&5を所持されている方は公式ブリッジアドオンを使用してキャラクターをインポートしますとかなり高精度な<br>
同期キャラクターを実現できます。(狂いは全く無いと言って良いレベルです)<br>

ボーン構成で特に重要なのはHipです。HipのTransformでHeadとTail:X=0 Y=0が精度を確保する上で絶対の仕様となりますので、<br>
汎用を組まれる方は特にここに注意してください。<br>

SampleCharacterはHipが傾いた状態でAccuRIGから出力されてたことから、仕方なくBlenderのエディットモードで修正を施しました。<br>
その影響で指先等の位置精度が若干悪くなっています。<br>
この辺は最適なフローがありましたら是非フィードバックを頂けるとありがたいです。

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
