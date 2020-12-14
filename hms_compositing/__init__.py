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
    'name': 'Hawkmoth Studio: Compositing',
    'author': 'Vitaly Ogoltsov',
    'wiki_url': 'https://github.com/hawkmoth-studio/blender-tools/wiki',
    'tracker_url': 'https://github.com/hawkmoth-studio/blender-tools/issues',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'View 3D > Tool Shelf > Hawkmoth Studio',
    'category': 'Game Development'
}


class HMS_COMPOSITING_prefs(bpy.types.PropertyGroup):
    """Compositing tools preferences."""
    vertex_colors_layer_name: bpy.props.StringProperty(
        name='Layer name',
        description='Vertex color layer name to be used for vertex painting',
        default='Col'
    )
    vertex_color: bpy.props.FloatVectorProperty(
        name='Color',
        subtype='COLOR',
        default=[1, 1, 1, 1],
        size=4,
        min=0, max=1,
    )


class HMS_COMPOSITING_OT_vertex_color_pick(bpy.types.Operator):
    """Operator used to pick color from currently selected object / vertices."""
    bl_idname = 'hms_compositing.vertex_color_pick'
    bl_label = 'Pick color'
    bl_description = 'Pick color from currently selected object / vertices'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        active_object: bpy.types.Object = context.view_layer.objects.active
        if active_object is None or active_object.type != 'MESH':
            return False
        return True

    def execute(self, context: bpy.types.Context):
        prefs: HMS_COMPOSITING_prefs = context.scene.hms_compositing

        active_object: bpy.types.Object = context.view_layer.objects.active
        mesh: bpy.types.Mesh = active_object.data

        # Vertex colors can only be accessed programmatically when in object mode.
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Check if in edit mode and any vertices are selected.
        # Must be done *after* going into object mode or vertex selection will not be updated.
        selected_vertices = []
        if mode == 'EDIT':
            selected_vertices = [v.index for v in mesh.vertices if v.select]

        try:
            # Find vertex colors set.
            vertex_colors_layer: bpy.types.MeshLoopColorLayer = None
            if mesh.vertex_colors:
                if mesh.vertex_colors.active.name == prefs.vertex_colors_layer_name:
                    vertex_colors_layer = mesh.vertex_colors.active
                else:
                    vertex_colors_layer = next((vc for vc in mesh.vertex_colors if vc.name == prefs.vertex_colors_layer_name), None)
            # Create new vertex colors set if not found.
            if vertex_colors_layer is None:
                self.report({'WARNING'}, 'Currently selected object does not have vertex colors')
                return {'CANCELLED'}

            # Pick vertex color.
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    # Paint only selected vertices, if any. Otherwise, pain whole mesh.
                    if not selected_vertices or mesh.loops[loop_index].vertex_index in selected_vertices:
                        context.scene.hms_compositing.vertex_color = vertex_colors_layer.data[loop_index].color
                        return {'FINISHED'}

            self.report({'WARNING'}, 'Could not find any vertices to pick color from')
            return {'CANCELLED'}
        finally:
            # Restore mode.
            bpy.ops.object.mode_set(mode=mode)


class HMS_COMPOSITING_OT_vertex_color_fill(bpy.types.Operator):
    """Operator used to fill currently selected object / vertices with color."""
    bl_idname = 'hms_compositing.vertex_color_fill'
    bl_label = 'Fill color'
    bl_description = 'Fill currently selected object / vertices'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        active_object: bpy.types.Object = context.view_layer.objects.active
        if active_object is None or active_object.type != 'MESH':
            return False
        return True

    def execute(self, context: bpy.types.Context):
        prefs: HMS_COMPOSITING_prefs = context.scene.hms_compositing

        active_object: bpy.types.Object = context.view_layer.objects.active
        mesh: bpy.types.Mesh = active_object.data

        # Vertex colors can only be accessed programmatically when in object mode.
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Check if in edit mode and any vertices are selected.
        # Must be done *after* going into object mode or vertex selection will not be updated.
        selected_vertices = []
        if mode == 'EDIT':
            selected_vertices = [v.index for v in mesh.vertices if v.select]

        try:
            # Find vertex colors set.
            vertex_colors_layer: bpy.types.MeshLoopColorLayer = None
            if mesh.vertex_colors:
                if mesh.vertex_colors.active.name == prefs.vertex_colors_layer_name:
                    vertex_colors_layer = mesh.vertex_colors.active
                else:
                    vertex_colors_layer = next((vc for vc in mesh.vertex_colors if vc.name == prefs.vertex_colors_layer_name), None)
            # Create new vertex colors set if not found.
            if vertex_colors_layer is None:
                vertex_colors_layer = mesh.vertex_colors.new(name=prefs.name, do_init=True)
            else:
                vertex_colors_layer.active = True

            # Assign vertex color.
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    # Paint only selected vertices, if any. Otherwise, pain whole mesh.
                    if not selected_vertices or mesh.loops[loop_index].vertex_index in selected_vertices:
                        vertex_colors_layer.data[loop_index].color = context.scene.hms_compositing.vertex_color

            return {'FINISHED'}
        finally:
            # Restore mode.
            bpy.ops.object.mode_set(mode=mode)


class HMS_COMPOSITING_PT_main(bpy.types.Panel):
    """Compositing tools main panel."""
    bl_category = "HMS: Compositing"
    bl_label = "Vertex Painting"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context: bpy.types.Context):
        prefs: HMS_COMPOSITING_prefs = context.scene.hms_compositing

        self.layout.use_property_split = True

        row = self.layout.row()
        row.prop(prefs, 'vertex_colors_layer_name')

        row = self.layout.row()
        row.prop(prefs, 'vertex_color')

        row = self.layout.row()
        row.scale_x = 0.5
        row.operator(HMS_COMPOSITING_OT_vertex_color_pick.bl_idname)
        row.operator(HMS_COMPOSITING_OT_vertex_color_fill.bl_idname)


# Use Blender factory to register / unregister classes.
register_classes, unregister_classes = bpy.utils.register_classes_factory([
    HMS_COMPOSITING_prefs,
    HMS_COMPOSITING_OT_vertex_color_pick,
    HMS_COMPOSITING_OT_vertex_color_fill,
    HMS_COMPOSITING_PT_main,
])


def register():
    # Register all classes.
    register_classes()
    # Create addon-level properties object.
    bpy.types.Scene.hms_compositing = bpy.props.PointerProperty(type=HMS_COMPOSITING_prefs)


def unregister():
    unregister_classes()
