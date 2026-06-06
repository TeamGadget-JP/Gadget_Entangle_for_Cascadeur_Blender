bl_info = {
    "name": "AccuRIG Hip Bone Fix",
    "author": "TeamGadget",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > GECB",
    "description": "Fixes the Hip bone tail alignment for AccuRIG / CC-compatible skeletons.",
    "warning": "",
    "category": "Rigging",
}

import bpy


def fix_accurig_hip(context):
    obj = context.active_object

    if not obj or obj.type != 'ARMATURE':
        return False, "Please select an Armature object before running this tool."

    original_mode = obj.mode

    # Switch to Object Mode first, then enter Edit Mode
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.mode_set(mode='EDIT')
    armature_data = obj.data

    # Find the Hip bone
    hip_names = ["CC_Base_Hip", "CC_Base_Pelvis"]
    hip_bone = None

    for name in hip_names:
        if name in armature_data.edit_bones:
            hip_bone = armature_data.edit_bones[name]
            break

    if not hip_bone:
        bpy.ops.object.mode_set(mode='OBJECT')
        return False, "CC_Base_Hip or CC_Base_Pelvis was not found."

    # Temporarily store child bone information
    children_info = []

    for child in list(hip_bone.children):
        children_info.append({
            "bone": child,
            "use_connect": child.use_connect,
            "head": child.head.copy(),
            "tail": child.tail.copy(),
        })

        # Temporarily detach child bones to prevent unwanted transformation
        child.use_connect = False
        child.parent = None

    before_tail_x = hip_bone.tail.x
    before_tail_y = hip_bone.tail.y

    # Align the Hip bone tail X/Y position to the Hip bone head X/Y position
    # The Z-axis length is preserved
    hip_bone.tail.x = hip_bone.head.x
    hip_bone.tail.y = hip_bone.head.y

    after_tail_x = hip_bone.tail.x
    after_tail_y = hip_bone.tail.y

    # Restore child bones
    for info in children_info:
        child = info["bone"]
        child.parent = hip_bone
        child.use_connect = info["use_connect"]
        child.head = info["head"]
        child.tail = info["tail"]

    # Return to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    message = (
        "Hip bone fix completed. "
        f"Tail X/Y: ({before_tail_x:.6f}, {before_tail_y:.6f}) "
        f"-> ({after_tail_x:.6f}, {after_tail_y:.6f})"
    )

    return True, message


class GECB_OT_FixAccuRIGHip(bpy.types.Operator):
    bl_idname = "gecb.fix_accurig_hip"
    bl_label = "Fix Hip Bone"
    bl_description = "Aligns the AccuRIG Hip bone tail vertically for CC-compatible skeletons"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        success, message = fix_accurig_hip(context)

        if success:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)

        return {'FINISHED'} if success else {'CANCELLED'}


class GECB_PT_HipFixPanel(bpy.types.Panel):
    bl_label = "AccuRIG Hip Fix"
    bl_idname = "GECB_PT_hip_fix_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GECB"

    def draw(self, context):
        layout = self.layout

        layout.label(text="AccuRIG / CC-Compatible Fix")
        layout.operator(
            "gecb.fix_accurig_hip",
            text="Fix Hip Bone",
            icon='BONE_DATA'
        )


classes = (
    GECB_OT_FixAccuRIGHip,
    GECB_PT_HipFixPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()