import array

from panda3d.core import Point3

from .rounded_box import Sides, RoundedBox


class CapsulePrism(RoundedBox):

    """Create a geom node of capsule prism.
        Args:
            width (float): dimension along the x-axis; more than zero.
            depth (float): dimension along the y-axis; more than zero.
            height (float): dimension along the z-axis; more than zero.
            segs_w (int): the number of subdivisions in width; more than 1.
            segs_d (int): the number of subdivisions in depth; more than 1.
            segs_z (int): the number of subdivisions in height; more than 1.
            thickness (float): offset of inner box sides; 0 means no inner box.
            rounded_left (bool): if True, left side is rounded.
            rounded_right (bool): if True, right side is rounded.
            open_top(bool): used only when thickness is 0; if True, no top side.
            open_bottom(bool): used only when thickness is 0; if True, no bottom side.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, width=1., depth=1., height=1., segs_w=4, segs_d=4, segs_z=4, thickness=0.,
                 rounded_left=True, rounded_right=True, open_top=False, open_bottom=False, invert=False):
        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            invert=invert,
            open_left=rounded_left,
            open_right=rounded_right,
            open_top=True if thickness > 0 else open_top,
            open_bottom=True if thickness > 0 else open_bottom
        )

        self.rounded_left = rounded_left
        self.rounded_right = rounded_right

    def create_rounded_corners(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self.height * 0.5)

        match side:

            case Sides.LEFT:
                center.x = -self.width * 0.5
                start_angle = 90 if self.invert else 270

            case Sides.RIGHT:
                center.x = self.width * 0.5
                start_angle = 270 if self.invert else 90

        vertex_cnt = self.create_vertical_edge_cylinder(
            vertex_cnt, vdata_values, prim_indices, self.height, center, start_angle, 180
        )
        return vertex_cnt

    def create_corners(self, vertex_cnt, vdata_values, prim_indices):
        if self.rounded_left:
            vertex_cnt = self.create_rounded_corners(
                vertex_cnt, vdata_values, prim_indices, Sides.LEFT)

        if self.rounded_right:
            vertex_cnt = self.create_rounded_corners(
                vertex_cnt, vdata_values, prim_indices, Sides.RIGHT)

        return vertex_cnt

    def define_variables(self):
        # Variables for the box.
        super().define_variables()
        # Variables for the left and right cylinders.
        self.c_radius = self.depth / 2.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        self.c_segs_tc = 0 if self.thickness <= 0 and self.open_top else self.segs_d
        self.c_segs_bc = 0 if self.thickness <= 0 and self.open_bottom else self.segs_d

    def get_geom_node(self):
        self.define_variables()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_sides(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)

        if self.thickness > 0:
            maker = CapsulePrism(
                width=self.inner_dims['x'],
                depth=self.inner_dims['y'],
                height=self.inner_dims['z'],
                segs_w=self.segs_w,
                segs_d=self.segs_d,
                segs_z=self.segs_z,
                thickness=0,
                rounded_left=self.rounded_left,
                rounded_right=self.rounded_right,
                open_top=True,
                open_bottom=True,
                invert=not self.invert
            )

            # Define the inner box center.
            maker.center = self.calc_inner_box_center()

            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'capsule_prism')

        return geom_node