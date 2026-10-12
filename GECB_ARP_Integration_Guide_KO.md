# GECB v1.0 → Blender Auto-Rig Pro(ARP) 연동을 위한 기술 참고 자료

**TeamGadget — 외부 개발자 참고용 초안 (2026-10-12)**  
**대상:** Cascadeur와 Blender에서 애니메이션을 제작하며, GECB 수신부를 자신의 ARP 작업 환경에 맞게 확장해 보려는 개발자  
**범위:** 1세대 **GECB**. 후속 프로젝트 CEB 및 URSS와 혼동하지 마세요.

> 이 문서는 GECB Sender 구현을 검토해 정리한 **인터페이스 설명**입니다. 비공개 Cascadeur Sender 소스 코드는 제공하지 않습니다. ARP 연동은 아직 이 문서로 검증된 공식 지원 기능이 아니며, 아래 개발 방향은 실험을 위한 제안입니다.

## 1. 결론부터: 어디를 수정할 수 있나요?

GECB v1.0은 CC(Character Creator) 호환 본 이름과 구조를 중심으로 만들어졌습니다. 현재의 Sender가 모든 리그를 동적으로 인식하는 방식은 **아닙니다**.

- **Cascadeur(송신 측):** Sender는 특정 CC 본 이름을 기준으로 캐릭터 존재 여부를 확인한 뒤, 지정된 이름 목록에서 본을 찾습니다. ARP 고유 이름만 있는 리그라면 송신 자체가 시작되지 않을 수 있습니다.
- **Blender(수신 측):** 전달된 본 ID를 ARP의 실제 변형용 본(deform bones) 또는 별도의 중계용 CC 리그로 연결하는 방식으로 확장할 여지가 있습니다.
- **핵심:** Blender 수신부만 고치더라도, Cascadeur 측이 먼저 인식 가능한 본 구조와 이름을 제공해야 합니다.

**권장하는 첫 접근**은 기존 CC 샘플 씬의 동작을 확인한 뒤, Blender에 CC 호환 **중계 리그(proxy)** 를 남겨두고 ARP의 변형 리그로 애니메이션을 전달해 보는 것입니다. 직접 ARP 본에 적용하는 방식도 가능성을 검토할 수 있지만, 본 공간 변환과 제약(Constraints) 충돌을 별도로 다뤄야 합니다.

## 2. 구성과 데이터 흐름

```text
Cascadeur scene (CC-compatible / recognized names)
    │ 현재 프레임의 본 위치·회전 추출
    ▼
GECB Sender (비공개 코드; 변경 불필요한 경로부터 검토)
    │ UDP, 127.0.0.1:8985, 각 캐릭터마다 1개 데이터그램
    ▼
Blender GECB Receiver (공개 배포물)
    │ 수신/디코딩 → 본 ID → 대상 본/중계 리그
    ├─ 기존 CC 호환 Armature
    └─ [실험 확장] CC Proxy → ARP Deform Rig
```

Sender는 약 **33 ms 간격**으로 현재 프레임을 확인하도록 타이머를 설정합니다(명목상 약 30회/초). 실제 전송 간격을 보장하는 정확한 동기 시계는 아닙니다. 이 1세대 패킷에는 타임스탬프나 프레임 번호가 포함되지 않습니다.

## 3. Sender가 캐릭터를 인식하는 조건 — 가장 중요

각 캐릭터 슬롯에 대해 다음 이름 중 **하나 이상**이 Cascadeur 씬에 있어야 활성 캐릭터로 판정합니다.

- `CC_Base_Hip`
- `CC_Base_Pelvis`

다중 캐릭터 슬롯에서는 아래 접두어가 각 이름 앞에 붙습니다.

| 패킷의 Character ID | Cascadeur 본 이름 접두어 |
|---:|---|
| `0` | 없음 (`CC_Base_Hip`) |
| `1` | `character1:` |
| `2` | `character2:` |
| `3` | `character3:` |

**주의:** 아래 본 검색 목록에 `pelvis`, `root` 같은 일부 별칭이 있어도, 캐릭터를 처음 찾는 관문은 `CC_Base_Hip` 또는 `CC_Base_Pelvis`입니다. 따라서 ARP 리그가 일반적인 `pelvis` 이름만 가지고 있으면, 그 이름만으로는 활성 캐릭터로 인식되지 않습니다.

이는 **Cascadeur에서 ARP 본 이름을 그대로 사용하는 경우**와 **Blender에서 ARP 리그를 대상으로 사용하는 경우**를 구분해야 하는 이유입니다. 두 경우는 해결해야 하는 문제가 다릅니다.

## 4. UDP 패킷 참조 (Sender v1.0 기준)

| 순서 | 필드 | 형식 | 설명 |
|---|---|---|---|
| 1 | Magic | ASCII 4바이트 | `GECB` |
| 2 | Character ID | `uint8` | `0`–`3` |
| 3 | Bone entries | 반복 | 패킷 끝까지 반복; 별도의 본 개수 필드 없음 |

각 Bone entry는 다음 순서입니다.

| 순서 | 필드 | 형식 | 설명 |
|---|---|---|---|
| 1 | Bone ID | `uint8` | 아래 표의 내부 ID |
| 2 | Data type | `uint8` | `1`: 회전만 / `3`: 위치 + 회전 |
| 3a | Translation | `<3f` (12B) | **type=3일 때만** X, Y, Z |
| 3b | Rotation | `<4f` (16B) | Quaternion **X, Y, Z, W** |

모든 float는 **리틀 엔디언 32비트 float**입니다. `type=1` 항목은 총 **18바이트**, `type=3` 항목은 총 **30바이트**입니다(각 항목의 2바이트 헤더 포함).

- Translation은 **Bone ID 0(Root) 또는 1(Hip/Pelvis)** 에서 위치를 읽을 수 있을 때에만 포함됩니다. 그 외 본은 회전 데이터만 송신합니다.
- Root/Hip의 송신 위치 값은 Sender가 읽은 값에 **`0.01`을 곱한 값**입니다. Blender에서 다시 적용할 때에는 장면 단위와 기존 Receiver 처리 방식을 확인하세요.
- 회전은 Cascadeur의 **`Local Rotation`을 우선** 사용하고, 없으면 `Global Rotation`을 사용합니다.
- 위치는 **`Global Position`을 우선** 사용하고, 없으면 `Local Position`을 사용합니다.
- 해당 본의 회전을 얻지 못하면 그 항목은 **전송하지 않습니다**. 슬롯 안에 전송 가능한 본이 하나도 없으면 해당 슬롯의 패킷도 보내지 않습니다.
- 본 ID는 연속 번호가 아니며, 데이터그램에 포함되는 본 개수도 고정되어 있지 않습니다. **순서나 고정 길이에 의존하지 않고 ID를 기준으로 파싱**해야 합니다.
- 네트워크 목적지는 송신 구현상 **`127.0.0.1:8985`**, 즉 동일 PC의 루프백입니다.

**주의:** Sender의 `Local Rotation`과 Blender Pose Bone의 `rotation_quaternion`을 무조건 동일 공간의 값으로 간주하면 안 됩니다. 기준 자세(rest pose), 부모 본 좌표계, 축 방향과 제약 상태를 고려해야 합니다. 특히 Sender가 일부 데이터에서 Global 값을 대체 사용하더라도 그 사실을 패킷에 별도 표시하지 않습니다.

## 5. 간단한 수신 데이터 디코더 (개발용)

아래 코드는 **Sender 소스가 아니며**, 위 패킷을 확인할 수 있도록 별도로 작성한 최소한의 파싱 예시입니다. 값의 공간 변환이나 Blender 적용까지 구현한 것은 아닙니다.

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

**포트 사용 주의:** 기존 GECB Receiver가 8985 포트를 사용 중이면, 이 테스트 수신기와 같은 포트에 동시에 일반적인 방식으로 바인딩할 수 없습니다. 패킷 확인 테스트는 기존 Receiver를 멈춘 상태에서 수행하거나, Receiver 내부에 로그 기능을 추가하는 편이 안전합니다.

## 6. ARP 대응을 시도할 때의 두 경로

### A. CC Proxy 리그를 두는 방법 — 첫 실험으로 권장

```text
Cascadeur: CC-compatible character
       ↓ (original Sender / original protocol)
Blender: CC-compatible proxy armature
       ↓ (constraints / retarget with proper rest alignment)
Blender: ARP deform armature → character mesh
```

- 먼저 저장소의 `SampleCharacter.casc` 및 `SampleCharacter.blend` 조합으로 기존 동작을 확인합니다.
- CC 리그를 데이터 수신 전용으로 사용하고, ARP 변형용 리그에 제약 또는 매핑으로 모션을 전달합니다.
- 원본 리그와 ARP 리그의 Rest Pose 및 축 방향을 정렬하고, 각 본의 부모 공간을 고려합니다.
- ARP **컨트롤 본**을 무조건 직접 구동하지 마세요. IK/FK, 컨스트레인트, 드라이버가 겹칠 수 있으므로 **실제 변형에 사용되는 본**을 확인해야 합니다.

이 방법은 Sender를 변경할 필요가 적지만, **리타게팅/제약 설정 작업이 완전히 사라지는 것은 아닙니다.**

### B. Blender 수신부에서 본 ID → ARP 본 매핑

- 송신한 Bone ID를 받아 대상 ARP 본으로 매핑할 수 있습니다.
- 하지만 이름만 바꾸면 되는 문제가 아닙니다. 같은 ID의 회전 값도 **Cascadeur 본의 기준 공간과 ARP 대상 본의 로컬 공간**이 다를 수 있습니다.
- 필요한 처리는 대개 **Rest Pose 기준 보정 → 축/좌표계 변환 → 부모 공간 변환 → ARP 제약과의 충돌 확인**으로 나뉩니다.
- 이름 매핑은 초기 연결 작업이고, **자세 변환(Pose Conversion)** 이 실질적인 난점입니다.

두 방법 모두 **Sender가 보내지 않은 임의의 ARP 컨트롤 본 데이터**를 만들어 낼 수는 없습니다. 예를 들어 아래 64개 ID 목록에 없는 추가 본은 별도 처리 방법을 설계해야 합니다.

## 7. 권장 테스트 순서

1. **기준선:** 저장소의 GECB 샘플 씬에서 기존 CC 캐릭터의 실시간 동작과 Zero Calibration을 먼저 확인합니다.
2. **슬롯 0만:** 하나의 캐릭터, 하나의 Receiver, 기본 포트로 시작합니다.
3. **루트/Hip:** Root(0), Hip/Pelvis(1)의 전송 및 이동값 적용을 확인합니다.
4. **한쪽 팔:** Clavicle(10) → Upperarm(11) → Forearm(12) → Hand(13)만 우선 비교합니다.
5. **기본 자세:** T/A Pose와 Rest Pose 차이, 회전축, 부모 공간을 확인합니다. 팔을 90° 굽혀 볼 때 어디서 오차가 발생하는지 기록하세요.
6. **ARP 구동:** ARP의 변형 본과 제어 본을 구별하여, 중복 제약이나 IK/FK 충돌이 없는지 확인합니다.
7. **하체·머리·손가락:** 팔이 정확하게 맞은 후 범위를 확장합니다.
8. **마지막에 다중 슬롯:** 접두어 규칙과 Character ID를 확인합니다.

### 문제 발생 시 빠른 진단

| 현상 | 먼저 확인할 것 |
|---|---|
| 패킷이 전혀 오지 않음 | Cascadeur에 `CC_Base_Hip` 또는 `CC_Base_Pelvis`가 실제로 있는지, Sender가 시작되었는지 |
| CC 샘플은 동작하지만 ARP만 움직이지 않음 | Receiver의 본 ID 매핑, 대상 Armature/Deform Bone 참조, Constraint 상태 |
| 본은 움직이지만 자세가 뒤틀림 | Rest Pose, 본 축, Quaternion 공간, 부모 Transform, Zero Calibration |
| Root/Hip의 위치만 어긋남 | 0.01 배율, Global/Local 위치 우선순위, 객체/Armature 스케일 |
| 두 번째 캐릭터가 누락됨 | `character1:` 접두어, Character ID 1 사용 여부 |
| 일부 손가락만 움직이지 않음 | 실제 송신된 Bone ID, 해당 이름의 존재 및 Rotation 데이터 유무 |

## 8. Sender v1.0에서 검색하는 본 목록 (64개 ID)

첫 번째 이름이 우선 검색되는 이름입니다. 그 뒤의 이름은 Sender가 순서대로 시도하는 별칭입니다. **모든 이름이 자유롭게 매핑 가능한 것은 아닙니다.** 활성 캐릭터 판정은 앞의 §3 조건을 따릅니다.

| Bone ID | 우선 검색하는 이름 | 추가 검색 별칭 |
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

## 9. 이 자료의 범위와 후속 버전

**Sender 구현으로 확인 가능한 사실:** 패킷 구조, 송신 대상 주소, 슬롯/접두어 규칙, 본 ID와 검색 이름, 현재 프레임 데이터 추출 및 우선순위.

**이 문서만으로 확정할 수 없는 사항:** 실제 ARP 본 구조(사용자의 ARP 버전·설정에 따라 다름), Blender Receiver의 세부 Pose 적용 방식, 모든 리그의 호환성, ARP 대응 작업량 및 성공 여부. 그런 사항은 실제 리그와 Receiver 코드를 검토해 확인해야 합니다.

- **GECB (1세대, 이 문서의 대상):** https://github.com/TeamGadget-JP/Gadget_Entangle_for_Cascadeur_Blender
- **CEB (2세대):** Rig-Agnostic 및 Smart Swizzle 도입 — https://github.com/TeamGadget-JP/Cascadeur_Entangle_for_Blender
- **URSS (후속 시스템):** G-HUB를 중심으로 한 모듈식 실시간 동기화 — https://github.com/TeamGadget-JP/UNIVERSAL_REAL-TIME_SYNC_SYSTEM

새로운 시스템을 사용하려는 목적이라면 CEB/URSS도 참고할 수 있습니다. 반면 GECB 구조를 직접 연구하거나 확장해 보는 목적이라면, 위 제약과 인터페이스가 출발점이 될 것입니다.

---

**저작/배포에 관한 참고:** 이 문서에는 비공개 Sender 원본 코드를 포함하지 않았습니다. 수신부의 수정·재배포는 해당 저장소/배포물의 라이선스 조건을 별도로 확인하세요. 이 문서는 정식 ARP 호환성 보증서가 아니라 개발자에게 제공하는 기술 참고 초안입니다.
