from ursina import *

# --- Core Game Entities and Logic ---

class Particle(Entity):
    """Represents an individual particle in an explosion."""
    def __init__(self, position, color):
        super().__init__(
            model="sphere",
            color=color,
            scale=random.uniform(0.1, 0.3),
            position=position,
            collider="box"
        )
        # Initial random velocity for the explosion effect
        self.velocity = Vec3(random.uniform(-5, 5), random.uniform(5, 10), random.uniform(-5, 5))
        self.lifetime = 30 # Time until particle disappears
        
    def update(self):
        # Apply velocity and gravity
        self.position += self.velocity * time.dt
        self.velocity.y -= 9.8 * time.dt # Simple gravity
        
        # Decrease lifetime and destroy when expired
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)

# --- Car Driving Mechanics ---
def car_drive_update(dt):
    """Handles the car's acceleration, braking, and steering."""
    # Acceleration/Braking
    if held_keys["w"]:
        car.speed += accel * dt
        car.speed = min(car.speed, max_forward)
    elif held_keys["s"]:
        car.speed -= brake * dt
        car.speed = max(car.speed, -max_backward)
    else:
        # Apply drag to slow down when no key is pressed
        car.speed = lerp(car.speed, 0, min(drag * dt, 1))
        
    # Steering
    turn_input = held_keys["a"] - held_keys["d"]
    if abs(car.speed) > 0.1 and turn_input != 0:
        # Turn direction depends on whether the car is moving forward or backward
        sign = 1 if car.speed >= 0 else -1
        car.rotation_y += turn_input * turn_rate * dt * sign
    
    # Move the car
    car.position += car.forward * car.speed * dt

# --- Game Interaction Functions ---

def collect_coin():
    """Checks for player collision with coins and respawns them."""
    for coin in coins_list:
        if distance(player, coin) < 3:
            # Respawn coin at a new random location
            coin.x = random.randint(-90, 90)
            coin.z = random.randint(-90, 90)

def collect_bomb():
    """Checks for player collision with bombs and adds them to inventory."""
    for bomb in bomb_list:
        if distance(player, bomb) < 3:
            bomb_list.remove(bomb)
            player_bombs_list.append(bomb)
            print(f"Bombs collected: {len(player_bombs_list)}")
            bomb.enabled = False
            break

def detonate_bomb():
    """Triggers the explosion effect and applies force to nearby NPCs."""
    if not placed_bombs:
        return
        
    bomb_to_detonate = placed_bombs.pop(0)
    explosion_position = bomb_to_detonate.position

    # Create particle explosion effect
    for i in range(20):
        particle_color = color.random_color()
        Particle(explosion_position, particle_color)

    # Affect nearby NPCs
    for npc in npc_list:
        if distance(npc, explosion_position) < 15:
            # Animate NPC away from the explosion (knockback)
            npc.animate_position(npc.forward * -50, duration=1) 
            
    destroy(bomb_to_detonate) # The bomb is destroyed after detonation

# --- Input Handling ---

def input(key):
    global in_car

    # Get Gun 1
    if key == "g" and distance(player, gun1) < 3:
        get_gun(gun1)
    # Get Gun 2
    if key == "g" and distance(player, gun2) < 3:
        get_gun(gun2)

    # Jump
    if key == "space":
        if player.y < 0.1: # Prevent double jump if already jumping
            player.animate_position((player.x, 2, player.z), duration=0.3, curve=curve.out_circ)
            player.animate_position((player.x, 0, player.z), duration=0.7, delay=0.3, curve=curve.in_quint)
            
    # Teleport Player and NPCs
    if key == "j":
        player.x = random.randint(-50, 50)
    if key == "r":
        for npc in npc_list:
            npc.x = random.randint(-50, 50)
            npc.z = random.randint(-50, 50)
            
    # Place Bomb
    if key == "b":
        if not player_bombs_list:
            print("No bombs left!")
            return
            
        bomb = player_bombs_list.pop()
        bomb.x = player.x
        bomb.z = player.z
        bomb.enabled = True
        placed_bombs.append(bomb)
        
        # Detonate after 5 seconds
        invoke(detonate_bomb, delay=5)
        
        # Range indicator (placed in world, rotation fixed)
        range_indicator = Entity(
            model=Circle(resolution=64),
            color=color.rgba(255, 255, 0, 100),
            scale=15, # Increased scale for better visual (was 10)
            rotation_x=90, 
            position=bomb.position + Vec3(0, 0.01, 0) # Raise slightly to avoid Z-fighting
        )
        destroy(range_indicator, delay=5) # Destroy indicator when bomb detonates

    # Particle explosion test
    if key == "p":
        invoke(particle_explosion, delay=0)
        
    # Shooting
    if key == "left mouse down" and player.gun:
        # Create bullet relative to the gun, then parent it to scene
        bullet = Entity(model="cube", color=color.black, scale=0.6, parent=player.gun)
        bullet.world_parent = scene
        
        # Bullet movement
        target_position = bullet.position + bullet.forward * 100
        bullet.animate_position(target_position, duration=0.9)
        
        bullets.append(bullet)
        # Clean up bullet after it reaches its destination
        invoke(lambda: bullets.remove(bullet), delay=0.9)
        destroy(bullet, 1)

    # Enter/Exit Vehicle
    if key == "enter":
        if in_car:
            # Exit car
            exit_point = car.world_position + car.right * 1.8 + Vec3(0, 0.6, 0)
            player.position = exit_point
            player.enabled = True
            in_car = False
            cam_target = player
            set_hint()
        else:
            # Enter car
            if distance(player, car) < 3:
                in_car = True
                player.enabled = False
                cam_target = car
                set_hint()
                
                # Snap player to car's position but keep the player entity in the scene
                player.parent = car
                player.position = Vec3(0, 0.6, 0.1)
                player.parent = scene # Re-parent to scene for cleaner world-space updates

def get_gun(gun):
    """Picks up a gun, dropping the current one if necessary."""
    if distance(player, gun) > 5:
        return 
        
    # Drop the current gun
    if player.gun:
        player.gun.parent = scene
        player.gun.position = (random.randint(-20, 20), 0.5, random.randint(-20, 20))
        
    # Pick up the new gun
    gun.parent = player
    gun.position = Vec3(0.5, 0.5, 0.5)
    player.gun = gun

def hit_enemy():
    """Checks for bullet collision with NPCs and teleports them."""
    for npc in npc_list:
        for bullet in bullets:
            if distance(npc, bullet) < 3:
                # 'Hit' action: teleport NPC
                npc.x = random.randint(-100, 100)
                npc.z = random.randint(-100, 100)
                # Remove the bullet after hit
                if bullet in bullets:
                    bullets.remove(bullet)
                destroy(bullet)
                return # Only hit one enemy per frame per bullet check


# --- Movement and Collision ---

def npc_movement():
    """Handles the basic movement and collision of NPCs."""
    for npc in npc_list:     
        npc.position += npc.forward * npc.speed * time.dt
        
        # Simple collision check: reset player if touched
        if distance(npc, player) < 1:
            player.position = Vec3(0, 0, 0)
            
        # NPC tries to look at the player when far away, and rotates randomly to patrol
        if distance(npc, player) > 100:
            npc.look_at_xz(player)
            npc.rotation_y += random.randint(-30, 30) # Random turn
        elif distance(npc, player) > 10:
            npc.look_at_xz(player) # Track player when close

def player_move(dt):
    """Third-person movement on foot, relative to camera direction."""
    # Define movement based on standard controller keys (WASD for movement)
    move_input = Vec3(
        held_keys['d'] - held_keys['a'], 
        0, 
        held_keys['w'] - held_keys['s']
    )
    
    if move_input.length() > 0:
        move_input = move_input.normalized() * 6 * dt # 6 is player speed
        
        # Project camera direction onto the XZ plane
        forward = camera.forward
        forward.y = 0 
        forward = forward.normalized()
        
        right = camera.right
        right.y = 0 
        right = right.normalized()
        
        # Calculate world movement vector based on camera orientation
        movement_vector = right * move_input.x + forward * move_input.z
        player.position += movement_vector
        
        # Make player face the direction they are moving
        player.look_at_xz(player.world_position + movement_vector) # Quick turn
        
        # NOTE: Removed the player.world_rotation_y = camera_yaw line, 
        # as the custom camera yaw control has been removed.


# --- Game Loop (Update) ---
def update():
    global in_car
    
    dt = time.dt

    # 1. CAMERA CONTROL (Simplified Third-Person Follow)
    # The camera now follows the target smoothly, staying 8 units back and 4 units up,
    # and always looking at the target.
    if cam_target:
        # Calculate desired position: 8 units back, 4 units up from the target
        # Use the target's forward direction to position the camera behind it
        desired_position = cam_target.world_position - cam_target.forward * 8 + Vec3(0, 4, 0) 
        
        # Smoothly move the camera to the desired position (lerp)
        camera.position = lerp(camera.position, desired_position, min(8 * dt, 1))
        
        # Always look at the target's center (slightly above ground)
        camera.look_at(cam_target.world_position + Vec3(0, 0.6, 0))

    # 2. MOVEMENT LOGIC
    if in_car:
        car_drive_update(dt)
    else:
        player_move(dt)

    # 3. GAME LOGIC UPDATES
    collect_coin()
    npc_movement()
    collect_bomb()
    
    # Player facing the mouse point on the ground (only when on foot)
    if not in_car and mouse.world_point:
        # Look at mouse point, but only on the XZ plane to prevent player tipping over
        # We only want this when NOT moving with WASD (as movement handles rotation in player_move)
        if held_keys['w'] == 0 and held_keys['s'] == 0 and held_keys['a'] == 0 and held_keys['d'] == 0:
            player.look_at_xz(mouse.world_point)
            
    hit_enemy()
    set_hint()
    
    # Restore player to ground if somehow high up (e.g., after jump)
    if player.y > 0.1:
        # Check if the player is still falling, if not, bring them down smoothly
        if player.y > 2: # Stop falling animation if already high up
            player.y -= 9.8 * dt 
        else: # Small adjustment to ensure they settle on the ground
            player.y = lerp(player.y, 0, min(10 * dt, 1))
        
        # Clamp position to ground
        if player.y < 0:
             player.y = 0


def particle_explosion():
    """Generates a large particle explosion at the player's position."""
    for i in range(250):
        particle_color = color.random_color()
        Particle(player.position, particle_color)

# --- Initialization ---

app = Ursina(borderless=False)

# Environment
ground = Entity(model="plane", scale=200, texture="grass", texture_scale=(200, 200), collider="box")
Sky()

# Global Lists
player_bombs_list = []
coins_list = []
npc_list = []
bomb_list = []
placed_bombs = []
bullets = []

# Populate World
for i in range(10):
    x, z = random.randint(-90, 90), random.randint(-90, 90)
    coin = Entity(model="sphere", scale=0.5, color=color.yellow, x=x, y=0.5, z=z, collider='sphere')
    coins_list.append(coin)
    
for i in range(10):
    x, z = random.randint(-90, 90), random.randint(-90, 90)
    bomb = Entity(model="sphere", scale=0.5, color=color.black, x=x, y=0.5, z=z, collider='sphere')
    bomb_list.append(bomb)

for i in range(10): # Reduced NPC count for performance
    x, z = random.randint(-90, 90), random.randint(-90, 90)
    npc = Entity(model="cube", scale_y=2, color=color.red, x=x, origin_y=-0.5, z=z, speed=random.uniform(5, 10), collider='box')
    npc_list.append(npc)    

# Player Setup
player = Entity(model="cube", scale_y=2, color=color.azure, origin_y=-0.5, gun=None, collider='box')

# Gun Setup
gun1 = Button(parent=scene, model="cube", color=color.blue, origin_y=-.5, position=(random.randint(-20, 20), 0.5, random.randint(-20, 20)), collider="box", scale=(0.2, 0.2, 1))
gun2 = Button(parent=scene, model="cube", color=color.red, origin_y=-.5, position=(random.randint(-20, 20), 0.5, random.randint(-20, 20)), collider="box", scale=(0.2, 0.2, 1))

# Car Setup
car = Entity(model="yellowcar", scale=0.01, position=(4, 0, 10), origin_y=-0.5, speed=0, collider='box')

# Car Parameters
max_forward = 14
max_backward = 6
accel, brake, drag = 18, 28, 4.5
turn_rate = 85
in_car = False

# Camera and Hint Setup
hint = Text("Hint", y=0.4, x=0.4, scale=0.9, color=color.black)

def set_hint():
    """Updates the hint text based on game state and proximity to the car."""
    if in_car:
        hint.text = "In Car: W/S (ACCEL/BRAKE) A/D (STEER) ENTER (Exit)"
    else:
        near = distance(player, car) < 3
        hint.text = f"On Foot: WASD (Move) SPACE (Jump) G (Get Gun) B (Place Bomb) ENTER ({'Enter Car' if near else 'Too Far'})"

set_hint()
cam_target = player

# --- CAMERA VARIABLES ---
mouse_speed = 150 # This variable is no longer used but kept for simple future re-implementation.

# Initial Camera Positioning
camera.position = Vec3(0, 4, -8)
camera.look_at(cam_target)

# Run the application
app.run()
