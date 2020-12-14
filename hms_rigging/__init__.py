###
# Hawkmoth Studio Blender Tools
# Copyright (C) 2020 Hawkmoth Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###


import bpy

bl_info = {
    'name': 'Hawkmoth Studio: Rigging',
    'author': 'Vitaly Ogoltsov',
    'wiki_url': 'https://github.com/hawkmoth-studio/blender-tools/wiki',
    'tracker_url': 'https://github.com/hawkmoth-studio/blender-tools/issues',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'View 3D > Tool Shelf > Hawkmoth Studio',
    'category': 'Game Development'
}


class HMS_RIGGING_prefs(bpy.types.PropertyGroup):
    """Rigging tools preferences."""
    pass


class HMS_RIGGING_OT_weight_from_selected_bones_only(bpy.types.Operator):
    """This operator assigns automatic weights assuming only selected bones deform currently selected vertex/object.

    Standard 'automatic weights from bones' operator re-calculates weights for selected bones,
    but it assumes unselected bones can also deform the body (those weight are just not being re-calculated).
    This leads to undesired effects when you have additional bones controlling other parts / objects
    (e.g. a bone that controls an earring) - certain vertices can be assigned 0 weight in all groups.

    What this operator does is: mark all bones except for selected as non-deform bones (use_deform = False),
    use automatic weights for weight assignment and then restores bone use_deform property.
    """
    bl_idname = "hms_rigging.weight_from_selected_bones_only"
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
        try:
            # only currently selected bones should be set as deform bones
            selected_bone_names = set(map(lambda x: x.name, context.selected_pose_bones))
            for bone in rig.bones:
                bone.use_deform = bone.use_deform and bone.name in selected_bone_names
            # delete currently selected vertices from groups
            # so they are not being influenced by other bones
            bpy.ops.object.vertex_group_remove_from(use_all_groups=True)
            # use automatic weight painting
            bpy.ops.paint.weight_from_bones()
        finally:
            # restore deform state
            for bone in rig.bones:
                bone.use_deform = bone.name in deform_bone_names
        return {"FINISHED"}


class HMS_RIGGING_OT_vertex_group_lock_selected_bones(bpy.types.Operator):
    """Locks vertex groups that correspond to selected bones."""
    bl_idname = "hms_rigging.vertex_group_lock_selected_bones"
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


class HMS_RIGGING_OT_vertex_group_unlock_selected_bones(bpy.types.Operator):
    """Unlocks vertex groups that correspond to selected bones."""
    bl_idname = "hms_rigging.vertex_group_unlock_selected_bones"
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


class HMS_RIGGING_PT_main(bpy.types.Panel):
    bl_idname = "HMS_RIGGING_PT_main"
    bl_category = "HMS: Rigging"
    bl_label = "Weight Painting"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context: bpy.types.Context):
        prefs: HMS_RIGGING_prefs = context.scene.hms_rigging

        row = self.layout.row()
        row.operator(HMS_RIGGING_OT_weight_from_selected_bones_only.bl_idname)

        row = self.layout.row()
        row.scale_x = 0.5
        row.operator(HMS_RIGGING_OT_vertex_group_lock_selected_bones.bl_idname)
        row.operator(HMS_RIGGING_OT_vertex_group_unlock_selected_bones.bl_idname)


classes = (
    HMS_RIGGING_prefs,
    HMS_RIGGING_OT_weight_from_selected_bones_only,
    HMS_RIGGING_OT_vertex_group_lock_selected_bones,
    HMS_RIGGING_OT_vertex_group_unlock_selected_bones,
    HMS_RIGGING_PT_main,
)
register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    # Register all classes.
    register_classes()
    # Create addon-level properties object.
    bpy.types.Scene.hms_rigging = bpy.props.PointerProperty(type=HMS_RIGGING_prefs)


def unregister():
    unregister_classes()
