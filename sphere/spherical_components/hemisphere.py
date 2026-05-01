from types import SimpleNamespace

from panda3d.core import Vec3, Point3

from ..sphere import SphereVariables, SphereGeometry


class BasicHemisphere(SphereVariables, SphereGeometry):
    """A class that provides functionality for creating a hemisphere model
    """

    def create_bottom(self, index_offset, vdata_values, prim_indices):
        cap = SimpleNamespace(
            z=self.bottom_height,
            normal=Vec3(0., 0., -1.),
            pole_vertex=Point3(0, 0, -self.radius) + self.center,
            is_bottom=True
        )
        vertex_cnt = 0

        if self.bottom_clip > -1:
            offset_cnt = self.create_cap_edge_vertices(vdata_values, cap)
            vertex_cnt += self.create_bottom_edge_quads(index_offset, vdata_values, prim_indices)
        else:
            offset_cnt = self.create_cap_pole(vdata_values, cap)
            vertex_cnt += self.create_bottom_pole_triangles(index_offset, vdata_values, prim_indices)

        return vertex_cnt + offset_cnt, index_offset + offset_cnt

    def create_top(self, index_offset, vdata_values, prim_indices):
        cap = SimpleNamespace(
            z=self.top_height,
            normal=Vec3(0., 0., 1.),
            pole_vertex=Point3(0, 0, self.radius) + self.center,
            is_bottom=False
        )
        vertex_cnt = 0

        if self.top_clip < 1.:
            vertex_cnt += self.create_cap_edge_vertices(vdata_values, cap)
            self.create_top_edge_quads(index_offset + vertex_cnt - 1, prim_indices)
        else:
            vertex_cnt += self.create_cap_pole(vdata_values, cap)
            self.create_top_pole_triangles(index_offset + vertex_cnt - 1, prim_indices)

        return vertex_cnt