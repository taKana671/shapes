# shapes

This repository provides the classes to procedurally make 3D shapes to be used in the games made with panda3D.
By changing parameter values, various kinds of rectangle, cone, cylinder, shape, torus and plane can be created.
The simple editor, ModelDisplay, enables you to create such shape models while confirming their parameter values.

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






