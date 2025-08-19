# shapes

Provides the modules to procedurally generate 3D shape models, which can be used when programming 3D games by panda3D.
In addition to generating basic 3D shapes, you can create many variations by changing parameters.
For example, you can make them hollow inside or cut them like a pie.
Currently, the following 3D shapes can be created, but I plan to add more in the future. 
A model editor [3DModelEditor](https://github.com/taKana671/3DModelEditor) allows you to create a 3D model while seeing how the shape changes as you change the parameters.  
And this repositroy is also a submodule for
* https://github.com/taKana671/VoronoiCity
* https://github.com/taKana671/DeliveryCart

![Image](https://github.com/user-attachments/assets/b4db70b2-81be-4556-b81d-2f1c36a9ffde)
![Image](https://github.com/user-attachments/assets/40ca644a-a478-467d-9f72-1ca3e32b4fc2)
![Image](https://github.com/user-attachments/assets/2da62053-40d0-4938-bec3-13b6ba5424bc)

# Requirements
* Panda3D 1.10.15
* numpy 2.2.4

# Environment
* Python 3.12
* Windows11

# Usage of modules

* There are 12 classes, including Cylinder, Sphere, Box, Torus, Cone, Plane, QuickSphere, Capsule, RightTriangularPrism, EllipticalPrism, CapsulePrism and RoundedCornerBox, but they all have the same usage.
* Instantiate and call create method.
* When instantiating, change parameters as necessary.
* Returnd model is a NodePath of Panda3D.
```
from shapes.src import Box

box_maker = Box()
model = box_maker.create() 
```




