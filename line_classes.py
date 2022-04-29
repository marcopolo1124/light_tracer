import numpy as np
from numpy.linalg import LinAlgError
import pygame


class Line:
    """
    A Line represented in vectors. 
    start point is where the line starts, and direction is a vector parallel to the line
    in form START + n DIRECTION where n is the parameter
    """
    def __init__(self, start_point, direction):
        self.start_point = np.array(start_point)
        self.direction = np.array(direction)
        self.unit_direction = direction / np.linalg.norm(direction)
        self.normal = self.find_normal()
        self.unit_normal = self.normal / np.linalg.norm(self.normal)
        self.line = np.array([self.start_point, self.direction])
    def find_normal(self):
        """Uses the direction vector to find a normal"""
        normal_x_direction = -self.direction[1]
        normal_y_direction = self.direction[0]
        normal = np.array([normal_x_direction, normal_y_direction])
        return normal
    def find_intersection_point(self, param):
        """Takes n param to get a point on the line"""
        intersection_point = self.start_point + (param * self.direction)
        return intersection_point
    def find_line_intersection(self, line2):
        """
        Find the param at where line intersect.
        param[0] has the n param for the current line
        param[1] has the n param for the incoming line
        """
        sub_vector = self.start_point - line2.start_point
        dir_matrix = np.array([line2.direction, -1 * self.direction]).transpose()
        try:
            dir_matrix_inv = np.linalg.inv(dir_matrix)
        except LinAlgError:
            # No solution --> Non intersecting
            return None
        param = dir_matrix_inv.dot(sub_vector)
        param[0], param[1] = param[1], param[0]
        return param
    def intersecting_point(self, line2):
        """Only returns the param of the incoming line"""
        intersection = self.find_line_intersection(line2)
        if intersection is None:
            return None
        return self.find_intersection_point(intersection[0])
    def reflect_ray(self, line_boundary):
        """reflect itself on a line boundary"""
        intersection = self.intersecting_point(line_boundary)
        if intersection is None:
            return
        # Find a line perpendicular to the boundary and intersect current line
        # Can't intersect line at the intersection of boundary and line
        perp_line = Line(self.start_point, line_boundary.unit_normal)
        perp_intersection = perp_line.find_line_intersection(line_boundary)
        if perp_intersection is None:
            return None
        reflected_start = perp_line.find_intersection_point(2*perp_intersection[0])
        reflected_direction = intersection - reflected_start
        return reflected_direction
    def change_direction(self, direction):
        """For rotating the line"""
        self.direction = direction
        self.unit_direction = direction / np.linalg.norm(direction)
        self.normal = self.find_normal()
        self.unit_normal = self.normal / np.linalg.norm(self.normal)
        self.line = np.array([self.start_point, self.direction])
    def change_start(self, new_start):
        """For moving the line"""
        self.start_point = np.array(new_start)
        self.line = np.array([self.start_point, self.direction])
    def __repr__(self):
        return f"Starting point {self.start_point} direction {self.direction}"



class Boundary(Line):
    """
    A more specialized line for making boundaries.
    The boundary will start with n param = 0 and end at n param = 1 (see Line docstring)
    Also has draw onto surface functions
    """
    def __init__(self, start_coordinates, end_coordinates, colour, reflectivity):
        self.start_coordinates = np.array(start_coordinates)
        self.end_coordinates = np.array(end_coordinates)
        direction = self.end_coordinates - self.start_coordinates
        super().__init__(self.start_coordinates, direction)
        self.colour = colour
        self.reflectivity = reflectivity

    def draw_boundary(self, surface):
        """draws the boundary onto the surface"""
        object_colour = self.colour
        return pygame.draw.line(surface, object_colour, self.start_coordinates, self.end_coordinates, 1)

    def boundary_intersection(self, line):
        """returns what n param it takes for the incoming line to hit the boundary"""
        param = line.find_line_intersection(self)
        if param is None:
            return None
        if param[1] < 0 or param[1] > 1:
            return None
        return param[0]


class Block:
    """
    Block class refers to an object displayed on screen
    """
    def __init__(self, name, refraction_index, colour, absorption_coeff, reflectivity, vertices):
        self.name = name
        self.refraction_index = refraction_index
        self.reflectivity = reflectivity
        self.absorption_coeff = absorption_coeff
        self.vertices = []
        self.edges = []
        self.colour = colour
        num_of_vertices = len(vertices)
        for vertex in vertices:
            self.vertices.append(np.array(vertex))
        
        for i, vertex in enumerate(vertices):
            next_vertex = (i+1) % num_of_vertices
            edge = Boundary(self.vertices[i], self.vertices[next_vertex], colour, reflectivity)
            self.edges.append(edge)
    
    def __repr__(self):
        return self.name

    def enclosed_point(self, point, direction):
        point = np.array(point) + 0.1 * np.array(direction)
        test_line = Line(point, direction)
        counter = 0
        for edge in self.edges:
            intersect = edge.boundary_intersection(test_line)
            if intersect is None:
                continue
            if intersect > 0.01:
                counter += 1
        if counter % 2 == 1:
            return True
        else:
            return False
    
    def draw_block(self, surface):
        for edge in self.edges:
            edge.draw_boundary(surface)
        lx, ly = zip(*self.vertices)
        min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(shape_surf, self.colour, [(x - min_x, y-min_y) for x, y in self.vertices])
        surface.blit(shape_surf, target_rect)


class Map:
    def __init__(self, *blocks):
        self.boundaries = []
        for block in blocks:
            self.boundaries += block.edges
        self.blocks = blocks

    def block_boundary(self, boundary) -> Block:
        """Checks which block a boundary belongs to"""
        for block in self.blocks:
            if boundary in block.edges:
                return block
        return None
    
    def block_enclosed(self, point, direction) -> Block:
        for block in self.blocks:
            if block.enclosed_point(point, direction):
                return block
        return None

    def draw_map(self, surface):
        for block in self.blocks:
            block.draw_block(surface)


class Ray(Line):
    def __init__(self, direction, starting_power, start_point, room_map:Map):
        super().__init__(start_point, direction)
        self.power = starting_power
        self.room_map = room_map
        self.medium = room_map.block_enclosed(start_point, direction)
        self.boundary_hit, self.shortest_path = self.collision()

        self.end_point = self.start_point + 100 * self.direction
        if self.boundary_hit is not None:
            self.end_point = self.find_intersection_point(self.shortest_path)

    def move_start(self, new_start):
        self.change_start(new_start)
        self.medium = self.room_map.block_enclosed(self.start_point, self.direction)
        self.boundary_hit, self.shortest_path = self.collision()
        self.end_point = self.start_point + 100 * self.direction
        if self.boundary_hit is not None:
            self.end_point = self.find_intersection_point(self.shortest_path)

    def collision(self):
        """Finds the boundary that is in the ray's path"""
        shortest_path = np.inf
        boundary_hit = None
        
        for boundary in self.room_map.boundaries:
            distance = boundary.boundary_intersection(self)
            if distance is not None:
                if distance <= 0.01:
                    continue
            else:
                continue
            if  distance < shortest_path:
                shortest_path = distance
                boundary_hit = boundary
        return boundary_hit, shortest_path
    
    def new_trajectory(self, new_direction):
        self.change_direction(np.array(new_direction))
        self.boundary_hit, self.shortest_path = self.collision()
        self.end_point = self.start_point + 100 * self.direction
        if self.boundary_hit is not None:
            self.end_point = self.find_intersection_point(self.shortest_path)

    def reflect(self):
        if self.boundary_hit is None:
            return None
        reflect_direction = self.reflect_ray(self.boundary_hit)
        return Ray(reflect_direction, self.power, self.end_point, self.room_map)
            
    def refract(self):
        # No transmitted rays if it didn't hit anything
        if self.boundary_hit is None:
            return None
        if self.boundary_hit.reflectivity == 1:
            return None
        block_enclosed = self.room_map.block_enclosed(self.end_point, self.direction)
        if block_enclosed is None:
            refraction_r = 1
        else:
            refraction_r = block_enclosed.refraction_index

        if self.medium is None:
            refraction_i = 1
        else:
            refraction_i = self.medium.refraction_index

        refraction_constant = refraction_i/refraction_r
        incidence = self.unit_direction
        normal = self.boundary_hit.unit_normal
        dot_prod = np.dot(incidence, normal)
        neg_power = 0
        if dot_prod < 0:
            neg_power = 1
        if dot_prod >= 0:
            neg_power = 2
        i_perp = dot_prod * normal
        i_par = incidence - i_perp

        if np.linalg.norm(i_par) <= 1/refraction_constant:
            t_par = refraction_constant * i_par
            t_perp = (-1)**neg_power * np.sqrt(1 - (np.dot(t_par, t_par)))*normal
            transmitted_direction = t_par + t_perp
            return Ray(transmitted_direction, self.power, self.end_point, self.room_map)   
        else:
            return None
        
    def draw_ray(self, surface):
        pygame.draw.line(surface, (255,255,0), self.start_point, self.end_point)