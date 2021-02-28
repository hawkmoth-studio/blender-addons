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
    'name': 'Hawkmoth Studio: Rendering',
    'author': 'Vitaly Ogoltsov',
    'wiki_url': 'https://github.com/hawkmoth-studio/blender-tools/wiki',
    'tracker_url': 'https://github.com/hawkmoth-studio/blender-tools/issues',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'View 3D > Tool Shelf > Hawkmoth Studio',
    'category': 'Game Development'
}


class HMS_RENDERING_prefs(bpy.types.PropertyGroup):
    """Rendering tools preferences."""
    render_output: bpy.props.StringProperty(
        name='Render output path',
        description='Path where render passes are saved during rendering',
        default='C:\\RenderOutput'
    )


class HMS_RENDERING_OT_batch_render_selected(bpy.types.Operator):
    """This operator renders selected objects one-by-one.
    """
    bl_idname = "hms_rendering.batch_render_selected"
    bl_label = "Batch render selected"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects) == 0:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        selected_object_names = sorted([o.name for o in bpy.context.selected_objects])

        # hide all objects from rendering
        for name in selected_object_names:
            render_object: bpy.types.Object = bpy.data.objects.get(name)
            render_object.hide_viewport = render_object.hide_render = True
        # render objects one by one
        for name in selected_object_names:
            print(f"Rendering object: {name}")
            render_object: bpy.types.Object = bpy.data.objects.get(name)
            render_object.hide_viewport = render_object.hide_render = False
            bpy.ops.render.render()
            self._create_archive(context, render_object)
            render_object.hide_viewport = render_object.hide_render = True

        return {"FINISHED"}

    def _create_archive(self, context: bpy.types.Context, render_object: bpy.types.Object):
        import os
        import zipfile

        prefs: HMS_RENDERING_prefs = context.scene.hms_rendering

        zf = zipfile.ZipFile(f"{prefs.render_output}\\{render_object.name}.zip", "w")
        for dirname, subdirectories, filenames in os.walk(prefs.render_output):
            for filename in filenames:
                if not filename.endswith('.zip'):
                    filepath = os.path.join(dirname, filename)
                    zf.write(filepath, filename)
                    os.remove(filepath)
        zf.close()


class HMS_RENDERING_PT_main(bpy.types.Panel):
    bl_idname = "HMS_RENDERING_PT_main"
    bl_category = "HMS: Rendering"
    bl_label = "Batch Rendering"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context: bpy.types.Context):
        prefs: HMS_RENDERING_prefs = context.scene.hms_rendering

        row = self.layout.row()
        row.prop(prefs, 'render_output')

        row = self.layout.row()
        row.operator(HMS_RENDERING_OT_batch_render_selected.bl_idname)


classes = (
    HMS_RENDERING_prefs,
    HMS_RENDERING_OT_batch_render_selected,
    HMS_RENDERING_PT_main,
)
register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    # Register all classes.
    register_classes()
    # Create addon-level properties object.
    bpy.types.Scene.hms_rendering = bpy.props.PointerProperty(type=HMS_RENDERING_prefs)


def unregister():
    unregister_classes()
