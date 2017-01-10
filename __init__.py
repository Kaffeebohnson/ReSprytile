bl_info = {
    "name": "Sprytile Painter",
    "author": "Jeiel Aranal",
    "version": (0, 2, 0),
    "blender": (2, 7, 0),
    "description": "A utility for creating tile based low spec scenes with paint/map editor tools",
    "location": "View3D > UI panel > Sprytile",
    "tracker_url": "https://github.com/ChemiKhazi/Sprytile/issues",
    "category": "Paint"
}

if "bpy" in locals():
    import imp

    imp.reload(sprytile_gui)
    imp.reload(sprytile_modal)
    imp.reload(sprytile_panel)
    imp.reload(sprytile_utils)
else:
    from . import sprytile_gui, sprytile_modal, sprytile_panel, sprytile_utils

import bpy
from bpy.props import *
import rna_keymap_ui


class SprytileSceneSettings(bpy.types.PropertyGroup):
    def set_normal(self, value):
        if self.lock_normal is True:
            return
        self["normal_mode"] = value

    def get_normal(self):
        if "normal_mode" not in self.keys():
            self["normal_mode"] = 3
        return self["normal_mode"]

    normal_mode = EnumProperty(
        items=[
            ("X", "X", "World X-Axis", 1),
            ("Y", "Y", "World Y-Axis", 2),
            ("Z", "Z", "World X-Axis", 3)
        ],
        name="Normal Mode",
        description="Normal to create the mesh on",
        default='Z',
        set=set_normal,
        get=get_normal
    )

    lock_normal = BoolProperty(
        name="Lock",
        description="Lock normal used to create meshes",
        default=False
    )

    def set_mode(self, value):
        run_modal = True
        if "is_running" in self.keys():
            if self["is_running"]:
                if self["paint_mode"] == value:
                    self["is_running"] = False
                    run_modal = False

        if run_modal:
            bpy.ops.sprytile.modal_tool('INVOKE_REGION_WIN')
        self["paint_mode"] = value

    def get_mode(self):
        if "paint_mode" not in self.keys():
            self["paint_mode"] = 3
        return self["paint_mode"]

    paint_mode = EnumProperty(
        items=[
            ("SET_NORMAL", "Set Normal", "Select a normal to use for face creation", 2),
            ("PAINT", "Paint", "Advanced UV paint tools", 1),
            ("MAKE_FACE", "Build", "Only create new faces", 3),
        ],
        name="Sprytile Paint Mode",
        description="Paint mode",
        default='MAKE_FACE',
        set=set_mode,
        get=get_mode
    )

    world_pixels = IntProperty(
        name="World Pixel Density",
        description="How many pixels are displayed in one world unit",
        subtype='PIXEL',
        default=32,
        min=8,
        max=2048
    )

    paint_normal_vector = FloatVectorProperty(
        name="Srpytile Last Paint Normal",
        description="Last saved painting normal used by Sprytile",
        subtype='DIRECTION',
        default=(0.0, 0.0, 1.0)
    )

    paint_up_vector = FloatVectorProperty(
        name="Sprytile Last Paint Up Vector",
        description="Last saved painting up vector used by Sprytile",
        subtype='DIRECTION',
        default=(0.0, 1.0, 0.0)
    )

    uv_flip_x = BoolProperty(
        name="Flip X",
        default=False
    )
    uv_flip_y = BoolProperty(
        name="Flip Y",
        default=False
    )
    mesh_rotate = FloatProperty(
        name="Grid Rotation",
        description="Rotation of mesh creation",
        subtype='ANGLE',
        unit='ROTATION',
        step=9000,
        precision=0,
        min=-6.28319,
        max=6.28319,
        default=0.0
    )

    cursor_snap = EnumProperty(
        items=[
            ('VERTEX', "Vertex", "Snap cursor to nearest vertex", "SNAP_GRID", 1),
            ('GRID', "Grid", "Snap cursor to grid", "SNAP_VERTEX", 2)
        ],
        name="Cursor snap mode",
        description="Sprytile cursor snap mode"
    )

    cursor_flow = BoolProperty(
        name="Cursor Flow",
        description="Cursor automatically follows mesh building",
        default=False
    )
    paint_align = EnumProperty(
        items=[
            ('TOP_LEFT', "Top Left", "", 1),
            ('TOP', "Top", "", 2),
            ('TOP_RIGHT', "Top Right", "", 3),
            ('LEFT', "Left", "", 4),
            ('CENTER', "Center", "", 5),
            ('RIGHT', "Right", "", 6),
            ('BOTTOM_LEFT', "Bottom Left", "", 7),
            ('BOTTOM_LEFT', "Bottom", "", 8),
            ('BOTTOM_RIGHT', "Bottom Right", "", 9),
        ],
        name="Paint Align",
        description="Paint alignment mode",
        default='CENTER'
    )

    def set_align_toggle(self, value, row):
        prev_value = self.get_align_toggle(row)
        row_val = 0
        if row == 'top':
            row_val = 0
        elif row == 'middle':
            row_val = 3
        elif row == 'bottom':
            row_val = 6
        else:
            return
        col_val = 0
        if value[0] and prev_value[0] != value[0]:
            col_val = 1
        elif value[1] and prev_value[1] != value[1]:
            col_val = 2
        elif value[2] and prev_value[2] != value[2]:
            col_val = 3
        else:
            return
        self["paint_align"] = row_val + col_val

    def set_align_top(self, value):
        self.set_align_toggle(value, "top")

    def set_align_middle(self, value):
        self.set_align_toggle(value, "middle")

    def set_align_bottom(self, value):
        self.set_align_toggle(value, "bottom")

    def get_align_toggle(self, row):
        if "paint_align" not in self.keys():
            self["paint_align"] = 5
        align = self["paint_align"]
        if row == 'top':
            return align == 1, align == 2, align == 3
        if row == 'middle':
            return align == 4, align == 5, align == 6
        if row == 'bottom':
            return align == 7, align == 8, align == 9
        return False, False, False

    def get_align_top(self):
        return self.get_align_toggle("top")

    def get_align_middle(self):
        return self.get_align_toggle("middle")

    def get_align_bottom(self):
        return self.get_align_toggle("bottom")

    paint_align_top = BoolVectorProperty(
        name="Align",
        size=3,
        set=set_align_top,
        get=get_align_top
    )
    paint_align_middle = BoolVectorProperty(
        name="Align",
        size=3,
        set=set_align_middle,
        get=get_align_middle
    )
    paint_align_bottom = BoolVectorProperty(
        name="Align",
        size=3,
        set=set_align_bottom,
        get=get_align_bottom
    )

    paint_hinting = BoolProperty(
        name="Hinting",
        description="Selected edge is used as X axis for UV mapping."
    )
    paint_stretch_x = BoolProperty(
        name="Stretch X",
        description="Stretch face over X axis of tile"
    )
    paint_stretch_y = BoolProperty(
        name="Stretch Y",
        description="Stretch face over Y axis of tile"
    )
    paint_edge_snap = BoolProperty(
        name="Stretch Edge Snap",
        description="Snap UV vertices to edges of tile when stretching.",
        default=True
    )
    edge_threshold = FloatProperty(
        name="Threshold",
        description="Ratio of UV tile near to edge to apply snap",
        min=0.01,
        max=0.5,
        soft_min=0.01,
        soft_max=0.5,
        default=0.35
    )
    paint_uv_snap = BoolProperty(
        name="UV Snap",
        default=True,
        description="Snap UV vertices to texture pixels"
    )

    is_running = BoolProperty(
        name="Sprytile Running",
        description="Exit Sprytile tool"
    )
    is_snapping = BoolProperty(
        name="Is Cursor Snap",
        description="Is cursor snapping currently activated"
    )
    show_extra = BoolProperty(
        name="Extra UV Grid Settings",
        default=False
    )
    show_overlay = BoolProperty(
        name="Show Grid Overlay",
        default=True
    )


class SprytileMaterialGridSettings(bpy.types.PropertyGroup):
    mat_id = StringProperty(
        name="Material Id",
        description="Name of the material this grid references",
        default=""
    )
    id = IntProperty(
        name="Grid ID",
        default=-1
    )
    name = StringProperty(
        name="Grid Name"
    )
    grid = IntVectorProperty(
        name="Size",
        description="Grid size, in pixels",
        min=2,
        size=2,
        subtype='XYZ',
        default=(32, 32)
    )
    offset = IntVectorProperty(
        name="Offset",
        description="Offset of the grid",
        subtype='TRANSLATION',
        size=2,
        default=(0, 0)
    )
    rotate = FloatProperty(
        name="UV Rotation",
        description="Rotation of UV grid",
        subtype='ANGLE',
        unit='ROTATION',
        default=0.0
    )
    tile_selection = IntVectorProperty(
        name="Tile Selection",
        size=4,
        default=(0, 0, 1, 1)
    )


class SprytileMaterialData(bpy.types.PropertyGroup):

    def expanded_default(self):
        if 'is_expanded' not in self.keys():
            self['is_expanded'] = True

    def get_expanded(self):
        self.expanded_default()
        return self['is_expanded']

    def set_expanded(self, value):
        self.expanded_default()
        do_rebuild = self['is_expanded'] is not value
        self['is_expanded'] = value
        if do_rebuild:
            bpy.ops.sprytile.build_grid_list()

    mat_id = StringProperty(
        name="Material Id",
        description="Name of the material this grid references",
        default=""
    )
    is_expanded = BoolProperty(
        default=True,
        get=get_expanded,
        set=set_expanded
    )
    grids = CollectionProperty(type=SprytileMaterialGridSettings)


class SprytileGridDisplay(bpy.types.PropertyGroup):
    mat_id = StringProperty(default="")
    grid_id = IntProperty(default=-1)

    def get_mat_name(self):
        if self.mat_id == "":
            return ""
        data_idx = bpy.data.materials.find(self.mat_id)
        if data_idx < 0:
            return ""
        return bpy.data.materials[self.mat_id].name

    def set_mat_name(self, value):
        if self.mat_id == "":
            return
        data_idx = bpy.data.materials.find(self.mat_id)
        if data_idx < 0:
            return
        bpy.data.materials[self.mat_id].name = value
        bpy.ops.sprytile.validate_grids()

    mat_name = StringProperty(
        get=get_mat_name,
        set=set_mat_name
    )


class SprytileGridList(bpy.types.PropertyGroup):

    def get_idx(self):
        if "idx" not in self.keys():
            self["idx"] = 0
        return self["idx"]

    def set_idx(self, value):
        # If the selected index is a material entry
        # Move to next entry
        list_size = len(self.display)
        while value < (list_size - 1) and self.display[value].mat_id != "":
            value += 1
        value = max(0, min(len(self.display)-1, value))
        self["idx"] = value
        if value < 0 or value >= len(self.display):
            return
        # Set the object grid id to target grid
        target_entry = self.display[value]
        if target_entry.grid_id != -1:
            bpy.context.object.sprytile_gridid = target_entry.grid_id

    display = bpy.props.CollectionProperty(type=SprytileGridDisplay)
    idx = IntProperty(
        default=0,
        get=get_idx,
        set=set_idx
    )


def setup_props():
    bpy.types.Scene.sprytile_data = bpy.props.PointerProperty(type=SprytileSceneSettings)
    bpy.types.Scene.sprytile_mats = bpy.props.CollectionProperty(type=SprytileMaterialData)

    bpy.types.Scene.sprytile_list = bpy.props.PointerProperty(type=SprytileGridList)

    bpy.types.Scene.sprytile_ui = bpy.props.PointerProperty(type=sprytile_gui.SprytileGuiData)

    bpy.types.Object.sprytile_gridid = IntProperty(
        name="Grid ID",
        description="Grid index used for object",
        default=-1
    )


def teardown_props():
    del bpy.types.Scene.sprytile_data
    del bpy.types.Scene.sprytile_mats

    del bpy.types.Scene.sprytile_list

    del bpy.types.Scene.sprytile_ui

    del bpy.types.Object.sprytile_gridid


class SprytileAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our addon")
        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi_list in sprytile_modal.SprytileModalTool.keymaps.items():
            col.label(km.name)
            km = km.active()
            for kmi in kmi_list:
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

def setup_keymap():
    km_array = sprytile_modal.SprytileModalTool.keymaps
    win_mgr = bpy.context.window_manager
    key_config = win_mgr.keyconfigs.addon

    keymap = key_config.keymaps.new(name='Mesh', space_type='EMPTY')
    km_array[keymap] = [
        keymap.keymap_items.new("sprytile.modal_tool", 'SPACE', 'PRESS', ctrl=True, shift=True)
    ]

    keymap = key_config.keymaps.new(name="Sprytile Paint Modal Map", space_type='EMPTY', region_type='WINDOW', modal=True)
    km_items = keymap.keymap_items
    km_array[keymap] = [
        km_items.new_modal('CANCEL', 'ESC', 'PRESS'),
        km_items.new_modal('SNAP', 'S', 'ANY'),
        km_items.new_modal('FOCUS', 'W', 'PRESS'),
        km_items.new_modal('ROTATE_LEFT', 'ONE', 'PRESS'),
        km_items.new_modal('ROTATE_RIGHT', 'TWO', 'PRESS')
    ]
    sprytile_modal.SprytileModalTool.modal_values = [
        'Cancel',
        'Cursor Snap',
        'Cursor Focus',
        'Rotate Left',
        'Rotate Right'
    ]


def teardown_keymap():
    for keymap in sprytile_modal.SprytileModalTool.keymaps:
        kmi_list = keymap.keymap_items
        for keymap_item in kmi_list:
            keymap.keymap_items.remove(keymap_item)
    sprytile_modal.SprytileModalTool.keymaps.clear()


def register():
    bpy.utils.register_class(sprytile_panel.SprytilePanel)
    bpy.utils.register_module(__name__)
    setup_props()
    setup_keymap()


def unregister():
    teardown_keymap()
    teardown_props()
    bpy.utils.unregister_class(sprytile_panel.SprytilePanel)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
