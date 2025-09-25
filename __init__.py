bl_info = {
    "name": "Store, Reapply and Animate Bone Constraints",
    "author": "Liz",
    "version": (1, 3),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Bone Constraints",
    "description": "Store/reapply constraints, keyframe influences, and bake pose",
    "category": "Rigging",
}

import bpy

from .animation import constrains, rigify

# ----------------------
# UI Panel
# ----------------------

class BONECONSTRAINTS_PT_panel(bpy.types.Panel):
    bl_label = "Bone Constraint Storage"
    bl_idname = "BONECONSTRAINTS_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bone Constraints"

    def draw(self, context):
        layout = self.layout
        layout.operator("boneconstraints.store", icon="COPYDOWN")
        layout.operator("boneconstraints.apply", icon="PASTEDOWN")
        layout.separator()
        layout.operator("boneconstraints.keyframe_influence", icon="KEY_HLT")
        layout.operator("boneconstraints.bake_and_remove", icon="ACTION_TWEAK")
        # layout.operator("boneconstraints.bake_and_removee", icon="ACTION_TWEAK")
        layout.separator()
        layout.operator("boneconstraints.test", icon="KEY_HLT")
        layout.operator("boneconstraints.copy_rig", icon="COPYDOWN")
        layout.operator("boneconstraints.copy_to_mocap_constr", icon="COPYDOWN")
        # layout.operator("boneconstraints.rigify_spine_retarget", icon="COPYDOWN")
        layout.operator("boneconstraints.rigify_spine_retarget", icon="COPYDOWN")
        layout.separator()
        layout.operator("rigify_utils.copy_rig", icon="COPYDOWN")

        


classes = (
    constrains.BONECONSTRAINTS_OT_store,
    constrains.BONECONSTRAINTS_OT_apply,
    constrains.BONECONSTRAINTS_OT_keyframe_influence,
    constrains.BONECONSTRAINTS_OT_bake_and_remove,
    
    rigify.BONECONSTRAINTS_test,
    rigify.BONECONSTRAINTS_OT_Copy_rig,
    rigify.BONECONSTRAINTS_OT_Copy_to_mocap_constrains,
    # rigify.Rigify_spine_retarget,
    rigify.Rigify_spine_retarget,

    rigify.Rigify_utils_Copy_rig,
    BONECONSTRAINTS_PT_panel   
)

# ----------------------
# Registration
# ----------------------

def register():
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "main":
    register()