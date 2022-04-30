import numpy as np
from bin_list import Node, BinTree
from block import Ray, Receiver

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

def get_all_rays(head_ray: Ray, iterations=3):
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
