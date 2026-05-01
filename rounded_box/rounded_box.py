from enum import Flag, auto

from panda3d.core import Vec3, Point3

from ..box import BasicBox
from ..sphere import QuarteredHemisphereCorner
from ..cylinder import VerticalRoundedEdge, HorizontalRoundedEdge


class Sides(Flag):

    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    FRONT = auto()
    BACK = auto()

    FRONT_LEFT = FRONT | LEFT
    FRONT_RIGHT = FRONT | RIGHT
    BACK_LEFT = BACK | LEFT
    BACK_RIGHT = BACK | RIGHT


class BasicRoundedBox(BasicBox):

    def create_sides(self, vertex_cnt, vdata_values, prim_indices):
        for plane in ('xyz', 'zxy', 'yzx'):
            plane_id = plane[:2]
            is_front = plane_id == 'zx'
            name, index, offset, segments = self.get_plane_details(plane)

            for direction in (-1, 1):
                normal = Vec3()
                normal[index.axis_3] = direction * (-1 if self.invert else 1)
                vertex = Point3()
                vertex[index.axis_3] = .5 * self.dims[index.axis_3] * direction + offset.axis_3
                side_id = f"{'-' if direction == -1 else ''}{plane_id}"

                if self.open_sides[side_id]:
                    if self.thickness > 0:
                        if plane_id in ('zx', 'yz'):
                            continue

                        vertex_cnt += self.create_thick_side(
                            vertex_cnt, vdata_values, prim_indices, direction, is_front,
                            vertex, normal, name, index, offset, segments)
                else:
                    vertex_cnt += self.create_side(
                        vertex_cnt, vdata_values, prim_indices, direction, is_front,
                        vertex, normal, index, offset, segments)

        return vertex_cnt

    def create_vertical_edge_cylinder(self, vertex_cnt, vdata_values, prim_indices,
                                      height, center, start_angle, slice_deg):
        corner = VerticalRoundedEdge(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=height,
            segs_c=20,
            segs_a=self.segs_z,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=slice_deg,
            invert=self.invert
        )

        vertex_cnt = corner.create_cylinder(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_horizontal_edge_cylinder(self, vertex_cnt, vdata_values, prim_indices,
                                        height, center, start_angle, slice_deg, x_axis,
                                        start_slice_cap, end_slice_cap, is_open):
        edge = HorizontalRoundedEdge(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=height,
            segs_c=20,
            segs_a=self.segs_w if x_axis else self.segs_d,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=slice_deg,
            start_slice_cap=start_slice_cap,
            end_slice_cap=end_slice_cap,
            invert=self.invert,
            x_axis=x_axis
        )

        vertex_cnt = edge.create_cylinder(vertex_cnt, vdata_values, prim_indices)

        if self.thickness and is_open:
            vertex_cnt += edge.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def create_corner_sphere(self, vertex_cnt, vdata_values, prim_indices, center,
                             start_angle, slice_deg, bottom_clip=-1., top_clip=1.):
        corner = QuarteredHemisphereCorner(
            center=center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            segs_h=20,
            segs_v=20,
            segs_slice_caps=0,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip,
            invert=self.invert
        )

        vertex_cnt = corner.create_quartered_hemisphere(
            vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt