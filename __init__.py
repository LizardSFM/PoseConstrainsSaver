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
from bpy.props import StringProperty

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
        layout.operator("rigify_utils.copy_rig2", icon="COPYDOWN")
        layout.operator("rigify_utils.copy_rig3", icon="COPYDOWN")
        layout.operator("rigify_utils.copy_rig4", icon="COPYDOWN")

        props = context.scene.my_addon_props

        # bone inputs
        # layout.prop(props, "my_text")  # This creates the text input field
        layout.separator()
        layout.prop(props, "usr_torso")
        layout.prop(props, "usr_hand_l")
        layout.prop(props, "usr_hand_r")
        layout.prop(props, "usr_foot_l")
        layout.prop(props, "usr_foot_r")

        layout.separator()
        layout.prop(props, "mch_torso")
        layout.prop(props, "mch_hand_l")
        layout.prop(props, "mch_hand_r")
        layout.prop(props, "mch_foot_l")
        layout.prop(props, "mch_foot_r")

        layout.separator()
        layout.prop(props, "org_spine")
        layout.prop(props, "org_hand_l")
        layout.prop(props, "org_hand_r")
        layout.prop(props, "org_foot_l")
        layout.prop(props, "org_foot_r")
        layout.separator()
        layout.prop(props, "org_shoulder_r")
        layout.prop(props, "org_upper_arm_r")
        layout.prop(props, "org_forearm_r")
        layout.prop(props, "org_thigh_r")
        layout.prop(props, "org_shin_r")
        layout.prop(props, "org_toe_r")
        layout.separator()
        layout.prop(props, "org_shoulder_l")
        layout.prop(props, "org_upper_arm_l")
        layout.prop(props, "org_forearm_l")
        layout.prop(props, "org_thigh_l")
        layout.prop(props, "org_shin_l")
        layout.prop(props, "org_toe_l")
        # layout.prop_search(item, 'bone_name_target', armature_target.pose, "bones", text='')
        # layout.prop(context.scene, 'rsl_retargeting_armature_source', icon='ARMATURE_DATA')

# context.scene.my_addon_props.my_text


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
    rigify.Rigify_utils_Copy_rig2,
    rigify.Rigify_utils_Copy_rig3,
    rigify.Rigify_utils_Copy_rig4,
    rigify.MyAddonProperties,


    BONECONSTRAINTS_PT_panel   
)

# ----------------------
# Registration
# ----------------------

def register():
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon_props = bpy.props.PointerProperty(type=rigify.MyAddonProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_addon_props
    
if __name__ == "main":
    register()