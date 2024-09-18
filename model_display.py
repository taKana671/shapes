import sys
import math

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock

from panda3d.core import Vec3, Vec2, Point3, LColor, Vec4
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import NodePath, PandaNode, TextNode
from panda3d.core import load_prc_file_data
from panda3d.core import TransparencyAttrib
from direct.gui.DirectFrame import DirectFrame

from panda3d.core import OrthographicLens, Camera, MouseWatcher, PGTop
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectLabel import DirectLabel


from src import Cylinder, Sphere, QuickSphere, Torus, Cone


load_prc_file_data("", """
    win-size 1200 600
    window-title ProceduralShapes
""")

class ModelDisplay(ShowBase):

    def __init__(self, model_cls):
        super().__init__()
        self.disable_mouse()
        self.camera_root = NodePath('camera_root')
        self.camera_root.reparent_to(self.render)
        self.camera.reparent_to(self.camera_root)
        self.camera.set_pos(Point3(30, -30, 0))
        self.camera.look_at(Point3(0, 0, 0))

        # self.camera.set_pos(Point3(20, -30, 5))
        # self.camera.look_at(Point3(0, 10, 2))
        self.setup_light()

        self.dragging = False
        self.before_mouse_pos = None

        self.model_maker = model_cls()
        self.create_2d_region()

        # self.model = Cylinder(invert=False, radius=2, inner_radius=0.5, slice_angle_deg=0, slice_caps_radial=2, slice_caps_axial=2).create()
        
        # model_maker = model_cls()
        # model_maker = Cone()
      
        # model_maker = Torus(ring_slice_deg=60, section_slice_deg=90, section_inner_radius=0.3)
        # self.model = Cone().create()
        self.model = self.model_maker.create()
        self.model.reparent_to(self.render)
        self.model.set_pos(Point3(0, 0, 0))
        self.model.set_color(LColor(1, 0, 0, 1))
        self.model.set_scale(4)

        # self.model2 = model_maker.create()
        # self.model2.reparent_to(self.render)
        # self.model2.set_pos(Point3(0, 0, 0))
        # self.model2.set_color(LColor(0, 1, 0, 1))
        # self.model2.set_scale(4)
        # self.model2.set_pos(Point3(0, 0, 0))

        # self.model.set_texture(self.loader.load_texture('src/board.jpg'))

        self.is_rotating = True
        self.show_wireframe = True
        self.accept('d', self._toggle_wireframe)
        self.accept('r', self._rotate_model)

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.taskMgr.add(self.update, 'update')

    def _rotate_model(self):
        self.is_rotating = not self.is_rotating

    def _toggle_wireframe(self):
        self.show_wireframe = not self.show_wireframe
        # self.toggle_wireframe()

        if self.show_wireframe:
            self.model.set_render_mode_filled()
        else:
            self.model.set_render_mode_wireframe()

    def calc_aspect_ratio(self, window_size, display_region):
        """Return aspect ratio.
            Args:
                window_size (Vec2): current window size; Vec2(width, height)
                display_region (Vec4): (left, right, bottom, top); The ranges are from 0 to 1,
                               where 0 is the left and bottomof the window,
                               and 1 is the right and top of the window.
        """
        region_w = display_region.y - display_region.x
        region_h = display_region.w - display_region.z
        display_w = int(window_size.x * region_w)
        display_h = int(window_size.y * region_h)

        gcd = math.gcd(display_w, display_h)
        w = display_w / gcd
        h = display_h / gcd
        aspect_ratio = w / h

        return aspect_ratio

    def create_2d_region(self):
        props = self.win.get_properties()
        region_size = Vec4(0.0, 0.3, 0.0, 1.0)

        region = self.win.make_display_region(region_size)
        region.set_sort(20)
        region.set_clear_color((0.5, 0.5, 0.5, 1.))
        region.set_clear_color_active(True)

        cam2d = NodePath(Camera('cam2d'))
        lens = OrthographicLens()
        lens.set_film_size(2, 2)
        lens.set_near_far(-1000, 1000)
        # **************************************************************************
        # window_size = props.get_size()
        # ratio = self.calc_aspect_ratio(window_size, Vec4(0.0, 0.3, 0.0, 1.0))
        # lens.set_aspect_ratio(ratio)
        # **************************************************************************
        cam2d.node().set_lens(lens)

        gui_render2d = NodePath('gui_render2d')
        gui_render2d.set_depth_test(False)
        gui_render2d.set_depth_write(False)
        cam2d.reparent_to(gui_render2d)
        region.set_camera(cam2d)
        gui_aspect2d = gui_render2d.attach_new_node(PGTop('gui_aspect2d'))

        mw2d_nd = MouseWatcher('mw2d')
        mw2d_nd.set_display_region(region)
        input_ctrl = self.mouseWatcher.parent
        mw2d_np = input_ctrl.attach_new_node(mw2d_nd)
        gui_aspect2d.node().set_mouse_watcher(mw2d_nd)

        # **************************************************************************
        aspect_ratio = self.get_aspect_ratio()
        w = region_size.y - region_size.x
        h = region_size.w - region_size.z
        new_aspect_ratio = aspect_ratio * w / h

        if aspect_ratio > 1.:
            s = 1. / h
            gui_aspect2d.set_scale(s / new_aspect_ratio, 1.0, s)
        else:
            s = 1.0 / w
            gui_aspect2d.set_scale(s, 1.0, s * new_aspect_ratio)
        # **************************************************************************

        self.gui = Gui(gui_aspect2d, self.model_maker)


        # entry = DirectEntry(
        #     parent=gui_aspect2d,
        #     pos=(0, 0, -0.3),
        #     width=10,
        #     scale=0.07,
        #     initialText='abc',
           
        #     numLines=1,
        #     # frameColor=(0, 0, 0, 1),
        # )
    
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

    def update(self, task):
        dt = globalClock.get_dt()

        if self.is_rotating:
            self.rotate_model(dt)

        if self.mouseWatcherNode.has_mouse():
            mouse_pos = self.mouseWatcherNode.get_mouse()

            if self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    self.rotate_camera(mouse_pos, dt)

        return task.cont


class Gui(DirectFrame):

    def __init__(self, parent, instance):
        super().__init__(
            parent=parent,
            # frameSize=(-0.65, 0.65, 0.2, -0.2),  # (left, right, bottom, top)
            frameSize=(-0.6, 0.6, -1., 1.),  # (left, right, bottom, top)
            frameColor=(1, 1, 1, 0.8),
            pos=Point3(0, 0, 0)
        )
        self.initialiseoptions(type(self))
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.create_gui(instance)

    def create_gui(self, instance):
        # font = base.loader.load_font('font/segoeui.ttf')

        z = 0.8
        for i, (name, val) in enumerate(instance.__dict__.items()):
            DirectLabel(
                parent=self,
                text=name,
                pos=Point3(0, 0, z - i * 0.05),
                text_fg=LColor(0, 0, 0, 1),
                # text_font=font,
                text_scale=0.05,
                frameColor=LColor(1, 1, 1, 0),
                text_align=TextNode.ARight
            )





if __name__ == '__main__':
    app = ModelDisplay(Cone)
    app.run()