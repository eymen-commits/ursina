from ursina import *

def input(key):
    if key =="s":
        player.z -=1
    if key =="w":
        player.z +=1
    if key =="d":
        player.x +=1
    if key =="a":
        player.x -=1
def update():
    if held_keys["right arrow"]:
        player.x +=0.1


app = Ursina()

cube = Entity(model = "cube",y = 0.5,z = 4.5,x = 0.5)
cube2 = Entity(model = "cube",color = color.red,x = 0.5,y = 0.5,z = -0.5)
cube3 = Entity(model = "cube",texture = "brick",x = -0.5,origin_y= -0.5 ,z = 0.5)
ground = Entity(model = "plane",scale = 200,texture = "white_cube",texture_scale = (200,200))


for i in range (10):
    for j in range (10):
        cube = Entity(model = "cube",texture ="brick",y = 0.5+j,z = 4.5,x = 0.5+i)
        cube = Entity(model = "cube",texture ="brick",y = 0.5+j,z = 9.5,x = 0.5+i)
for i in range (4):
  for j in range(10):
      cube = Entity(model = "cube",texture ="brick",y = 0.5+j,z = 5.5+i,x = 0.5)
      cube = Entity(model = "cube",texture ="brick",y = 0.5+j,z = 5.5+i,x = 9.5)
     


for i in range(10):
    for j in range(10):
        cube = Entity(model = "cube",texture ="brick",y = 0.5,z = 5.5+j,x = 9.5+i)
        
for i in range (9):
 for j in range(9):
        cube = Entity(model = "cube",texture ="brick",y = 1.5,z = 5.5+j,x = 9.5+i)

player = Entity(model = "cube",scale_y=2,color=color.azure,origin_y=-0.5)



EditorCamera()
Sky()
app.run()