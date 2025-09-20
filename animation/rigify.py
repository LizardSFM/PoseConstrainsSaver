# For mocap. Copy rig, leave only ORG, reparent them. 

import bpy

# RIGIFY TOOLS
# For mocap. Copy rig, leave only ORG, reparent them. 

# def is_selected_object_armature():
#     selected_objects = bpy.context.selected_objects[0]
#     if not selected_objects:
#         return False
#     return selected_objects[0].type == 'ARMATURE'

# def copy_rig(obj = bpy.context.active_object):
#     # Store current selection
#     # original_selection = bpy.context.selected_objects[0].copy()
#     obj.duplicate()
#     # # Deselect all
#     # bpy.ops.object.select_all(action='DESELECT')
    
#     # # Select only armatures
#     # for obj in original_selection:
#     #     if obj.type == 'ARMATURE':
#     #         obj.select_set(True)
#     #         bpy.context.view_layer.objects.active = obj
    
#     # # Duplicate selected armatures
#     # if bpy.context.selected_objects:
#     #     bpy.ops.object.duplicate()
    
#     # Restore original selection if needed
#     bpy.ops.object.select_all(action='DESELECT')
#     for obj in original_selection:
#         obj.select_set(True)

class BONECONSTRAINTS_OT_Copy_rig(bpy.types.Operator):
    """Copy rigify rig, leave only ORG BONES"""
    bl_idname = "boneconstraints.copy_rig"
    bl_label = "Copy rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        orig_rig, obj = context.active_object
        # obj = context.object
        if obj is None or obj.type != "ARMATURE":
            self.report({'ERROR'}, "Select an armature in Pose Mode")
            return {'CANCELLED'}
        
        bpy.ops.object.duplicate()
        obj = context.active_object

        
        # Cut ORG out as new armature
        org_id = obj.data.collections_all.find("ORG")
        obj.data.collections_all[org_id].is_solo = True
        col = obj.data.collections[org_id]
        bpy.ops.object.editmode_toggle(True)
        # Move feet MCH to ORG for proper retargeting of feet later
        obj.data.collections[org_id].assign(obj.data.edit_bones["MCH-foot_ik.parent.L"])
        obj.data.collections[org_id].assign(obj.data.edit_bones["MCH-foot_ik.parent.R"])
        obj.data.collections["MCH"].unassign(obj.data.edit_bones["MCH-foot_ik.parent.L"])
        obj.data.collections["MCH"].unassign(obj.data.edit_bones["MCH-foot_ik.parent.R"])
        
        obj.data.edit_bones["MCH-foot_ik.parent.L"].parent = obj.data.edit_bones["ORG-foot.L"]
        obj.data.edit_bones["MCH-foot_ik.parent.R"].parent = obj.data.edit_bones["ORG-foot.R"]


        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.separate()
        bpy.ops.object.editmode_toggle(False)
        
        # org_rig = bpy.context.selected_objects[1]
        bpy.data.objects.remove(context.active_object, do_unlink=True)
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        # Make ORG visible
        bpy.ops.armature.collection_remove_unused()
        for i, collection in enumerate(context.active_object.data.collections):
            collection.is_visible = True
            collection.is_solo = False
        
        # Clear constrains and Locks
        bpy.ops.object.posemode_toggle(True)
        for pose_bone in context.active_object.pose.bones:
            bpy.ops.pose.constraints_clear()
            pose_bone.lock_location[0] = False
            pose_bone.lock_location[1] = False
            pose_bone.lock_location[2] = False
            pose_bone.lock_rotation_w = False
            pose_bone.lock_rotation[0] = False
            pose_bone.lock_rotation[1] = False
            pose_bone.lock_rotation[2] = False
            pose_bone.lock_scale[0] = False
            pose_bone.lock_scale[1] = False
            pose_bone.lock_scale[2] = False
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.constraints_clear()
        bpy.ops.object.posemode_toggle(False)

        # Find center bones
        bpy.ops.object.editmode_toggle(True)
        edit_bones = context.active_object.data.edit_bones
        center_bones = []
        for edit_bone in edit_bones:
            if abs(edit_bone.head.x) == 0 and abs(edit_bone.tail.x) == 0:
                center_bones.append(edit_bone)
        # AI Sort bones by their Z position (assuming spine runs vertically) 
        center_bones.sort(key=lambda bone: bone.head.z)

        # Reparent
        for i, edit_bone in enumerate(center_bones):
            if i >= (len(center_bones) - 1): break
            current_bone = center_bones[i]
            next_bone = center_bones[i + 1]
            
            # Check if next bone's head matches current bone's tail
            head_tail_match = (
                abs(next_bone.head.x - current_bone.tail.x) < 0.001 and
                abs(next_bone.head.y - current_bone.tail.y) < 0.001 and
                abs(next_bone.head.z - current_bone.tail.z) < 0.001
            )
            if head_tail_match:
                next_bone.parent = current_bone
                next_bone.use_connect = True
                print(f"Parented '{next_bone.name}' to '{current_bone.name}'")
            else:
                print(f"Warning: '{next_bone.name}' head doesn't match '{current_bone.name}' tail position")
            # bpy.context.active_bone.parent = bpy.data.armatures["rig.012"].edit_bones["ORG-pelvis.L"]
        
        # Specific finger parenting
        edit_bones["ORG-thumb.01.R"].parent = edit_bones["ORG-hand.R"]
        edit_bones["ORG-palm.01.R"].parent = edit_bones["ORG-hand.R"]
        edit_bones["ORG-palm.02.R"].parent = edit_bones["ORG-hand.R"]
        edit_bones["ORG-palm.03.R"].parent = edit_bones["ORG-hand.R"]
        edit_bones["ORG-palm.04.R"].parent = edit_bones["ORG-hand.R"]

        edit_bones["ORG-thumb.01.L"].parent = edit_bones["ORG-hand.L"]
        edit_bones["ORG-palm.01.L"].parent = edit_bones["ORG-hand.L"]
        edit_bones["ORG-palm.02.L"].parent = edit_bones["ORG-hand.L"]
        edit_bones["ORG-palm.03.L"].parent = edit_bones["ORG-hand.L"]
        edit_bones["ORG-palm.04.L"].parent = edit_bones["ORG-hand.L"]
        bpy.ops.object.editmode_toggle(False)
        
        




        # # Making all bones except ORG visible
        # for i, collection in enumerate(obj.data.collections):
        #     collection.is_visible = True

        #     if collection.name == "ORG": collection.is_solo = False
        #     else: collection.is_solo = True

        # # Remove unused bones
        # bpy.ops.object.editmode_toggle(True)
        # bpy.ops.armature.select_all(action='SELECT')
        # bpy.ops.armature.delete()
        # bpy.ops.object.editmode_toggle(False)

        # # Remove solo
        # for i, collection in enumerate(obj.data.collections):
        #     collection.is_visible = True
        #     collection.is_solo = False

        # bpy.ops.armature.collection_remove_unused()





        # bpy.ops.object.editmode_toggle(False)
        self.report({'INFO'}, f"Copied the rig")
        return {'FINISHED'}

