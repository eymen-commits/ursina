from ursina import *

class Particle(Entity):
    def __init__(self,position, color):
        super().__init__(
            model="sphere",
            color=color,
            scale=random.uniform(0.1,0.3),
            position=position,
            collider="box"
        )


        self.velocity = Vec3(random.uniform(-5,5),random.uniform(5,10),random.uniform(-5,5))
        self.lifetime = 30
    def update(self):
        self.position += self.velocity*time.dt
        self.velocity.y -=9.8*time.dt
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)





#MARK:CARDRİVE
def cardrive(dt):
    if held_keys["w"]:
        car.speed += accel*dt
        car.speed = min(car.speed,maxforward)
    elif held_keys["s"]:
        car.speed -= brake*dt
        car.speed = max(car.speed,-maxbackward)
    else:
        car.speed =lerp(car.speed,0,min(drag*dt,1))
    #direksiyon
    turninput=held_keys["a"]-held_keys["d"]
    if abs(car.speed)>0.1 and turninput!=0:
        sign=1 if car.speed>=0 else -1
        car.rotation_y+= turninput*turnrate*dt*sign
    
    
    









def coinyakala():
    for coin in coinslist:
        if distance(player,coin)<3:
            coin.x = random.randint (-30,30)
            coin.z = random.randint (-30,30)
def bombyakala():
    for bomb in bomblist:
        if distance(player,bomb)<3:
            bomblist.remove(bomb)
            playerbombslist.append(bomb)
            print(len(playerbombslist))
            bomb.enabled = False
            break
def bombayipatlat():
    for i in range(20):
        particle_color = color.random_color()
        particle = Particle(koyulanbombs[0].position, particle_color)
    for npc in npclist:
      for bomb in koyulanbombs:
         if distance(npc,bomb)<15:
             npc.animate_position(npc.forward*-50)
    b = koyulanbombs.pop()
    destroy(b,3)
 #MARK:İNPUT   
def input(key):

    if key =="g" and distance(player,gun1)<3:
        getgun()
    if key =="g" and distance(player,gun2)<3:
        getgun2()
    if key =="s":
        player.z -=3
    if key =="w":
        player.z +=3
    if key =="d":
        player.x +=3
    if key =="a":
        player.x -=3
    if key=="space":
        player.y = 5 
    if key == "j":
        player.x = random.randint(-50,50)
    if key =="r":
        for npc in npclist:
            npc.x = random.randint(-50,50)
            npc.z = random.randint(-50,50)
    if key =="b":
        if len(playerbombslist)==0:
            return
        bomb = playerbombslist.pop()
        bomb.x=player.X
        bomb.z =player.z
        bomb.enabled = True
        koyulanbombs.append(bomb)
        invoke(bombayipatlat,delay = 5)
        # Çember (menzil göstergesi)
        menzil = Entity(
    model=Circle(resolution=64),  # yuvarlak model
    color=color.rgba(255, 255, 0, 100),  # yarı saydam sarı
    scale=10,  # menzil yarıçapı
    rotation_x=90,  # zemine paralel hale getir
    position=bomb.position
)
        destroy(menzil,delay=8)
    if key =="p":
        invoke(particle_patlat,delay=3)
    if key =="left mouse down" and player.gun:
        bullet = Entity(model="cube",color=color.black,scale=0.6,parent=player.gun)
        bullet.world_parent=scene
        bullet.animate_position(player.gun.position+bullet.forward*50)
        bullets.append(bullet)
        invoke(bullet_pop,bullet,delay=0.9)
        destroy(bullet,1)
    if key=="enter":
        if incar:
            exitpoint=car.world_position+car.right*1.8+Vec3(0,0.6,0)
            player.position = exitpoint
            player.enabled =True
            incar=False
            camtarget=player
            sethint()
        else:
            if distance(player,car)<2:
                incar = True
                player.enabled=False
                camtarget=car
                sethint()
                player.parent=car
                player.position=Vec3(0,0.6,0.1)
                player.parent=scene

def bullet_pop(bullet):
    bullets.remove(bullet)
def hit_enemy():
    for npc in npclist:
        for bullet in bullets:
            if distance(npc,bullet)<3:
                npc.x = random.randint(-100,100)
                npc.z = random.randint(-100,100)







def npc_hareket():
    for npc in npclist:     
        npc.position +=  npc.forward * npc.speed* time.dt
        if distance(npc,player)<1:
            player.x = 0
            player.z= 0
        if distance(npc,player)>100:
            npc.look_at_xz(player)
            npc.rotation_y += random.randint(-30,30)

 # MARK:UPDATE
def update():
    global yaw,pitch
    if mouse.right:
        yaw -= mouse.velocity[0]*mouse_sensitivity
        pitch += mouse.velocity[1]*mouse_sensitivity
        pitch=clamp(pitch,-15,45)
    if camtarget:
        t=Entity()
        t.position=camtarget.world_position
        t.rotation_y=yaw
        t.rotation_x=pitch
        istenen = t.world_position+t.back+Vec3(0,3,0)
        destroy(t)
        camera.position=lerp(camera.position,istenen,min(8*time.dt,1))
        camera.look_at(camtarget.world_position+Vec3(0,0.6,0))
    if incar:
        cardrive(time.dt)
    else:
        player_move(time.dt)


    if held_keys["right arrow"]:
        player.x +=0.1
    if player.y >= 5:
        player.animate_position((player.x,0,player.z),duration=5)
    coinyakala()
    npc_hareket()
    bombyakala()
    if mouse.world_point:
     player.look_at_xz(mouse.world_point)
    hit_enemy()
    sethint()
    



app = Ursina(borderless=False)


ground = Entity(model = "plane",scale = 200,texture = "white_cube",texture_scale = (200,200),collider="box")
playerbombslist=[]
coinslist = []
npclist= []
bomblist= []

koyulanbombs=[]
for i in range(10):
    x = random.randint(-90,90)
    z = random.randint(-90,90)
    coin = Entity(model = "Sphere",scale =  0.5,color = color.yellow,x=x,y=1 , z=z) 
    coinslist.append(coin)
    
for i in range(10):
    x = random.randint(-90,90)
    z = random.randint(-90,90)
    bomb = Entity(model = "Sphere",scale =  0.5,color = color.black,x=x,y=1 , z=z) 
    bomblist.append(bomb)

for i in range(100):
    x = random.randint(-90,90)
    z = random.randint(-90,90)
    npc = Entity(model = "cube",scale_y = 2,color=color.red,x=x,origin_y=-0.5,z=z,speed = random.uniform(5,10))
    npclist.append(npc)  



player = Entity(model = "cube",scale_y=2,color=color.azure,origin_y=-0.5,gun=None)

def particle_patlat():
     for i in range(250):
        particle_color = color.random_color()
        particle = Particle(player.position, particle_color)
gun1 = Button(parent=scene,model="cube",color=color.blue,origin_y =-.5,position=(random.randint(-20,20),0,random.randint(-20,20)),collider="box",scale =(0.2,0.2,1))
def getgun():
    if distance(player,gun1)>5 : 
        return   
    if player.gun:
        player.gun.parent=scene
        player.gun.position=(random.randint(-20,20),0,random.randint(-20,20))
    gun1.parent=player
    gun1.position=Vec3(0.5,0.5,0.5)
    player.gun=gun1


gun1.on_click=getgun

gun2 = Button(parent=scene,model="cube",color=color.red,origin_y =-.5,position=(random.randint(-20,20),0,random.randint(-20,20)),collider="box",scale =(0.2,0.2,1))
def getgun2():
    if distance(player,gun2)>5 : 
        return   
    
    if  player.gun:
        player.gun.parent=scene
        player.gun.position=(random.randint(-20,20),0,random.randint(-20,20))
        
    gun2.parent=player
    gun2.position=Vec3(0.5,0.5,0.5)
    player.gun=gun2


gun2.on_click=getgun2
bullets=[]




car = Entity(model="yellowcar",scale=0.01,position=(4,0,10),origin_y = -0.5,speed=0)
maxforward =14
maxbackward = 6
accel,brake,drag =18,28,4.5
turnrate=85
incar=False

hint = Text("ipucu",  y=0.4,x=0.4,scale=0.9,color=color.black)
def sethint():
    if incar:
        hint.text="Arabadasin W/S (İLERİ-GERİ)A/D (DİREKSİYON) Enter(in) esc(cik)"
    else:
        near = distance(player,car)<2
        hint.text=f'yaya wasd , enter(bin) space(zipla){"okey" if near else "olumsuz"}'
sethint()
EditorCamera()
Sky()
app.run()