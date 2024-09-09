import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock

from panda3d.core import Vec3, Vec2, Point3, LColor
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import NodePath, PandaNode

from src import Cylinder, Sphere, QuickSphere


class ModelDisplay(ShowBase):

    def __init__(self):
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

        # self.model = CylinderModel(radius=2).create()
        self.model = QuickSphere().create()
        self.model.reparent_to(self.render)
        self.model.set_pos(Point3(0, 0, 0))
        # self.model.set_color(LColor(1, 0, 0, 1))
        self.model.set_scale(4)
        self.model.set_texture(self.loader.load_texture('src/board.jpg'))

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


if __name__ == '__main__':
    app = ModelDisplay()
    app.run()