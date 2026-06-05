bl_info = {
    "name": "Gadget Entangle for Cascadeur/Blender (GECB)",
    "author": "Gadget Entangle",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > GECB",
    "description": "Real-time motion sync and live-calibration from Cascadeur.",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import bpy
import socket
import struct
import threading
import queue
import mathutils
import sys
import json

data_queue = queue.Queue()

# =========================================================
# Core Swizzle Engine
# =========================================================
def apply_swizzle(bone_name, rx, ry, rz, rw):
    if bone_name in ["CC_Base_Pelvis", "CC_Base_L_ToeBase", "CC_Base_R_ToeBase"]:
        return mathutils.Quaternion((rw, rx, rz, -ry)) 
    return mathutils.Quaternion((rw, rx, ry, rz))

# =========================================================
# Live Teaching Calibration Engine
# =========================================================
def tune_rotation(obj, bone_name, q_mapped):
    if "gecb_zero_calib" in obj:
        try:
            calib_data = json.loads(obj["gecb_zero_calib"])
            if bone_name in calib_data["rot"]:
                saved_q = calib_data["rot"][bone_name]
                q_zero_inv = mathutils.Quaternion((saved_q[0], saved_q[1], saved_q[2], saved_q[3]))
                return q_zero_inv @ q_mapped
        except: pass
    return q_mapped

def tune_location(obj, bone_name, px, py, pz):
    dx, dy, dz = px, py, pz
    if "gecb_zero_calib" in obj:
        try:
            calib_data = json.loads(obj["gecb_zero_calib"])
            if bone_name in calib_data["pos"]:
                bp = calib_data["pos"][bone_name]
                dx = px - bp[0]
                dy = py - bp[1]
                dz = pz - bp[2]
        except: pass
        
    scale = 100.0
    if bone_name == "CC_Base_BoneRoot":
        return mathutils.Vector((dx * scale, -dz * scale, dy * scale))
    elif bone_name in ["CC_Base_Hip", "CC_Base_Pelvis"]:
        return mathutils.Vector((dx * scale, dz * scale, -dy * scale))
        
    return mathutils.Vector((0, 0, 0))

# =========================================================
# Network & Streaming Logic
# =========================================================
def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("127.0.0.1", 8985))
        sock.settimeout(1.0)
        sys.gecb_sock = sock
    except:
        sys.gecb_is_listening = False
        return

    while getattr(sys, 'gecb_is_listening', False):
        try:
            data, addr = sock.recvfrom(8192)
            if data.startswith(b'GECB'):
                data_queue.put(data)
        except socket.timeout:
            continue
        except Exception:
            break
            
    try: sock.close()
    except: pass

def apply_transforms():
    if not getattr(sys, 'gecb_is_listening', False): return None 
    
    slots = [
        bpy.context.scene.gecb_slot_0,
        bpy.context.scene.gecb_slot_1,
        bpy.context.scene.gecb_slot_2,
        bpy.context.scene.gecb_slot_3
    ]
    
    bone_mapping = {
        0: "CC_Base_BoneRoot", 1: "CC_Base_Hip", 2: "CC_Base_Waist", 6: "CC_Base_Spine01", 3: "CC_Base_Spine02", 
        4: "CC_Base_NeckTwist01", 7: "CC_Base_NeckTwist02", 5: "CC_Base_Head",
        10: "CC_Base_L_Clavicle", 11: "CC_Base_L_Upperarm", 12: "CC_Base_L_Forearm", 13: "CC_Base_L_Hand",
        20: "CC_Base_R_Clavicle", 21: "CC_Base_R_Upperarm", 22: "CC_Base_R_Forearm", 23: "CC_Base_R_Hand",
        30: "CC_Base_L_Thigh", 31: "CC_Base_L_Calf", 32: "CC_Base_L_Foot", 33: "CC_Base_L_ToeBase",
        40: "CC_Base_R_Thigh", 41: "CC_Base_R_Calf", 42: "CC_Base_R_Foot", 43: "CC_Base_R_ToeBase",
        51: "CC_Base_L_Thumb1", 52: "CC_Base_L_Thumb2", 53: "CC_Base_L_Thumb3",
        54: "CC_Base_L_Index1", 55: "CC_Base_L_Index2", 56: "CC_Base_L_Index3",
        57: "CC_Base_L_Mid1", 58: "CC_Base_L_Mid2", 59: "CC_Base_L_Mid3",
        60: "CC_Base_L_Ring1", 61: "CC_Base_L_Ring2", 62: "CC_Base_L_Ring3",
        63: "CC_Base_L_Pinky1", 64: "CC_Base_L_Pinky2", 65: "CC_Base_L_Pinky3",
        71: "CC_Base_R_Thumb1", 72: "CC_Base_R_Thumb2", 73: "CC_Base_R_Thumb3",
        74: "CC_Base_R_Index1", 75: "CC_Base_R_Index2", 76: "CC_Base_R_Index3",
        77: "CC_Base_R_Mid1", 78: "CC_Base_R_Mid2", 79: "CC_Base_R_Mid3",
        80: "CC_Base_R_Ring1", 81: "CC_Base_R_Ring2", 82: "CC_Base_R_Ring3",
        83: "CC_Base_R_Pinky1", 84: "CC_Base_R_Pinky2", 85: "CC_Base_R_Pinky3",
        91: "CC_Base_L_BigToe1", 92: "CC_Base_L_IndexToe1", 93: "CC_Base_L_MidToe1", 94: "CC_Base_L_RingToe1", 95: "CC_Base_L_PinkyToe1",
        101: "CC_Base_R_BigToe1", 102: "CC_Base_R_IndexToe1", 103: "CC_Base_R_MidToe1", 104: "CC_Base_R_RingToe1", 105: "CC_Base_R_PinkyToe1"
    }
    
    # Process queued packets
    while not data_queue.empty():
        try:
            data = data_queue.get_nowait()
            if len(data) < 5: continue
            
            char_id = data[4]
            if char_id >= len(slots) or not slots[char_id]:
                continue
                
            target_obj = slots[char_id]
            is_calibrating = "gecb_request_calib" in target_obj
            if is_calibrating and not hasattr(sys, f'temp_calib_{char_id}'):
                setattr(sys, f'temp_calib_{char_id}', {"rot": {}, "pos": {}})
            
            offset = 5
            while offset < len(data):
                bone_id = data[offset]
                flags = data[offset+1]
                offset += 2
                
                bone_name = bone_mapping.get(bone_id)
                pbone = target_obj.pose.bones.get(bone_name) if bone_name else None
                
                has_pos = (flags & 2) != 0
                has_rot = (flags & 1) != 0
                
                if has_pos:
                    px, py, pz = struct.unpack_from('<3f', data, offset)
                    offset += 12
                    if is_calibrating and bone_name:
                        getattr(sys, f'temp_calib_{char_id}')["pos"][bone_name] = [px, py, pz]
                    if pbone: pbone.location = tune_location(target_obj, bone_name, px, py, pz)
                        
                if has_rot:
                    rx, ry, rz, rw = struct.unpack_from('<4f', data, offset)
                    offset += 16
                    if pbone:
                        q_mapped = apply_swizzle(bone_name, rx, ry, rz, rw)
                        if is_calibrating and bone_name:
                            q_inv = q_mapped.inverted()
                            getattr(sys, f'temp_calib_{char_id}')["rot"][bone_name] = [q_inv.w, q_inv.x, q_inv.y, q_inv.z]
                        pbone.rotation_mode = 'QUATERNION'
                        pbone.rotation_quaternion = tune_rotation(target_obj, bone_name, q_mapped)
            
            # Save calibration data at the end of packet processing
            if is_calibrating:
                target_obj["gecb_zero_calib"] = json.dumps(getattr(sys, f'temp_calib_{char_id}'))
                del target_obj["gecb_request_calib"]
                delattr(sys, f'temp_calib_{char_id}')
                print(f"[GECB] Calibration saved for {target_obj.name} (Slot {char_id})")
                
        except Exception:
            continue

    if bpy.context.view_layer: bpy.context.view_layer.update() 
    if bpy.context.screen:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D': area.tag_redraw() 

    return 0.016 

# =========================================================
# UI & Operators
# =========================================================
class GECB_OT_ToggleSync(bpy.types.Operator):
    bl_idname = "gecb.toggle_sync"
    bl_label = "Toggle Sync"
    bl_description = "Start/Stop UDP stream from Cascadeur"
    
    def execute(self, context):
        if getattr(sys, 'gecb_is_listening', False):
            sys.gecb_is_listening = False
            if hasattr(sys, 'gecb_sock'):
                try: sys.gecb_sock.close()
                except: pass
            self.report({'INFO'}, "GECB Sync Stopped")
        else:
            sys.gecb_is_listening = True
            threading.Thread(target=udp_listener, daemon=True).start()
            if not bpy.app.timers.is_registered(apply_transforms):
                bpy.app.timers.register(apply_transforms)
            self.report({'INFO'}, "GECB Sync Started")
        return {'FINISHED'}

class GECB_OT_ZeroCalibrate(bpy.types.Operator):
    bl_idname = "gecb.zero_calibrate"
    bl_label = "Zero Calibration"
    bl_description = "Capture current incoming stream as base pose (T-Pose required)"
    bl_options = {'REGISTER', 'UNDO'}
    
    slot_idx: bpy.props.IntProperty()
    
    def invoke(self, context, event):
        if not getattr(sys, 'gecb_is_listening', False):
            self.report({'WARNING'}, "Please START SYNC before calibration.")
            return {'CANCELLED'}
        return context.window_manager.invoke_confirm(self, event)
        
    def execute(self, context):
        slots = [context.scene.gecb_slot_0, context.scene.gecb_slot_1, context.scene.gecb_slot_2, context.scene.gecb_slot_3]
        obj = slots[self.slot_idx]
        if not obj: return {'CANCELLED'}
        
        obj["gecb_request_calib"] = True
        self.report({'INFO'}, "Calibration requested from stream...")
        return {'FINISHED'}

class GECB_OT_ClearCalibrate(bpy.types.Operator):
    bl_idname = "gecb.clear_calibrate"
    bl_label = "Clear Calibration"
    bl_description = "Remove saved calibration data"
    bl_options = {'REGISTER', 'UNDO'}
    
    slot_idx: bpy.props.IntProperty()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        
    def execute(self, context):
        slots = [context.scene.gecb_slot_0, context.scene.gecb_slot_1, context.scene.gecb_slot_2, context.scene.gecb_slot_3]
        obj = slots[self.slot_idx]
        if obj and "gecb_zero_calib" in obj:
            del obj["gecb_zero_calib"]
            self.report({'INFO'}, f"Calibration cleared for {obj.name}")
        return {'FINISHED'}

class GECB_PT_Panel(bpy.types.Panel):
    bl_label = "GECB Sync v1.0"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GECB'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        is_running = getattr(sys, 'gecb_is_listening', False)

        row = layout.row()
        row.scale_y = 2.0
        if is_running:
            row.operator("gecb.toggle_sync", text="STOP SYNC", icon='PAUSE')
        else:
            row.operator("gecb.toggle_sync", text="START SYNC", icon='PLAY')
            
        layout.separator()
        layout.label(text="Character Routing:")

        slots = [("Slot 0", "gecb_slot_0"), ("Slot 1", "gecb_slot_1"), ("Slot 2", "gecb_slot_2"), ("Slot 3", "gecb_slot_3")]
        for i, (label, prop_name) in enumerate(slots):
            box = layout.box()
            box.prop(scene, prop_name, text=label)
            
            obj = getattr(scene, prop_name)
            if obj:
                is_calib = "gecb_zero_calib" in obj
                row_calib = box.row(align=True)
                
                if is_calib:
                    btn = row_calib.operator("gecb.zero_calibrate", text="Calibrated", icon='CHECKMARK')
                    btn.slot_idx = i
                    reset_btn = row_calib.operator("gecb.clear_calibrate", text="", icon='TRASH')
                    reset_btn.slot_idx = i
                else:
                    btn = row_calib.operator("gecb.zero_calibrate", text="Zero Calib (Live Stream)", icon='MESH_DATA')
                    btn.slot_idx = i

classes = (
    GECB_OT_ToggleSync,
    GECB_OT_ZeroCalibrate,
    GECB_OT_ClearCalibrate,
    GECB_PT_Panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.gecb_slot_0 = bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda self, obj: obj.type == 'ARMATURE')
    bpy.types.Scene.gecb_slot_1 = bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda self, obj: obj.type == 'ARMATURE')
    bpy.types.Scene.gecb_slot_2 = bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda self, obj: obj.type == 'ARMATURE')
    bpy.types.Scene.gecb_slot_3 = bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda self, obj: obj.type == 'ARMATURE')

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.gecb_slot_0
    del bpy.types.Scene.gecb_slot_1
    del bpy.types.Scene.gecb_slot_2
    del bpy.types.Scene.gecb_slot_3

if __name__ == "__main__":
    register()