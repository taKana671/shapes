import sys
import math
from enum import Enum, auto
from distutils.util import strtobool

import direct.gui.DirectGuiGlobals as DGG
from panda3d.core import Vec3, Vec2, Point3, LColor, Vec4
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import NodePath, TextNode
from panda3d.core import load_prc_file_data
from panda3d.core import TransparencyAttrib
from panda3d.core import OrthographicLens, Camera, MouseWatcher, PGTop
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGui import OkDialog
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock

from src import Cylinder, Sphere, QuickSphere, Torus, Cone, Plane, Cube


load_prc_file_data("", """
    win-size 1200 600
    window-title ProceduralShapes
""")


def is_int(str_val):
    try:
        int(str_val, 10)
    except ValueError:
        return False
    else:
        return True


def is_float(str_val):
    try:
        float(str_val)
    except ValueError:
        return False
    else:
        return True


def is_bool(str_val):
    try:
        strtobool(str_val)
    except ValueError:
        return False
    else:
        return True


class Status(Enum):

    SHOW_MODEL = auto()
    REPLACE_MODEL = auto()


class ModelDisplay(ShowBase):

    def __init__(self, model_cls):
        super().__init__()
        self.model_cls = model_cls

        self.disable_mouse()
        self.camera_root = NodePath('camera_root')
        self.camera_root.reparent_to(self.render)
        self.setup_light()

        self.is_rotating = True
        self.show_wireframe = True

        self.mw3d_node = self.create_display_region()
        self.gui_aspect2d = self.create_gui_region()

        model_maker = self.model_cls()
        self.gui = Gui(self.gui_aspect2d, model_maker)

        model = model_maker.create()
        self.dispay_model(model, hpr=Vec3(0, 0, 0))

        self.dragging = False
        self.before_mouse_pos = None
        self.state = Status.SHOW_MODEL

        # self.accept('d', self.toggle_wireframe)
        # self.accept('r', self.toggle_rotation)

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.taskMgr.add(self.update, 'update')

    def dispay_model(self, model, hpr):
        model.set_hpr(hpr)
        model.set_pos(Point3(0, 0, 0))
        model.set_color(LColor(1, 0, 0, 1))
        model.set_scale(4)
        model.reparent_to(self.render)

        if self.show_wireframe:
            model.set_render_mode_wireframe()

        self.model = model

    def output_bam_file(self):
        # node_path.writeBamFile(filepath)
        pass

    def toggle_rotation(self):
        self.is_rotating = not self.is_rotating

    def toggle_wireframe(self):
        # self.toggle_wireframe()

        if self.show_wireframe:
            self.model.set_render_mode_filled()
        else:
            self.model.set_render_mode_wireframe()
        self.show_wireframe = not self.show_wireframe

    def calc_aspect_ratio(self, display_region):
        """Return aspect ratio.
            Args:
                display_region (Vec4): (left, right, bottom, top); The ranges are from 0 to 1;
                0 means the left and bottom of the window; 1 means the right and top of the window.
        """
        props = self.win.get_properties()
        window_size = props.get_size()

        region_w = display_region.y - display_region.x
        region_h = display_region.w - display_region.z
        display_w = int(window_size.x * region_w)
        display_h = int(window_size.y * region_h)

        gcd = math.gcd(display_w, display_h)
        w = display_w / gcd
        h = display_h / gcd
        aspect_ratio = w / h

        return aspect_ratio

    def calc_scale(self, region_size):
        aspect_ratio = self.get_aspect_ratio()

        w = region_size.y - region_size.x
        h = region_size.w - region_size.z
        new_aspect_ratio = aspect_ratio * w / h

        if aspect_ratio > 1.0:
            s = 1. / h
            return Vec3(s / new_aspect_ratio, 1.0, s)
        else:
            s = 1.0 / w
            return Vec3(s, 1.0, s * new_aspect_ratio)

    def create_mouse_watcher(self, name, display_region):
        mw_node = MouseWatcher(name)
        # Gets MouseAndKeyboard, the parent of base.mouseWatcherNode
        # that passes mouse data into MouseWatchers,
        input_ctrl = self.mouseWatcher.get_parent()
        input_ctrl.attach_new_node(mw_node)
        # Restricts new MouseWatcher to the intended display region.
        mw_node.set_display_region(display_region)

        return mw_node

    def create_display_region(self):
        """Create a model display region and its MouseWatcher.
        """
        region_size = Vec4(0.3, 1.0, 0.0, 1.0)  # (left, right, bottom, top)
        region = self.win.make_display_region(region_size)

        cam = NodePath(Camera('cam3d'))
        aspect_ratio = self.calc_aspect_ratio(region_size)
        cam.node().get_lens().set_aspect_ratio(aspect_ratio)
        region.set_camera(cam)
        self.camNode.set_active(False)
        cam.set_pos(Point3(30, -30, 0))
        cam.look_at(Point3(0, 0, 0))
        cam.reparent_to(self.camera_root)

        mw3d_node = self.create_mouse_watcher('mw3d', region)
        return mw3d_node

    def create_gui_region(self):
        """Create a custom 2D display region and its MouseWatcher.
        """
        # (left, right, bottom, top)
        region_size = Vec4(0.0, 0.3, 0.0, 1.0)
        region = self.win.make_display_region(region_size)
        region.set_sort(20)
        # region.set_clear_color((0.5, 0.5, 0.5, 1.))
        # region.set_clear_color_active(True)

        cam = NodePath(Camera('cam2d'))
        lens = OrthographicLens()
        lens.set_film_size(2, 2)
        lens.set_near_far(-1000, 1000)
        cam.node().set_lens(lens)

        gui_render2d = NodePath('gui_render2d')
        gui_render2d.set_depth_test(False)
        gui_render2d.set_depth_write(False)
        cam.reparent_to(gui_render2d)
        region.set_camera(cam)

        gui_aspect2d = gui_render2d.attach_new_node(PGTop('gui_aspect2d'))
        scale = self.calc_scale(region_size)
        gui_aspect2d.set_scale(scale)
        mw2d_nd = self.create_mouse_watcher('mw2d', region)
        gui_aspect2d.node().set_mouse_watcher(mw2d_nd)

        return gui_aspect2d

    def setup_light(self):
        ambient_light = NodePath(AmbientLight('ambient_light'))
        ambient_light.reparent_to(self.render)
        ambient_light.node().set_color(LColor(0.6, 0.6, 0.6, 1.0))
        self.render.set_light(ambient_light)

        directional_light = NodePath(DirectionalLight('directional_light'))
        directional_light.node().get_lens().set_film_size(200, 200)
        directional_light.node().get_lens().set_near_far(1, 100)
        directional_light.node().set_color(LColor(1, 1, 1, 1))
        directional_light.set_pos_hpr(Point3(0, 0, 50), Vec3(-30, -45, 0))
        # directional_light.node().show_frustom()
        self.render.set_light(directional_light)
        directional_light.node().set_shadow_caster(True)
        self.render.set_shader_auto()

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        self.dragging = False
        self.before_mouse_pos = None

    def rotate_camera(self, mouse_pos, dt):
        if self.before_mouse_pos:
            angle = Vec3()

            if (delta := mouse_pos.x - self.before_mouse_pos.x) < 0:
                angle.x -= 180
            elif delta > 0:
                angle.x += 180

            if (delta := mouse_pos.y - self.before_mouse_pos.y) < 0:
                angle.z += 180
            elif delta > 0:
                angle.z -= 180

            angle *= dt
            self.camera_root.set_hpr(self.camera_root.get_hpr() + angle)

        self.before_mouse_pos = Vec2(mouse_pos.x, mouse_pos.y)

    def rotate_model(self, dt):
        angle = self.model.get_hpr() + 20 * dt
        if angle > 360:
            angle = 0

        self.model.set_hpr(angle)

    def get_input_value(self, key, entry):
        str_val = entry.get()

        if is_int(str_val):
            return int(str_val)

        if is_float(str_val):
            return float(str_val)

        if is_bool(str_val):
            return bool(strtobool(str_val))

        raise ValueError(f'{key}: input value is invalid.')

    def reflect_changes(self):
        self.state = Status.REPLACE_MODEL

    def create_new_model(self):
        try:
            params = {key: self.get_input_value(key, entry) for key, entry in self.gui.entries.items()}
            new_model = self.model_cls(**params).create()
        except ValueError as e:
            self.gui.show_dialog(e.args[0])
        else:
            return new_model

    def update(self, task):
        dt = globalClock.get_dt()

        match self.state:

            case Status.SHOW_MODEL:
                if self.is_rotating:
                    self.rotate_model(dt)

                if self.mw3d_node.has_mouse():
                    mouse_pos = self.mw3d_node.get_mouse()

                    if self.dragging:
                        if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                            self.rotate_camera(mouse_pos, dt)

            case Status.REPLACE_MODEL:
                if new_model := self.create_new_model():
                    hpr = self.model.get_hpr()
                    self.model.remove_node()
                    self.dispay_model(new_model, hpr)
                self.state = Status.SHOW_MODEL

        return task.cont


class Gui(DirectFrame):

    def __init__(self, parent, instance):
        self.frame_color = LColor(0.6, 0.6, 0.6, 1)
        self.text_color = LColor(1.0, 1.0, 1.0, 1.0)
        self.font = base.loader.load_font('fonts/DejaVuSans.ttf')

        super().__init__(
            parent=parent,
            frameSize=(-0.6, 0.6, -1., 1.),  # (left, right, bottom, top)
            frameColor=self.frame_color,
            pos=Point3(0, 0, 0),
            relief=DGG.SUNKEN,
            borderWidth=(0.01, 0.01)

        )
        self.initialiseoptions(type(self))
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.create_gui(instance)

    def create_gui(self, instance):
        start_z = 0.85
        last_z = self.create_edit_boxes(start_z, instance)
        self.create_buttons(last_z - 0.2)

    def create_edit_boxes(self, start_z, instance):
        exclude = ('bottom_center', 'top_center', 'fmt', 'color', 'stride')
        replaces = REPlACE_NAMES.get(instance.__class__.__name__, {})
        self.entries = {}

        for i, (name, val) in enumerate(
                (k, v) for k, v in instance.__dict__.items() if k not in exclude):

            if name not in exclude:
                labe_text = replaces[name] if name in replaces else name
                z = start_z - i * 0.1

                DirectLabel(
                    parent=self,
                    text=labe_text,
                    pos=Point3(0.2, 0.0, z),
                    text_fg=self.text_color,
                    text_font=self.font,
                    text_scale=0.06,
                    frameColor=LColor(1, 1, 1, 0),
                    text_align=TextNode.ARight
                )

                entry = DirectEntry(
                    parent=self,
                    pos=(0.25, 0, z),
                    text_fg=self.text_color,
                    text_font=self.font,
                    width=5,
                    scale=0.05,
                    initialText=str(val),
                    numLines=1,
                    relief=DGG.SUNKEN,
                    frameColor=self.frame_color
                )
                self.entries[labe_text] = entry
                # self.default_settings[name] = val

        return z

    def create_buttons(self, start_z):
        buttons = [
            ('Reflect Changes', base.reflect_changes),
            ('Toggle Wireframe', base.toggle_wireframe),
            ('Toggle Rotation', base.toggle_rotation),
            ('Output Bam File', base.output_bam_file)
        ]

        for i, (text, cmd) in enumerate(buttons):
            z = start_z - 0.1 * i
            DirectButton(
                parent=self,
                relief=DGG.RAISED,
                frameSize=(-0.51, 0.51, -0.05, 0.05),
                frameColor=self.frame_color,
                text=text,
                pos=Point3(0, 0, z),
                text_fg=self.text_color,
                text_scale=0.05,
                text_font=self.font,
                text_pos=(0, -0.01),
                borderWidth=(0.01, 0.01),
                command=cmd
            )

    def show_dialog(self, msg):
        self.dialog = OkDialog(
            dialogName='validation',
            frameSize=(-1, 1, -0.2, 0.1),
            frameColor=self.frame_color,
            text=msg,
            text_scale=0.05,
            text_font=self.font,
            text_fg=self.text_color,
            buttonSize=(-0.08, 0.08, -0.05, 0.05),
            buttonTextList=['OK'],
            button_frameColor=self.frame_color,
            button_text_pos=(0, -0.01),
            button_text_scale=0.04,
            button_text_fg=self.text_color,
            relief=DGG.FLAT,
            pos=Point3(0.5, 0, 0.8),
            midPad=0.02,
            command=self.withdraw_dialog
        )

    def withdraw_dialog(self, btn):
        def withdraw(task):
            self.dialog.cleanup()
            return task.done

        base.taskMgr.do_method_later(0.5, withdraw, 'withdraw')


REPlACE_NAMES = {
    'Cone': {'segs_sc_r': 'slice_caps_radial', 'segs_sc_a': 'slice_caps_axial', 'segs_bc': 'segs_bottom_cap', 'segs_tc': 'segs_top_cap'},
    'Cylinder': {'segs_sc_r': 'slice_caps_radial', 'segs_sc_a': 'slice_caps_axial', 'segs_bc': 'segs_bottom_cap', 'segs_tc': 'segs_top_cap'},
    'Torus': {'segs_sssc': 'section_slice_start_cap', 'segs_ssec': 'section_slice_end_cap', 'segs_rssp': 'ring_slice_start_cap', 'segs_rsec': 'ring_slice_end_cap'},
}


def main(model_cls):
    app = ModelDisplay(model_cls)
    app.run()


if __name__ == '__main__':
    app = ModelDisplay(Plane)
    # app = ModelDisplay()
    app.run()