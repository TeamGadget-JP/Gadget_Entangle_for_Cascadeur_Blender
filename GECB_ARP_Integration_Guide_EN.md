# GECB v1.0 — Technical Notes for Auto-Rig Pro (ARP) Integration

**TeamGadget | Developer Reference | October 12, 2026**

**Audience:** Blender/Python developers experimenting with GECB and an Auto-Rig Pro (ARP) workflow.  
**Scope:** The **first-generation GECB** (Gadget Entangle for Cascadeur / Blender), not its later successors CEB or URSS.

> This document describes relevant interfaces and constraints of the original GECB Sender without publishing its source code. It is intended to help other developers explore possible ARP integrations. **ARP compatibility has not been validated by this document and is not an officially supported GECB feature.** The implementation approaches below are suggestions for experimentation, not confirmed solutions.

## 1. The key distinction: data transmission vs. rig evaluation

GECB v1.0 was designed around a **Character Creator (CC)-compatible bone naming convention and skeleton setup**. Its Cascadeur Sender does **not** dynamically discover and transmit arbitrary rig structures.

There are two separate questions:

1. **Can the Sender recognize and transmit the character in Cascadeur?** It looks for specific CC bone names and uses a fixed mapping from recognized names to numeric Bone IDs.
2. **Can Blender apply the received transforms to an ARP rig?** Even when the original GECB connection works, an ARP rig may have distinct control bones, deform bones, constraints, rest orientations, and local coordinate spaces.

Changing only the Blender side cannot make the Sender transmit a character it does not recognize. However, **if the Cascadeur character remains compatible with GECB**, there is a plausible integration path entirely on the Blender side: receive the original data into a CC-compatible proxy armature, then transfer the motion into the ARP rig.

## 2. System overview

```text
Cascadeur scene (CC-compatible bone names / setup)
       |
       | Read transforms at the current frame
       v
GECB Sender (original implementation)
       |
       | UDP to 127.0.0.1:8985
       | One datagram per active character per sender callback
       v
Blender GECB Receiver
       |
       +--> Existing CC-compatible armature
       |
       +--> [Experimental] CC proxy armature
                  |
                  | Constraints / retargeting / pose-space conversion
                  v
             ARP deform rig --> Character mesh
```

The Sender registers a Windows timer with a nominal **33 ms interval** (roughly 30 callbacks per second). This is not a guaranteed fixed sampling rate. GECB v1.0 packets contain **no timestamp or frame number**.

## 3. Character detection and slots

For each potential character, the Sender first searches the Cascadeur scene for at least one of the following names:

- `CC_Base_Hip`
- `CC_Base_Pelvis`

For additional characters, the names are prefixed as follows:

| Character ID in packet | Prefix used when searching Cascadeur bones |
|---:|---|
| `0` | None (e.g., `CC_Base_Hip`) |
| `1` | `character1:` |
| `2` | `character2:` |
| `3` | `character3:` |

**Important:** The later bone-lookup table includes aliases such as `pelvis` and `root`, but those aliases do **not** satisfy the initial character-detection check by themselves. A rig containing only a bone named `pelvis` will not be recognized as an active character by this Sender.

The detection stage checks names; it does not independently validate that the entire skeleton is structurally correct. Correct hierarchy, rest pose, and bone orientations still matter for meaningful pose transfer.

This is why **using an ARP rig directly in Cascadeur** and **driving an ARP rig in Blender from a recognized CC-compatible Cascadeur character** are very different tasks.

## 4. GECB v1.0 UDP packet format

The current Sender sends packets to **`127.0.0.1:8985`**, the local machine's loopback address. Each emitted datagram has the following structure:

| Offset / order | Field | Format | Notes |
|---|---|---|---|
| 0–3 | Magic | 4 ASCII bytes | `GECB` |
| 4 | Character ID | `uint8` | `0`–`3` |
| 5 onward | Bone entries | Variable length | Repeated until the end of the datagram; no bone-count field |

Each bone entry contains a one-byte **Bone ID**, a one-byte **Data Type**, and its associated numeric payload:

| Data Type | Payload | Total size of entry |
|---|---|---:|
| `1` | Quaternion: `<4f` (`x`, `y`, `z`, `w`) | 18 bytes |
| `3` | Translation: `<3f` (`x`, `y`, `z`) followed by quaternion `<4f` | 30 bytes |

All floating-point values are **little-endian IEEE 754 float32** values.

### Transmission rules

- **Rotation:** the Sender prefers Cascadeur's `Local Rotation`; if unavailable, it falls back to `Global Rotation`.
- **Position:** the Sender prefers `Global Position`; if unavailable, it falls back to `Local Position`.
- **Translation is included only for Bone ID `0` (Root) or `1` (Hip/Pelvis)**, and only when a position value is available. Other transmitted bones carry rotation only.
- **Position scale:** the Sender multiplies each transmitted translation component by **`0.01`**. Confirm how the existing Receiver and the Blender scene interpret this scale before applying any additional conversion.
- **Missing bones:** an entry is omitted when neither local nor global rotation can be read. If no qualifying bone is found for a slot, no datagram is sent for that slot.
- **No space metadata:** the packet does not specify whether a particular position or rotation came from local or global data.
- **Sparse IDs:** Bone IDs are not consecutive. Never assume a fixed number, contiguous sequence, or fixed total packet length.
- **No names in packets:** only numeric Bone IDs are transmitted, not the source bone names.

In particular, **a Cascadeur local rotation is not necessarily directly assignable to a Blender pose bone's local quaternion**. Rest-pose orientation, coordinate axes, parent transforms, and rig constraints can all change the meaning of the same quaternion values.

### Minimal diagnostic decoder (Python)

The following is an **independently written receiver-side packet parser**, not an excerpt from the closed-source Sender. It only decodes packets; it does **not** solve pose conversion or apply the results to a Blender rig.

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

**Port usage:** If the original GECB Receiver is already listening on UDP port 8985, do not assume that a separate diagnostic process can bind to the same port simultaneously. Stop the existing Receiver during packet inspection, or add logging inside the Receiver instead.

## 5. Two possible approaches to ARP integration

### Approach A — CC-compatible proxy armature (recommended as the first experiment)

```text
Cascadeur: CC-compatible skeleton
          |
          v
Original GECB Sender --> Original protocol --> Blender CC proxy armature
                                                |
                                                | Constraints / retargeting
                                                | with rest-pose alignment
                                                v
                                        ARP deform rig --> Mesh
```

Start with the repository's `SampleCharacter.casc` and `SampleCharacter.blend`, and confirm that the unchanged GECB setup works, including **Zero Calibration**. Then keep a CC-compatible Blender armature as the data receiver and transfer its evaluated pose into the relevant ARP deform bones.

This approach may avoid Sender changes, but **it does not eliminate the rig-conversion problem**. The developer still needs to align rest poses, understand parent spaces, and decide how to apply constraints or matrix offsets.

Also inspect ARP's actual bone roles. Driving **control bones** directly can conflict with IK/FK systems, constraints, or drivers. Driving **deform bones** directly may also be overridden by the ARP rig's evaluation chain. Which target is appropriate must be established on the specific rig.

### Approach B — Map received Bone IDs directly to ARP bones

The Blender Receiver could map the numeric Bone IDs listed below to the corresponding ARP bones. This is conceptually straightforward at the naming layer, but **renaming bones alone is insufficient**.

The substantive tasks are usually:

1. Identify the correct ARP destination bones (control or deform, depending on the setup).
2. Correct for rest-pose differences.
3. Convert quaternion/transform data between appropriate local, parent, and armature spaces.
4. Account for IK/FK, constraints, drivers, and the original GECB Zero Calibration workflow.
5. Verify the final evaluated deformation, not just the raw values assigned by Python.

Both approaches share a limitation: **the Receiver cannot directly recover ARP-specific bone controls or extra degrees of freedom that the Sender never transmitted.** Those must be reconstructed by using the ARP rig's own mechanisms or other logic.

## 6. Suggested validation sequence

1. **Establish a baseline:** run the unmodified GECB sample character in Cascadeur and Blender, including Zero Calibration.
2. **Use one character:** begin with Character ID `0`, without prefixes or multi-character setup.
3. **Check root motion:** inspect Root (`0`) and Hip/Pelvis (`1`), including translation scale and armature transforms.
4. **Test only one arm:** use Clavicle (`10`) → Upperarm (`11`) → Forearm (`12`) → Hand (`13`).
5. **Compare poses:** examine T/A pose, rest-pose offsets, axis directions, parent space, and a few easily recognizable arm rotations.
6. **Inspect ARP evaluation:** identify which bones drive the mesh and where existing constraints or IK/FK behavior override the test pose.
7. **Expand gradually:** test the other arm, legs, neck, fingers, and toes after one chain behaves correctly.
8. **Test multiple characters last:** verify prefixes and Character IDs only after the single-character path is stable.

### Quick troubleshooting

| Symptom | First things to inspect |
|---|---|
| No UDP packets | Is `CC_Base_Hip` or `CC_Base_Pelvis` present in Cascadeur with the required prefix? Is the Sender running? |
| CC sample works, but ARP does not move | Bone ID mapping, destination armature, control/deform bones, constraints |
| Bones move but the pose twists or collapses | Rest pose, local axes, parent spaces, quaternion basis, Zero Calibration |
| Root/Hip translation is wrong | Sender's `0.01` scale factor, Global/Local fallback, Blender object and armature scale |
| Second character is missing | `character1:` prefix and Character ID `1` |
| Some fingers do not move | Corresponding Bone IDs, source bone names, presence of rotation data |

## 7. Sender bone lookup table — 64 Bone IDs

The Sender searches each row's primary name first, then its available alternative names in order. Each name is combined with the character's slot prefix when applicable.

**This is a fixed lookup table, not a dynamic mapping API.** An alias in this table does not override the character-detection requirement described in Section 3.

| Bone ID | Primary source bone name | Alternative lookup names |
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
## 8. What this document establishes — and what it does not

**Confirmed from the original Sender implementation:** character-detection names, slot prefixes, fixed Bone ID lookup, packet layout, UDP destination, data extraction order, fallback behavior, and translation scaling.

**Not established by the Sender alone:** the internals of Blender Receiver pose application and Zero Calibration; the exact structure generated by a particular ARP version or rig preset; a reliable control-bone/deform-bone mapping; the effort required for full-body ARP compatibility; or whether a proposed integration will work in production. These require testing with the actual Blender Receiver and ARP rig.

### Project links

- **First generation — GECB (subject of this document):** https://github.com/TeamGadget-JP/Gadget_Entangle_for_Cascadeur_Blender
- **Second generation — Cascadeur Entangle for Blender (CEB):** introduced Rig-Agnostic and Smart Swizzle workflows. https://github.com/TeamGadget-JP/Cascadeur_Entangle_for_Blender
- **Current successor — Universal Real-Time Sync System (URSS):** a modular, G-HUB-centered synchronization system. https://github.com/TeamGadget-JP/UNIVERSAL_REAL-TIME_SYNC_SYSTEM

If the goal is simply to use a more capable synchronization system, the later projects are worth reviewing. If the goal is to study or extend the original GECB implementation, the constraints above provide a starting point for independent experimentation.

---

**Distribution and licensing:** This document contains interface-level technical information but **does not include the closed-source GECB Sender implementation**. Consult the licenses and distribution terms of the relevant repositories before modifying or redistributing their components. References to Auto-Rig Pro do not imply an official integration, partnership, endorsement, or compatibility certification.
