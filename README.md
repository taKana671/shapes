# shapes

Provides the classes to procedurally generate 3D shape models, which can be used when programming 3D games by panda3D.   
In addition to the basic 3D shapes: box, cone, cylinder, sphere and torus, by changing parameter values, various kinds of 3D shapes can be created. 
For example, changing the number of cone's bottom sides to 4 generates a square pyramid shape model.  
The simple editor, ModelDisplay, enables you to create such shape models while confirming their parameter values.  
And this repositroy is also a submodule for [DeliveryCart](https://github.com/taKana671/DeliveryCart) and [MazeLand](https://github.com/taKana671/MazeLand).

https://github.com/user-attachments/assets/43e0ae50-9e07-4ac0-9047-57782b8ed7a5

# Requirements
* Panda3D 1.10.14
* numpy 1.23.5

# Environment
* Python 3.11
* Windows11

# Usage of class
* There are 7 classes, including Sphere, Box, Torus, Cone, Plane, QuickSphere and Plane.
* Instantiate and call create method.
* Change parameter values as needed in instantiation.
```
from shapes.src import Box

box_maker = Box()
model = box_maker.create() 
```
# Usage of editor
```
>>> cd shapes
>>> python model_display.py
```






