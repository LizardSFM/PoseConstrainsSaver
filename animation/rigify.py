# For mocap. Copy rig, leave only ORG, reparent them. 

import bpy
from mathutils import Vector, geometry


class BONECONSTRAINTS_OT_Copy_rig(bpy.types.Operator):
    """Copy rigify rig, leave only ORG BONES"""
    bl_idname = "boneconstraints.copy_rig"
    bl_label = "Copy rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.active_object
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
        
        # Not needed
        # obj.data.edit_bones.remove(obj.data.edit_bones["ORG-breast.L"])
        # obj.data.edit_bones.remove(obj.data.edit_bones["ORG-breast.R"])
        obj.data.edit_bones.remove(obj.data.edit_bones["ORG-pelvis.L"])
        obj.data.edit_bones.remove(obj.data.edit_bones["ORG-pelvis.R"])

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
            if abs(edit_bone.head.x) < 0.001 and abs(edit_bone.tail.x) < 0.001:
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

class BONECONSTRAINTS_OT_Copy_to_mocap_constrains(bpy.types.Operator):
    """Creates bindings from Mocap to Copy. Select Copy of Rigify, then mocap, """
    bl_idname = "boneconstraints.copy_to_mocap_constr"
    bl_label = "Mocap/copy bind"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if len(context.selected_objects) < 2:
            self.report({'ERROR'}, "Select two armatures, one is Rigify copy, other is mocap")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        
        copy = context.selected_objects[0]
        mocap = context.selected_objects[1]
        id = copy.data.collections_all.find("ORG")
        if copy.data.collections_all.find("ORG") == -1:
            copy = context.selected_objects[1]
            mocap = context.selected_objects[0]

        # Setting constrains
        bpy.ops.object.posemode_toggle(True)
        bpy.ops.pose.select_all(action='DESELECT')
        # Select all bones in the first rig
        for bone in copy.data.bones:
            bone.select = True

        bone_binds = {
            "ORG-upper_arm.R" : "RightShoulder",
            "ORG-upper_arm.R" : "RightArm",
            "ORG-forearm.R" : "RightForeArm",
            "ORG-hand.R" : "RightHand",
            "ORG-thigh.R" : "RightUpLeg",
            "ORG-shin.R" : "RightLeg",
            "ORG-foot.R" : "RightFoot",
            "ORG-toe.R" : "RightToeBase",

            "ORG-shoulder.L" : "LeftShoulder",
            "ORG-upper_arm.L" : "LeftArm",
            "ORG-forearm.L" : "LeftForeArm",
            "ORG-hand.L" : "LeftHand",
            "ORG-thigh.L" : "LeftUpLeg",
            "ORG-shin.L" : "LeftLeg",
            "ORG-foot.L" : "LeftFoot",
            "ORG-toe.L" : "LeftToeBase",

            "ORG-spine" : "Hips",
            "" : "",
            "" : "",
            "" : "",
            "" : "",
            "" : "",
            "" : "",
            "" : "",
            "" : "",
        }
        count = 0
        for bone in context.selected_pose_bones:
            if bone.name not in bone_binds:
                continue
            con = bone.constraints.new('COPY_ROTATION')
            con.target = mocap
            con.subtarget = bone_binds[bone.name]

            # setattr(con, "target_space", 'LOCAL_OWNER_ORIENT')
            con.target_space = 'LOCAL_OWNER_ORIENT'
            con.owner_space = 'LOCAL'
            con.influence = 1.0
            con.mix_mode = 'AFTER'
            
            print(con)
            count += 1

        # Hips location bind
        for bone in context.selected_pose_bones:
            if bone.name != "ORG-spine":
                continue
            con = bone.constraints.new('COPY_LOCATION')
            con.target = mocap
            con.subtarget = "Hips"

            # setattr(con, "target_space", 'LOCAL_OWNER_ORIENT')
            con.target_space = 'LOCAL_OWNER_ORIENT'
            con.owner_space = 'LOCAL'
            con.influence = 1.0
            con.use_offset = True # allows moving around

        self.report({'INFO'}, f"{count} bindings added")
        return {'FINISHED'}

def find_centered_bones(bones):
    center_bones = []
    for bone in bones:
        if abs(bone.head.x) < 0.001 and abs(bone.tail.x) < 0.001:
            center_bones.append(bone)
    # AI Sort bones by their Z position (assuming spine runs vertically) 
    center_bones.sort(key=lambda bone: bone.head.z)
    return center_bones

# class Rigify_spine_retarget(bpy.types.Operator):
#     """Find spine bones close to other rig's spine bones, and retarget"""
#     bl_idname = "boneconstraints.rigify_spine_retarget"
#     bl_label = "Spine retarget"
#     bl_options = {'REGISTER', 'UNDO'}
#     def execute(self, context):
#         # Reference position (world space)
#         target_pos = Vector((0.0, 0.0, 1.5))

#         # Get armature object
#         arm = bpy.context.object
#         if arm.type != 'ARMATURE':
#             self.report({'ERROR'}, "Select two armatures, one is Rigify copy, other is mocap")
#             return {'CANCELLED'}
#         bpy.ops.object.editmode_toggle(True)
#         bpy.ops.armature.select_all(action='SELECT')
#         bones = context.object.data.edit_bones

#         closest_bone = None
#         closest_dist = float('inf')

#         count = 0
#         for bone in bones:
#             # Bone head position in world space
#             # head_world = arm.matrix_world @ bone.head
#             # tail_world = arm.matrix_world @ bone.tail

#             # Distance to head
#             dist_head = (bone.head - target_pos).length
#             # Distance to tail
#             dist_tail = (bone.tail - target_pos).length

#             # Use whichever is closer
#             dist = min(dist_head, dist_tail)

#             if dist < closest_dist:
#                 closest_dist = dist
#                 closest_bone = bone
#         bpy.ops.object.mode_set(mode='OBJECT')
#         # print("Closest bone:", closest_bone.name if closest_bone else None)
#         # print("Distance:", closest_dist)
#         self.report({'INFO'}, f"Closest bone: {closest_bone.name}, Distance: {closest_dist}")
#         return {'FINISHED'}
    

# def closest_bone_between_rigs(rig_a, rig_b):
#     """
#     Finds, for each bone in rig_a (edit mode), the closest bone in rig_b
#     based on head/tail positions.
#     """

#     # Matrices for local->world transforms
#     mat_a = rig_a.matrix_world
#     mat_b = rig_b.matrix_world

#     results = {}

#     for bone_a in rig_a.data.edit_bones:
#         # Bone A head/tail in world space
#         head_a = mat_a @ bone_a.head
#         tail_a = mat_a @ bone_a.tail

#         closest_bone = None
#         closest_dist = float("inf")

#         for bone_b in rig_b.data.edit_bones:
#             # Bone B head/tail in world space
#             head_b = mat_b @ bone_b.head
#             tail_b = mat_b @ bone_b.tail

#             # Compute pairwise distances
#             dists = [
#                 (head_a - head_b).length,
#                 (head_a - tail_b).length,
#                 (tail_a - head_b).length,
#                 (tail_a - tail_b).length,
#             ]
#             dist = min(dists)

#             if dist < closest_dist:
#                 closest_dist = dist
#                 closest_bone = bone_b

#         results[bone_a.name] = (closest_bone.name if closest_bone else None, closest_dist)

#     return results

def find_closest_bone(current_bone, other_bones):
    closest_bone = None
    closest_dist = float('inf')

    # Use the midpoint of current bone as reference
    current_mid = (current_bone.head + current_bone.tail) * 0.5

    for bone in other_bones:
        # Midpoint of candidate bone
        bone_mid = (bone.head + bone.tail) * 0.5

        # Distance between midpoints
        dist = (bone_mid - current_mid).length

        if dist < closest_dist:
            closest_dist = dist
            closest_bone = bone

    return closest_bone, closest_dist

class Rigify_spine_retarget(bpy.types.Operator):
    """Find spine bones close to other rig's spine bones, and retarget"""
    bl_idname = "boneconstraints.rigify_spine_retarget"
    bl_label = "Spine retarget"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if len(context.selected_objects) < 2:
            self.report({'ERROR'}, "Select two armatures, one is Rigify copy, other is mocap")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        
        copy = context.selected_objects[0]
        mocap = context.selected_objects[1]
        id = copy.data.collections_all.find("ORG")
        if copy.data.collections_all.find("ORG") == -1:
            copy = context.selected_objects[1]
            mocap = context.selected_objects[0]
        
        bpy.ops.object.editmode_toggle(True)
        # bpy.ops.object.mode_set(mode="EDIT")
        # bpy.context.view_layer.objects.active = mocap # not required
        bpy.ops.armature.select_all(action='SELECT')
        # Get center bones for copy rigify rig
        bones_copy = find_centered_bones(copy.data.edit_bones)
        bones_mocap = find_centered_bones(mocap.data.edit_bones)
        for bone_copy in bones_copy:
            closest_bone, closest_dist = find_closest_bone(bone_copy, bones_mocap)
            self.report({'INFO'}, f"{bone_copy.name} - Closest: {closest_bone.name}, dist: {closest_dist:.4f}")
        # for bone in bones_copy:
        #     self.report({'INFO'}, f"Center bone mocap: {bone.name}")
        # Get center bones for mocap

        # for bone in bones_mocap:
        #     self.report({'INFO'}, f"Center bone mocap: {bone.name}")

        ## Call function
        # closest_map = closest_bone_between_rigs(arm, rig_b)

        # for bone_a, (bone_b, dist) in closest_map.items():
        #     self.report({'INFO'}, f"{bone_a} -> {bone_b} (dist {dist:.4f})")
            # print(f"{bone_a} -> {bone_b} (dist {dist:.4f})")

        # self.report({'INFO'}, f"Closest bone: {closest_bone.name}, Distance: {closest_dist}")
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}