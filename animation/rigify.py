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
        bpy.ops.object.editmode_toggle(True)
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
        


        # Set the new active object
        





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

