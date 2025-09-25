# For mocap. Copy rig, leave only ORG, reparent them. 

import bpy
# from mathutils import Vector, geometry
class BONECONSTRAINTS_test(bpy.types.Operator):
    """Just test for debug"""
    bl_idname = "boneconstraints.test"
    bl_label = "Test"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        return {'FINISHED'}  
    
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
            "ORG-shoulder.R" : "RightShoulder",
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

            ## Local doesn't really work if rigify bones aren't straight
            # setattr(con, "target_space", 'LOCAL_OWNER_ORIENT')
            # con.target_space = 'LOCAL_OWNER_ORIENT'
            # con.owner_space = 'LOCAL'
            # con.influence = 1.0
            # con.mix_mode = 'AFTER'
            
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

        bpy.ops.object.mode_set(mode='OBJECT')
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
        bones_pairs = {}
        for bone_copy in bones_copy:
            closest_bone, closest_dist = find_closest_bone(bone_copy, bones_mocap)
            bones_pairs[bone_copy.name] = [closest_bone.name, closest_dist]
            self.report({'INFO'}, f"{bone_copy.name} - Closest: {closest_bone.name}, dist: {closest_dist:.4f}")
        


        bpy.ops.object.posemode_toggle(True)
        bpy.ops.pose.select_all(action='DESELECT')
        # Select all bones in the first rig
        for bone in copy.data.bones:
            if bone.name in bones_pairs:
                bone.select = True
        
        for bone in context.selected_pose_bones:
        # for bone, pair in bones_pairs.items():
            con = bone.constraints.new('COPY_ROTATION')
            con.target = mocap
            con.subtarget = bones_pairs[bone.name][0]

            # copypaste
            ## Local doesn't really work if rigify bones aren't straight
            # setattr(con, "target_space", 'LOCAL_OWNER_ORIENT')
            # con.target_space = 'LOCAL_OWNER_ORIENT'
            # con.owner_space = 'LOCAL'
            # con.influence = 1.0
            # con.mix_mode = 'AFTER'
            
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class Rigify_utils_Copy_rig(bpy.types.Operator):
    """Copy rigify rig, leave """
    bl_idname = "rigify_utils.copy_rig"
    bl_label = "Copy rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.active_object
        orig_name = context.active_object.name
        # obj = context.object
        if obj is None or obj.type != "ARMATURE":
            self.report({'ERROR'}, "Select an armature in Pose Mode")
            return {'CANCELLED'}
        
        bpy.ops.object.duplicate()
        obj = context.active_object

        
        # Cut ORG out as new armature
        org_id = obj.data.collections_all.find("ORG")
        obj.data.collections_all[org_id].name = ("ORG-mocap")
        obj.data.collections_all[org_id].is_solo = True
        col = obj.data.collections[org_id]
        bpy.ops.object.editmode_toggle(True)
        # Move feet MCH to MCH-mocap for proper retargeting of feet later
        obj.data.collections.new("MCH-mocap")
        obj.data.collections_all["MCH-mocap"].is_solo = True
        mchbones = {"MCH-foot_ik.parent.L": "ORG-foot.L",
                    "MCH-foot_ik.parent.R": "ORG-foot.R",
                    "MCH-hand_ik.parent.R": "ORG-hand.R",
                    "MCH-hand_ik.parent.L": "ORG-hand.L",
                    "MCH-torso.parent": "ORG-spine"}
        for bone, parent in mchbones.items():
            obj.data.collections["MCH-mocap"].assign(obj.data.edit_bones[bone])
            obj.data.collections["MCH"].unassign(obj.data.edit_bones[bone])
            obj.data.edit_bones[bone].parent = obj.data.edit_bones[parent]
        # obj.data.collections_all["MCH-mocap"].is_solo = False
        
        # Not needed
        # obj.data.edit_bones.remove(obj.data.edit_bones["ORG-breast.L"])
        # obj.data.edit_bones.remove(obj.data.edit_bones["ORG-breast.R"])
        obj.data.edit_bones.remove(obj.data.edit_bones["ORG-pelvis.L"])
        obj.data.edit_bones.remove(obj.data.edit_bones["ORG-pelvis.R"])

        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.separate()
        bpy.ops.object.editmode_toggle(False)

        # org_rig = bpy.context.selected_objects[1]
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        obj = context.active_object
        # Make ORG visible
        bpy.ops.armature.collection_remove_unused()
        for i, collection in enumerate(obj.data.collections):
            collection.is_visible = True
            collection.is_solo = False
        
        # Clear constrains and Locks
        bpy.ops.object.posemode_toggle(True)
        for pose_bone in obj.pose.bones:
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
        edit_bones = obj.data.edit_bones

        # Find only ORG bones
        org_bones = []
        for bone in edit_bones:
            cols = bone.collections
            for col in cols:
                if col.name == "ORG-mocap": org_bones.append(bone)
        center_bones = find_centered_bones(org_bones)
        
        # Reparent. Need to only be used on ORG
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
                # next_bone.use_connect = True
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
        
        obj.name = orig_name + "-copy"
        self.report({'INFO'}, f"Copied the rig")
        return {'FINISHED'}

