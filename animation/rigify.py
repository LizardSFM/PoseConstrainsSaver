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

## REWORK 
## TODO: Implement menu for manual input of bones (feet, hand IK, torso, neck etc)
# if rigify rig was customized and bone names changed

## TODO: clear constrains when copying, and back to pose position
class Rigify_utils_Copy_rig(bpy.types.Operator):
    """Copy rigify rig, leave ORG and MCH bones. It should follow mocap rig"""
    bl_idname = "rigify_utils.copy_rig"
    bl_label = "Copy rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.active_object
        orig_obj = context.active_object
        orig_name = context.active_object.name

        if obj is None or obj.type != "ARMATURE" or obj.data.collections_all.find("Torso (Tweak)") == -1:
            self.report({'ERROR'}, "Select a rigify armature")
            return {'CANCELLED'}
        
        bpy.ops.object.duplicate()
        obj = context.active_object

        
        # Cut ORG out as new armature
        org_id = obj.data.collections_all.find("ORG")
        obj.data.collections_all[org_id].name = ("ORG-mocap")
        obj.data.collections_all[org_id].is_solo = True
        col = obj.data.collections[org_id]
        bpy.ops.object.editmode_toggle(True)

        # Cut and edit the neck (reduce from 2 bones to 1)

        # Move feet MCH to MCH-mocap for proper retargeting of feet later
        obj.data.collections.new("MCH-mocap")
        obj.data.collections_all["MCH-mocap"].is_solo = True
        # Name of bone, their new parent, 1 if parent should lose parent
        mchbones = {"MCH-foot_ik.parent.L": ["ORG-foot.L", False],
                    "MCH-foot_ik.parent.R": ["ORG-foot.R", False],
                    "MCH-hand_ik.parent.R": ["ORG-hand.R", False],
                    "MCH-hand_ik.parent.L": ["ORG-hand.L", False],
                    "MCH-torso.parent": ["ORG-spine", True]}
        for bone_name, parent_data in mchbones.items():
            parent_name = parent_data[0]
            parent_loses_parent = parent_data[1]
            bone = obj.data.edit_bones[bone_name]
            parent = obj.data.edit_bones[parent_name]

            obj.data.collections["MCH-mocap"].assign(bone)
            obj.data.collections["MCH"].unassign(bone)
            if parent_loses_parent:
                parent.parent = None
            bone.parent = parent
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

        obj.data.pose_position = 'POSE'
        obj.name = orig_name + "-copy-org-mch"
        orig_obj.select_set(True)
        self.report({'INFO'}, f"Copied the rig")
        return {'FINISHED'}

## TODO: clear constrains when copying, and back to pose position
class Rigify_utils_Copy_rig2(bpy.types.Operator):
    """Copy rigify rig, attach it to copy-org-mch"""
    bl_idname = "rigify_utils.copy_rig2"
    bl_label = "Copy rigify rig2"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        if len(context.selected_objects) < 2:
            self.report({'ERROR'}, "Select two armatures, one is Rigify copy, other is copy-org-mch")
            return {'CANCELLED'}
        
        
        orig = context.selected_objects[0]
        copy_org = context.selected_objects[1]
        if orig.data.collections_all.find("Torso (Tweak)") == -1:
            orig = context.selected_objects[1]
            copy_org = context.selected_objects[0]
        
        # Duplicate rigify rig for attaching to copy-org-mch
        bpy.ops.object.select_all(action='DESELECT')
        orig.select_set(True)
        bpy.context.view_layer.objects.active = orig
        bpy.ops.object.duplicate()

        copy = bpy.context.active_object
        copy.name = orig.name + "-copy"

        # Iterating over bones
        bpy.ops.object.posemode_toggle(True)
        bpy.context.object.data.collections_all["MCH"].is_visible = True
        bpy.ops.pose.select_all(action='SELECT')
        # name, copy from, 1 copy location, 1 copy rotation
        bone_binds = {"MCH-torso.parent": ["MCH-torso.parent", 1,1],
                      "MCH-hand_ik.parent.R": ["MCH-hand_ik.parent.R", 1,1],
                      "MCH-hand_ik.parent.L": ["MCH-hand_ik.parent.L", 1,1],
                      "foot_ik.R": ["MCH-foot_ik.parent.R", 1,1],
                      "foot_ik.L": ["MCH-foot_ik.parent.L", 1,1],}
        
        for bone in context.selected_pose_bones:
            if bone.name not in bone_binds:
                continue
            params = bone_binds[bone.name]
            parent = params[0]
            copy_loc = params[1]
            copy_rot = params[2]

            if copy_loc:
                con = bone.constraints.new('COPY_LOCATION')
                con.name = con.name + "-mocap"
                con.target = copy_org
                con.subtarget = parent
            if copy_rot:
                con = bone.constraints.new('COPY_ROTATION')
                con.name = con.name + "-mocap"
                con.target = copy_org
                con.subtarget = parent


        # find Torso tweak bones (spine_fk)
        bpy.context.object.data.collections_all["Torso (Tweak)"].is_solo = True
        bpy.ops.pose.select_all(action='SELECT')
        spine_fk = []
        for bone in context.selected_pose_bones:
            if bone.name.startswith("spine_fk"):
                print(f"found - {bone.name}")
                spine_fk.append(bone)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        # copy.select_set(True)
        copy_org.select_set(True)
        bpy.context.view_layer.objects.active = copy_org

        # Find chest bones of copy_org for later attachments
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.object.data.collections_all["ORG-mocap"].is_solo = True
        bpy.ops.pose.select_all(action='SELECT')
        center_bones = find_centered_bones(context.selected_pose_bones)
        bpy.context.object.data.collections_all["ORG-mocap"].is_solo = False
        # print("Center bones")
        # for bone in center_bones:
        #     print(bone.name)

        # Get spine_fk on the screen
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        copy.select_set(True)
        bpy.context.view_layer.objects.active = copy

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        # Now attaching
        for pose_bone in spine_fk:
            bone = pose_bone.bone
            bone.select = True
            for center_pose_bone in center_bones:
                center_bone = center_pose_bone.bone
                if (bone.head_local - center_bone.tail_local).length <= 0.0001:
                    con = pose_bone.constraints.new('COPY_ROTATION')
                    con.name = con.name + "-mocap"
                    con.target = copy_org
                    con.subtarget = center_bone.name

        bpy.context.object.data.collections_all["Torso (Tweak)"].is_solo = False



        bpy.context.object.data.collections_all["MCH"].is_visible = False
        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, f"Copied the rig")
        return {'FINISHED'}
    
