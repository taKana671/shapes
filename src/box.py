import array
from types import SimpleNamespace

from panda3d.core import Vec3, Point3

from .create_geometry import ProceduralGeometry


class Box(ProceduralGeometry):
    """Create a geom node of cube or cuboid.
        Arges:
            width (float): dimension along the x-axis; more than zero.
            depth (float): dimension along the y-axis; more than zero.
            height (float): dimension along the z-axis; more than zero.
            segs_w (int): the number of subdivisions in width; more than 1.
            segs_d (int): the number of subdivisions in depth; more than 1.
            segs_h (int): the number of subdivisions in height; more than 1.
            thickness (float): offset of inner box sides; 0 means no inner box.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
            open_left(bool): if True, no left side.
            open_right(bool): if True, no right side.
            open_back(bool): if True, no back side.
            open_front(bool): if True, no front side.
            open_bottom(bool): if True, no bottom side.
            open_top(bool): if True, no top side.
    """

    def __init__(self, width=1.0, depth=1.0, height=1.0, segs_w=2, segs_d=2, segs_z=2,
                 thickness=0, invert=False, open_left=False, open_right=False, open_back=False,
                 open_front=False, open_bottom=False, open_top=False):
        super().__init__()
        self.width = width
        self.depth = depth
        self.height = height
        self.segs_w = segs_w
        self.segs_d = segs_d
        self.segs_z = segs_z
        self.thickness = thickness
        self.open_left = open_left
        self.open_right = open_right
        self.open_top = open_top
        self.open_bottom = open_bottom
        self.open_front = open_front
        self.open_back = open_back

        self.center = Point3(0, 0, 0)
        self.invert = False
        self.color = (1, 1, 1, 1)

    def define_vertex_order(self, index_offset, prim_indices, direction, inner_range, outer_range=1):
        for i in range(outer_range):
            for j in range(inner_range):
                vi1 = index_offset + i * (inner_range + 1) + j
                vi2 = vi1 + 1
                vi3 = vi2 + inner_range
                vi4 = vi3 + 1

                if self.invert:
                    prim_indices.extend((vi1, vi4, vi2) if direction == 1 else (vi1, vi2, vi4))
                    prim_indices.extend((vi1, vi3, vi4) if direction == 1 else (vi1, vi4, vi3))
                else:
                    prim_indices.extend((vi1, vi2, vi4) if direction == 1 else (vi1, vi4, vi2))
                    prim_indices.extend((vi1, vi4, vi3) if direction == 1 else (vi1, vi3, vi4))

    def create_side(self, index_offset, vdata_values, prim_indices, direction, is_front,
                    vertex, normal, name, index, offset, segs):
        vertex_cnt = 0

        for i in range(segs.axis_2 + 1):
            b = i / segs.axis_2
            vertex[index.axis_2] = (-.5 + b) * self.dims[index.axis_2] + offset.axis_2

            for j in range(segs.axis_1 + 1):
                a = j / segs.axis_1
                vertex[index.axis_1] = (-.5 + a) * self.dims[index.axis_1] + offset.axis_1

                if is_front:
                    u = -b * direction + (1 if direction > 0 else 0)
                    v = a
                else:
                    u = a * direction + (1 if direction < 0 else 0)
                    v = b

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        self.define_vertex_order(index_offset, prim_indices, direction, segs.axis_1, segs.axis_2)

        return vertex_cnt

    def create_thick_side(self, index_offset, vdata_values, prim_indices, direction, is_front,
                          vertex, normal, name, index, offset, segments):
        vertex_cnt = 0

        for sign in ('-', ''):
            thicknesses = []
            c1 = self.inner_corners[sign + name.axis_1]
            c2 = self.inner_corners[sign + name.axis_2]

            if c1 > 0:
                dim1 = self.dims[index.axis_2]
                dim2 = self.inner_dims[name.axis_2]
                thicknesses.append([1, ((dim2, c1, c2), (dim1, 0., 0.))])

            if c2 > 0:
                dim1 = self.dims[index.axis_1]
                dim2 = self.inner_dims[name.axis_1]
                thicknesses.append([2, ((dim1, 0., 0.), (dim2, c2, c1))])

            for primary_idx, t in thicknesses:
                _index_offset = index_offset + vertex_cnt

                if primary_idx == 1:
                    idx_1, idx_2 = index.axis_1, index.axis_2
                    offs_1, offs_2 = offset.axis_1, offset.axis_2
                    segs = segments.axis_2
                else:
                    idx_1, idx_2 = index.axis_2, index.axis_1
                    offs_1, offs_2 = offset.axis_2, offset.axis_1
                    segs = segments.axis_1

                for dim, corner_1, corner_2 in t:
                    if sign == '-':
                        coord = corner_1 - self.dims[idx_1] * .5
                    else:
                        coord = self.dims[idx_1] * .5 - corner_1

                    vertex[idx_1] = coord + offs_1
                    a = coord / self.dims[idx_1] + .5

                    for i in range(segs + 1):
                        j = i / segs
                        if sign == '-':
                            coord = corner_2 - self.dims[idx_2] * .5 + j * dim
                        else:
                            coord = self.dims[idx_2] * .5 - j * dim - corner_2

                        vertex[idx_2] = coord + offs_2
                        b = coord / self.dims[idx_2] + .5

                        if is_front:
                            u = (-b if primary_idx == 1 else -a) * direction + (1 if direction > 0 else 0)
                            v = a if primary_idx == 1 else b
                        else:
                            u = (a if primary_idx == 1 else b) * direction + (1 if direction < 0 else 0)
                            v = b if primary_idx == 1 else a

                        if self.invert:
                            u = 1. - u

                        vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                        vertex_cnt += 1

                    self.define_vertex_order(_index_offset, prim_indices, direction, segs)
        return vertex_cnt

    def get_plane_details(self, plane):
        name = SimpleNamespace(**{f'axis_{i + 1}': s for i, s in enumerate(plane)})
        index = SimpleNamespace(**{k: 'xyz'.index(v) for k, v in name.__dict__.items()})
        offset = SimpleNamespace(**{k: self.center[v] for k, v in index.__dict__.items()})
        segments = SimpleNamespace(**{k: self.segs[v] for k, v in name.__dict__.items()})

        return name, index, offset, segments

    def create_sides(self, vdata_values, prim_indices):
        vertex_cnt = 0

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
                        vertex_cnt += self.create_thick_side(vertex_cnt, vdata_values, prim_indices, direction, is_front,
                                                             vertex, normal, name, index, offset, segments)
                else:
                    vertex_cnt += self.create_side(vertex_cnt, vdata_values, prim_indices, direction, is_front,
                                                   vertex, normal, name, index, offset, segments)

        return vertex_cnt

    def get_inner_details(self, outer_box_details):
        inner_corners = {}
        inner_dims = {}

        for axis, dim, open_side1, open_side2 in outer_box_details:
            th1 = 0. if open_side1 else min(dim, self.thickness)
            th2 = 0. if open_side2 else min(dim, self.thickness)

            if th1 + th2 > dim:
                th1 = th2 = dim * .5

            inner_corners[f'-{axis}'] = th1
            inner_corners[axis] = th2
            inner_dims[axis] = dim - th1 - th2

        return inner_corners, inner_dims

    def get_geom_node(self):
        self.dims = (self.width, self.depth, self.height)
        self.segs = {'x': self.segs_w, 'y': self.segs_d, 'z': self.segs_z}

        self.open_sides = {
            '-yz': self.open_left,
            'yz': self.open_right,
            '-zx': self.open_back,
            'zx': self.open_front,
            '-xy': self.open_bottom,
            'xy': self.open_top
        }

        if self.thickness > 0:
            outer_details = [
                ['x', self.width, self.open_left, self.open_right],
                ['y', self.depth, self.open_back, self.open_front],
                ['z', self.height, self.open_bottom, self.open_top]
            ]
            self.inner_corners, self.inner_dims = self.get_inner_details(outer_details)

        # Create outer box sides.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_sides(vdata_values, prim_indices)

        if self.thickness > 0:
            box_maker = Cube(*self.inner_dims.values(), *self.segs.values(), 0,
                             not self.invert, *self.open_sides.values())

            # Define the inner box center.
            pts = [(self.inner_corners[f'-{s}'] - self.inner_corners[s]) for s in 'xyz']
            inner_center = Point3(*pts) * 0.5
            box_maker.center = inner_center + self.center

            # Create a geom node of the inner box to connect it to the outer box.
            geom_node = box_maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # If thickness is zero, create only the outer box geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'box')

        return geom_node