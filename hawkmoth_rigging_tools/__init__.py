# see https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts/28505#28505
# if "bpy" in locals():
#     pass

import bpy


# Blender Addon Info #
bl_info = {
    "name": "Hawkmoth Studio Rigging Tools",
    "blender": (2, 80, 0),
    "category": "Animation",
}


class PaintWeightFromSelectedBonesOnly(bpy.types.Operator):
    """This operator assigns automatic weights assuming only selected bones deform currently selected vertex/object.

    Standard 'automatic weights from bones' operator re-calculates weights for selected bones,
    but it assumes unselected bones can also deform the body (those weight are just not being re-calculated).
    This leads to undesired effects when you have additional bones controlling other parts / objects
    (e.g. a bone that controls an earring) - certain vertices can be assigned 0 weight in all groups.

    What this operator does is: mark all bones except for selected as non-deform bones (use_deform = False),
    use automatic weights for weight assignment and then restores bone use_deform property.
    """
    bl_idname = "paint.weight_from_selected_bones_only"
    bl_label = "Weight Paint Selected Bones Only"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.weight_paint_object is None or context.pose_object is None:
            return False
        if not context.selected_pose_bones:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        # define variable types
        bone: bpy.types.Bone

        if not isinstance(context.pose_object.data, bpy.types.Armature):
            self.report({"ERROR"}, "Active pose object is not an armature")
            return {"CANCELLED"}
        rig: bpy.types.Armature = context.pose_object.data

        # save deform bones names
        deform_bone_names = set(map(lambda x: x.name, filter(lambda x: x.use_deform, rig.bones)))
        # only currently selected bones should be set as deform bones
        selected_bone_names = set(map(lambda x: x.name, context.selected_pose_bones))
        for bone in rig.bones:
            bone.use_deform = bone.use_deform and bone.name in selected_bone_names
        # delete currently selected vertices from groups
        # so they are not being influenced by other bones
        bpy.ops.object.vertex_group_remove_from(use_all_groups=True)
        # use automatic weight painting
        bpy.ops.paint.weight_from_bones()
        # restore deform state
        for bone in rig.bones:
            bone.use_deform = bone.name in deform_bone_names
        return {"FINISHED"}


class ObjectVertexGroupLockSelectedBones(bpy.types.Operator):
    """Locks vertex groups that correspond to selected bones."""
    bl_idname = "object.vertex_group_lock_selected_bones"
    bl_label = "Lock Groups"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.weight_paint_object is None or context.pose_object is None:
            return False
        if not context.selected_pose_bones:
            return False
        return True

    def execute(self, context):
        selected_bone_names = set(map(lambda x: x.name, context.selected_pose_bones))
        for vertex_group in context.weight_paint_object.vertex_groups:
            if vertex_group.name in selected_bone_names:
                vertex_group.lock_weight = True
        return {"FINISHED"}


class ObjectVertexGroupUnlockSelectedBones(bpy.types.Operator):
    """Unlocks vertex groups that correspond to selected bones."""
    bl_idname = "object.vertex_group_unlock_selected_bones"
    bl_label = "Unlock Groups"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.weight_paint_object is None or context.pose_object is None:
            return False
        if not context.selected_pose_bones:
            return False
        return True

    def execute(self, context):
        selected_bone_names = set(map(lambda x: x.name, context.selected_pose_bones))
        for vertex_group in context.weight_paint_object.vertex_groups:
            if vertex_group.name in selected_bone_names:
                vertex_group.lock_weight = False
        return {"FINISHED"}


class WeightPaintingPanel(bpy.types.Panel):
    bl_idname = "ANIMATION_PT_hawkmoth_weight_painting"
    bl_label = "Weight Painting"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hawkmoth Rigging"

    def draw(self, context: bpy.types.Context):
        row = self.layout.row()
        row.operator("paint.weight_from_selected_bones_only")
        row = self.layout.row()
        row.scale_x = 0.5
        row.operator("object.vertex_group_lock_selected_bones")
        row.operator("object.vertex_group_unlock_selected_bones")


classes = (
    PaintWeightFromSelectedBonesOnly,
    ObjectVertexGroupLockSelectedBones,
    ObjectVertexGroupUnlockSelectedBones,
    WeightPaintingPanel,
)
register, unregister = bpy.utils.register_classes_factory(classes)
