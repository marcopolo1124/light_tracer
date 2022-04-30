import pygame, sys
from block import Block, Map, Receiver, Ray
from tracer import find_direction, get_all_rays, get_hit_medium, receiver_hit

#---------------------------------------------------------------------------------------------------------
# Create environment
def get_square(top_left_corner, side_length):
    corner1 = top_left_corner
    corner2 = (top_left_corner[0] + side_length, top_left_corner[1])
    corner3 = (top_left_corner[0] + side_length, top_left_corner[1] + side_length)
    corner4 = (top_left_corner[0], top_left_corner[1] + side_length)
    return (corner1, corner2, corner3, corner4)

def draw_all_ray(data_list):
    for ray_i in data_list:
        if ray_i is not None:
            ray_i.draw_ray(surface)

square_coord = get_square((10,10), 50)

square = Block(
    name="square",
    refraction_index=1.2,
    colour=(255,0,0, 127),
    absorption_coeff=1,
    reflectivity=0,
    vertices=((10,140),(450,140),(450,390))
)

square_2 = Receiver(
    name="square2",
    refraction_index=36,
    init_colour=(0,255,0, 127),
    receive_colour=(0,100, 0, 127),
    absorption_coeff=1,
    reflectivity=0,
    vertices=square_coord
)

lens = Receiver(
    name="lens",
    refraction_index=36,
    init_colour = (255,255,255,255),
    receive_colour=(100,100,100,255),
    absorption_coeff=1,
    reflectivity=0,
    vertices=((440, 400), (420, 340), (410, 280), (410, 220), (420, 160), (440, 100),
              (450, 100), (470, 160), (480, 220), (480, 280), (470, 340), (450, 400))
)

room = Block(
    name="room",
    refraction_index=1,
    colour=(0,0,0, 127),
    absorption_coeff=1,
    reflectivity=1,
    vertices=((0,0), (1000,0), (1000, 500),(0,500))
)
# When blocks overlap, the block that is at define at the start of "Map" will matter the most
room_map = Map(square, square_2)
#---------------------------------------------------------------------------------------------------------
# Game variables
pygame.init()
WIDTH = 1000
HEIGHT = 500
surface = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

angle = 0
pos_1 = [50, 50]
pos_2 = [50, 70]
pos_3 = [50, 90]
pos_4 = [50, 110]
pos_5 = [50, 130]
all_pos = [pos_1, pos_2, pos_3, pos_4, pos_5]


iterations =5


ray_1 = Ray(find_direction(angle), 1, pos_1, room_map)
ray_2 = Ray(find_direction(angle), 1, pos_2, room_map)
ray_3 = Ray(find_direction(angle), 1, pos_3, room_map)
ray_4 = Ray(find_direction(angle), 1, pos_4, room_map)
ray_5 = Ray(find_direction(angle), 1, pos_5, room_map)
all_rays = [ray_1, ray_2, ray_3, ray_4, ray_5]

def house_keeping(ray):
    data_list = get_all_rays(ray)
    hit_blocks = get_hit_medium(data_list)
    receivers_hit = receiver_hit(hit_blocks)
    return data_list, receivers_hit

all_list = []
all_hits = []
for ray_i in all_rays:
    li, ri = house_keeping(ray_i)
    all_list.append(li)
    all_hits += ri

for receiver in room_map.receivers:
    if receiver in all_hits:
        receiver.change_colour(hit=True)
    else:
        receiver.change_colour(hit=False)

move_speed = 10
down_key = False
up_key = False
w_key = False
a_key = False
s_key = False
d_key = False


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                down_key = True
            if event.key == pygame.K_UP:
                up_key = True
            if event.key == pygame.K_w:
                w_key = True
            if event.key == pygame.K_a:
                a_key = True
            if event.key == pygame.K_s:
                s_key = True
            if event.key == pygame.K_d:
                d_key = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                down_key = False
            if event.key == pygame.K_UP:
                up_key = False
            if event.key == pygame.K_w:
                w_key = False
            if event.key == pygame.K_a:
                a_key = False
            if event.key == pygame.K_s:
                s_key = False
            if event.key == pygame.K_d:
                d_key = False

    down = [down_key, up_key, w_key, a_key, s_key, d_key]
    up = [not n for n in down]
    if down_key:
        angle += 1
        # print(ray_1)
        for ray_j in all_rays:
            ray_j.new_trajectory(find_direction(angle))
    if up_key:
        angle -= 1
        for ray_j in all_rays:
            ray_j.new_trajectory(find_direction(angle))
        # print(ray_1)
    if w_key:
        for pos_i, ray_i in zip(all_pos, all_rays):
            pos_i[1] -= move_speed
            ray_i.move_start(pos_i)
    if s_key:
        for pos_i, ray_i in zip(all_pos, all_rays):
            pos_i[1] += move_speed
            ray_i.move_start(pos_i)
    if a_key:
        for pos_i, ray_i in zip(all_pos, all_rays):
            pos_i[0] -= move_speed
            ray_i.move_start(pos_i)
    if d_key:
        for pos_i, ray_i in zip(all_pos, all_rays):
            pos_i[0] += move_speed
            ray_i.move_start(pos_i)

    if not all(up):
        all_list = []
        all_hits = []
        for ray_i in all_rays:
            li, ri = house_keeping(ray_i)
            all_list.append(li)
            all_hits += ri
        for receiver in room_map.receivers:
            if receiver in all_hits:
                receiver.change_colour(hit=True)
            else:
                receiver.change_colour(hit=False)

    pygame.draw.rect(surface, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    
    room_map.draw_map(surface)
    for li in all_list:
        draw_all_ray(li)

    for pos_i in all_pos:
        pygame.draw.circle(surface, (255,255,255, 255), pos_i, 4)

    pygame.display.flip()
    clock.tick(60)