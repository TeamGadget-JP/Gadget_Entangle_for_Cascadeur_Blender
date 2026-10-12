# GECB v1.0 → Blender Auto-Rig Pro（ARP）対応検討のための技術資料

**TeamGadget — 開発者向けレビュー用日本語版（2026-10-12）**  
**対象:** GECBを自身のARP環境に対応させたいBlender/Python開発者。**第一世代GECBに限定。**

> 本資料はユーザー提供の非公開GECB Senderソースから、**外部開発者に必要な通信インターフェースと制約**を抜き出して整理したものです。Senderソースそのものは含めません。ARPへの対応は実験課題であり、動作保証や公式対応表明ではありません。

## 1. 最重要事項

GECB Senderは、任意のボーンを自動探索する仕組みではありません。まずCascadeur上に `CC_Base_Hip` または `CC_Base_Pelvis` が存在するかどうかでキャラクターを検出します。その後、固定のボーン名候補を探し、**64種類のBone ID**のいずれかに変換して送信します。

したがって、**Blender側だけARP対応にしても、Cascadeur側がSenderに認識されなければデータが出ません。** 一方でCascadeur側をCC互換に保てるなら、Blender側のARP変形ボーンへの転送やCC互換プロキシリグによる橋渡しが検討できます。

## 2. 構成とパケット概要

```text
Cascadeur (CC互換名・階層)
   → GECB Sender（閉源）
   → UDP 127.0.0.1:8985（キャラクターごとに1データグラム）
   → Blender GECB Receiver（配布物）
   → CC互換リグ / [試案] CC Proxy → ARP Deform Rig
```

SenderはWindowsタイマーを約33ms間隔で設定します。名目上約30Hzですが正確なフレームレート保証はありません。通信パケット内にタイムスタンプやフレーム番号はありません。

### キャラクター検出とスロット

| Character ID | 検索時のプレフィックス |
|---:|---|
| 0 | なし |
| 1 | `character1:` |
| 2 | `character2:` |
| 3 | `character3:` |

各スロットについて、プレフィックス付きの `CC_Base_Hip` または `CC_Base_Pelvis` を見つけた場合のみアクティブとします。検索候補には `pelvis` などの別名もありますが、それ単独では最初のキャラクター検出条件を満たしません。

### UDPペイロード

| オフセット/順序 | フィールド | 型 | 意味 |
|---|---|---|---|
| 0–3 | マジック | ASCII4 | `GECB` |
| 4 | Character ID | uint8 | 0–3 |
| 5以降 | Bone Entryを繰返し | 可変 | 末尾まで。個数フィールドなし |

Bone Entry は `Bone ID (uint8)` → `Data Type (uint8)` → ペイロードという順序です。

| Data Type | ペイロード | 1エントリ全体のサイズ |
|---|---|---:|
| `1` | Quaternion `<4f` (x,y,z,w) | 18 bytes |
| `3` | Position `<3f` (x,y,z) + Quaternion `<4f` | 30 bytes |

数値は**リトルエンディアンfloat32**。位置はID 0（Root）と1（Hip/Pelvis）に限り、値が取得できる場合だけ付加します。Positionの各成分には `0.01` が掛けられています。それ以外はQuaternionのみ。未取得のボーンは送信されず、すべて未取得なら当該スロットのパケット自体が送信されません。

- 回転：Cascadeur `Local Rotation`優先、なければ`Global Rotation`。
- 位置：`Global Position`優先、なければ`Local Position`。
- どちらを採ったかを示すメタ情報は送信されません。
- Bone IDは欠番があり、順序・件数・パケットサイズに固定前提を置いてはいけません。
- GECB Senderは `127.0.0.1:8985`（同一PC向け）へUDP送信します。

### 独立した解析用Python例

以下は**非公開Senderの再掲ではなく、パケット形式を調べるために新規作成したデコーダ例**です。Blenderリグへの実際の姿勢変換は行いません。

```python
# Receiver-side diagnostic sample only. This is NOT GECB Sender source.
import struct


def decode_gecb_packet(datagram: bytes):
    if len(datagram) < 5 or datagram[:4] != b"GECB":
        raise ValueError("Not a GECB v1.0 packet")

    character_slot = datagram[4]
    if character_slot not in (0, 1, 2, 3):
        raise ValueError("Unknown character slot")

    pos = 5
    bones = {}
    while pos < len(datagram):
        if len(datagram) - pos < 2:
            raise ValueError("Truncated bone entry")
        bone_id, data_type = datagram[pos], datagram[pos + 1]
        pos += 2

        translation = None
        if data_type == 3:
            if len(datagram) - pos < 12:
                raise ValueError("Truncated translation")
            translation = struct.unpack_from("<3f", datagram, pos)
            pos += 12
        elif data_type != 1:
            raise ValueError(f"Unknown data type: {data_type}")

        if len(datagram) - pos < 16:
            raise ValueError("Truncated quaternion")
        quat_xyzw = struct.unpack_from("<4f", datagram, pos)
        pos += 16
        bones[bone_id] = {"position": translation, "rotation_xyzw": quat_xyzw}

    return character_slot, bones
```

この受信テストで8985ポートをバインドする場合、既存のReceiverと同時使用しないこと。既存のReceiverを停止するか、Receiver内部のログ出力を利用します。

## 3. ARPへの対応方法（推奨順）

### 案A：CC互換プロキシ経由（初手としておすすめ）

```text
Cascadeur CC互換骨格 → GECB Sender → Blender CC互換Proxy骨格
                                         ↓ (Constraints / Retarget)
                                     ARP変形骨格 → Mesh
```

まず公式GECBの `SampleCharacter.casc` / `SampleCharacter.blend` の組み合わせで現状の同期を確認。Blender側で受信専用のCC骨格を保持し、ARPの**Deform Bone**へ適切なConstraintや補正行列で動きを伝える方式です。制御ボーンに直接入力するとIK/FKや制約との競合が起きうるため、対象を慎重に決めます。

### 案B：受信したBone IDをARPボーンに直結

Receiver側で各Bone IDをARPの適切な変形ボーンにマッピングする方式。ただし**名前の置換だけでは解決しません**。Rest Poseの違い、ボーンのローカル軸、親ボーン空間、回転クォータニオンの基準、IK/Constraint処理、Zero Calibration等の調整が必要です。

重要なのは、**Senderが送信していないARP固有の制御ボーンの情報は受信側で直接得られない**ことです。必要ならARPの既存リグ機能で再構築する必要があります。

## 4. 検証順序

1. **標準GECB CCサンプルを無改造で動かす。** Zero Calibrationまで確認。
2. まずキャラクター1体・Slot0のみで試す。
3. Root(0)とHip(1)の姿勢・移動・スケールを確認。
4. 左腕（Clavicle10→Upperarm11→Forearm12→Hand13）だけARPへ転送し、基準姿勢と回転の符号/軸を検証。
5. 同じ手法を反対側の腕、脚、首、指へ拡大。
6. その後に複数キャラクター（prefix / Character ID）をテスト。

問題別の診断：パケットなし→CC Hip/Pelvisの存在/起動状態。ARPのみ無反応→IDマッピング・Deform Bone・制約。変形がねじれる→Rest Pose/軸/親空間/Zero Calibration。Root/Hipの位置ずれ→0.01倍率・Global/Local・Armatureスケール。指だけ無反応→対応IDと回転データを確認。

## 5. Senderが参照するボーン名とID（64件）

`第一候補` → `別名候補` の順番で検索されます。いずれも最初のキャラクター検出ゲートを満たす必要があります。

| Bone ID | 第一候補 | 別名候補 |
|---:|---|---|
| `0` | `CC_Base_BoneRoot` | `root` |
| `1` | `CC_Base_Hip` | `CC_Base_Pelvis`, `pelvis` |
| `2` | `CC_Base_Waist` | `stomach` |
| `3` | `CC_Base_Spine02` | `chest` |
| `4` | `CC_Base_NeckTwist01` | `neck` |
| `5` | `CC_Base_Head` | `head` |
| `6` | `CC_Base_Spine01` | — |
| `7` | `CC_Base_NeckTwist02` | — |
| `10` | `CC_Base_L_Clavicle` | `clavicle_l` |
| `11` | `CC_Base_L_Upperarm` | `arm_l` |
| `12` | `CC_Base_L_Forearm` | `forearm_l` |
| `13` | `CC_Base_L_Hand` | `hand_l` |
| `20` | `CC_Base_R_Clavicle` | `clavicle_r` |
| `21` | `CC_Base_R_Upperarm` | `arm_r` |
| `22` | `CC_Base_R_Forearm` | `forearm_r` |
| `23` | `CC_Base_R_Hand` | `hand_r` |
| `30` | `CC_Base_L_Thigh` | `thigh_l` |
| `31` | `CC_Base_L_Calf` | `calf_l` |
| `32` | `CC_Base_L_Foot` | `foot_l` |
| `33` | `CC_Base_L_ToeBase` | `toe_l` |
| `40` | `CC_Base_R_Thigh` | `thigh_r` |
| `41` | `CC_Base_R_Calf` | `calf_r` |
| `42` | `CC_Base_R_Foot` | `foot_r` |
| `43` | `CC_Base_R_ToeBase` | `toe_r` |
| `51` | `CC_Base_L_Thumb1` | — |
| `52` | `CC_Base_L_Thumb2` | — |
| `53` | `CC_Base_L_Thumb3` | — |
| `54` | `CC_Base_L_Index1` | — |
| `55` | `CC_Base_L_Index2` | — |
| `56` | `CC_Base_L_Index3` | — |
| `57` | `CC_Base_L_Mid1` | — |
| `58` | `CC_Base_L_Mid2` | — |
| `59` | `CC_Base_L_Mid3` | — |
| `60` | `CC_Base_L_Ring1` | — |
| `61` | `CC_Base_L_Ring2` | — |
| `62` | `CC_Base_L_Ring3` | — |
| `63` | `CC_Base_L_Pinky1` | — |
| `64` | `CC_Base_L_Pinky2` | — |
| `65` | `CC_Base_L_Pinky3` | — |
| `71` | `CC_Base_R_Thumb1` | — |
| `72` | `CC_Base_R_Thumb2` | — |
| `73` | `CC_Base_R_Thumb3` | — |
| `74` | `CC_Base_R_Index1` | — |
| `75` | `CC_Base_R_Index2` | — |
| `76` | `CC_Base_R_Index3` | — |
| `77` | `CC_Base_R_Mid1` | — |
| `78` | `CC_Base_R_Mid2` | — |
| `79` | `CC_Base_R_Mid3` | — |
| `80` | `CC_Base_R_Ring1` | — |
| `81` | `CC_Base_R_Ring2` | — |
| `82` | `CC_Base_R_Ring3` | — |
| `83` | `CC_Base_R_Pinky1` | — |
| `84` | `CC_Base_R_Pinky2` | — |
| `85` | `CC_Base_R_Pinky3` | — |
| `91` | `CC_Base_L_BigToe1` | — |
| `92` | `CC_Base_L_IndexToe1` | — |
| `93` | `CC_Base_L_MidToe1` | — |
| `94` | `CC_Base_L_RingToe1` | — |
| `95` | `CC_Base_L_PinkyToe1` | — |
| `101` | `CC_Base_R_BigToe1` | — |
| `102` | `CC_Base_R_IndexToe1` | — |
| `103` | `CC_Base_R_MidToe1` | — |
| `104` | `CC_Base_R_RingToe1` | — |
| `105` | `CC_Base_R_PinkyToe1` | — |

## 6. 確認できる範囲／できない範囲

**Senderから確定できること:** キャラクター検出、プレフィックス/Slot、固定ボーンID辞書、通信形式・宛先、取得値と優先順位。

**この資料だけでは保証できないこと:** ARPの実際のリグ構造、Receiver内部のPose適用・ゼロキャリブレーション実装、対応作業量、ARP互換性。Receiverと使用するARPリグの検証が別途必要です。

公式公開資料（参考）：

- 第1世代GECB: https://github.com/TeamGadget-JP/Gadget_Entangle_for_Cascadeur_Blender
- 第2世代CEB（Rig-Agnostic / Smart Swizzle）: https://github.com/TeamGadget-JP/Cascadeur_Entangle_for_Blender
- URSS（G-HUB中心の後継プロジェクト）: https://github.com/TeamGadget-JP/UNIVERSAL_REAL-TIME_SYNC_SYSTEM

---

**共有前確認事項:** この文書は、公開していないSenderソースから抽出した**通信ポート・パケット形式・固定Bone ID一覧**を含みます。ソースコード自体は含めていませんが、内部インターフェース仕様を公開することになるため、**リーダーの公開判断を経てから配布**してください。改造物の再配布条件は各リポジトリのライセンスを確認してください。
