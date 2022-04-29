import numpy as np
from bin_list import Node, BinTree
import sys, pygame
from line_classes import Ray, Block, Map, Receiver

def find_direction(angle):
    return np.array([np.cos(angle*np.pi/180), np.sin(angle*np.pi/180)])

def trace_ray(ray_node: Node, iteration):
    if iteration == 0 or ray_node is None:
        return None
    iteration -= 1
    ray_data = ray_node.data
    if ray_data is not None:
        reflected_ray = ray_data.reflect()
        refracted_ray = ray_data.refract()
        reflected_node = Node(reflected_ray)
        refracted_node = Node(refracted_ray)
        ray_node.add_point(reflected_node, refracted_node)
        trace_ray(reflected_node, iteration)
        trace_ray(refracted_node, iteration)    

def get_all_rays(head_ray, iterations=1):
    head_node = Node(head_ray)
    trace_ray(head_node, iterations)
    tree = BinTree(head_node)
    data_list = tree.get_data_list()
    return data_list

def receiver_hit(med_list):
    hit_list = []
    for medium in med_list:
        if isinstance(medium, Receiver):
            hit_list.append(medium)
    return hit_list

def get_hit_medium(data_list):
    hit_blocks = []
    for ray in data_list:
        if ray is not None:
            hit_blocks += [ray.medium, ray.hit_block]
    return hit_blocks


#---------------------------------------------------------------------------------------------------------
# Create environment
square = Block(
    name="square",
    refraction_index=1.2,
    colour=(255,0,0, 127),
    absorption_coeff=1,
    reflectivity=0,
    vertices=((10,140),(450,140),(450,390))
)

square_2 = Block(
    name="square2",
    refraction_index=8,
    colour=(0,255,0, 127),
    absorption_coeff=1,
    reflectivity=0,
    vertices=((450,190),(900,190),(900,440),(450,440))
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
room_map = Map(lens, room)
all_receivers = [lens]
#---------------------------------------------------------------------------------------------------------
# Game variables
pygame.init()
screen_width = 1000
screen_height = 500
surface = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

angle = 0
position = [50, 50]
light_ray = Ray(find_direction(angle), 1, position, room_map)
data_list = get_all_rays(light_ray)
hit_blocks = get_hit_medium(data_list)
receivers_hit = receiver_hit(hit_blocks)
for receiver in all_receivers:
    if receiver in receivers_hit:
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
        # print(light_ray)
        light_ray.new_trajectory(find_direction(angle))
    if up_key:
        angle -= 1
        light_ray.new_trajectory(find_direction(angle))
        # print(light_ray)
    if w_key:
        position[1] -= move_speed
        light_ray.move_start(position)
    if s_key:
        position[1] += move_speed
        light_ray.move_start(position)
    if a_key:
        position[0] -= move_speed
        light_ray.move_start(position)
    if d_key:
        position[0] += move_speed
        light_ray.move_start(position)

    if not all(up):
        data_list = get_all_rays(light_ray)
        hit_blocks = get_hit_medium(data_list)
        receivers_hit = receiver_hit(hit_blocks)
        print(receivers_hit)
        for receiver in all_receivers:
            if receiver in receivers_hit:
                receiver.change_colour(hit=True)
            else:
                receiver.change_colour(hit=False)

    pygame.draw.rect(surface, (0, 0, 0), (0, 0, screen_width, screen_height))
    
    room_map.draw_map(surface)
    for ray_i in data_list:
        if ray_i is not None:
            ray_i.draw_ray(surface)
    pygame.draw.circle(surface, (255,255,255, 255), position, 10)

    pygame.display.flip()
    clock.tick(60)