import numpy as np
import re
import yaml

class Grid(object):
    """Grid object
    Creates a instance of Grid class

    Args:
        image: Path for the PGM file 
        yaml: Path for the YAML file contains resolution and origin data
        u_length: Length for the cell in meters (default 0.8m)
    """
    def __init__(self, image, yaml_file, u_length_m=0.8):
        self.image = image
        self.resolution, self.origin_mm = self.process_yaml(yaml_file)
        self.unit_length = int(u_length_m / self.resolution)
        self.raw_image, self.cost_map, self.origin_px = self.process_image()        

    def process_yaml(self, yaml_file):
        yaml_data = yaml.safe_load(open(yaml_file))
        origin = tuple(yaml_data['origin'][0:2])
        return yaml_data['resolution'], origin

    def process_image(self):
        raw_image = np.array(self.read_pgm(self.image))
        raw_image[raw_image < 210] = 0
        raw_image[raw_image > 210] = 255
        raw_image = np.rot90(np.flip(raw_image, 0),3)
        size = raw_image.shape

        self.h_units = int(size[0]/self.unit_length)
        self.v_units = int(size[1]/self.unit_length)

        return raw_image, np.zeros([self.h_units, self.v_units]), self.get_origin_px(size)
    
    def get_origin_px(self, image_size):
        origin_x = int(-self.origin_mm[0]/self.resolution)
        origin_y = int(image_size[1] + (self.origin_mm[1]/self.resolution))
        return (origin_x, origin_y)

    def set_obstacles(self):
            width, height = self.cost_map.shape
            num_pixls = self.unit_length ** 2

            data = []
            for i in range(self.h_units):
                for j in range(self.v_units):
                    x0, x1, y0, y1 = int(i*self.unit_length + 1), int((i+1)*self.unit_length), int(j*self.unit_length + 1), int((j+1)*self.unit_length)
                    non_zeros = np.count_nonzero(self.raw_image[x0:x1,y0:y1])
                    if (non_zeros/num_pixls) < 0.85:
                        self.cost_map[i,j] = 100

    def build_graph(self):
        self.set_obstacles()
        free_cells = np.argwhere(np.array(self.cost_map) == 0)
        neighbors = np.array([[0, -1], [0, 1], [-1, 0], [1, 0], [-1, -1], [-1, 1], [1, -1], [1, 1]])
        
        graph = dict()
        converted_graph = dict()
        
        for cell in free_cells:
            current_vertex = tuple(self.get_center(cell))
            converted_current_vertex = self.convert_coordinates(current_vertex)
            graph[current_vertex] = []
            converted_graph[converted_current_vertex] = []
            for neighbor in neighbors:
                neighbor_coord = cell + neighbor
                if self.cost_map[neighbor_coord[0]][neighbor_coord[1]] == 0:
                    graph[current_vertex].append(tuple(self.get_center(neighbor_coord)))
                    converted_graph[converted_current_vertex].append(self.convert_coordinates(self.get_center(neighbor_coord)))

        return converted_graph, graph

    def get_center(self, cell):
        return int(cell[0]*self.unit_length + self.unit_length/2), int(cell[1]*self.unit_length + self.unit_length/2)

    def convert_coordinates(self, screen_coordinate):
        x = round(float((screen_coordinate[0]- self.origin_px[0])*self.resolution), 3)
        y = round(float((-screen_coordinate[1]+ self.origin_px[1])*self.resolution), 3)
        return (x,y)

    def read_pgm(self, file_name, byte_order='>'):
        with open(file_name, 'rb') as file:
            buffer = file.read()
        try:
            header, width, height, maxval = re.search(
                b"(^P5\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n]\s)*)", buffer).groups()
        except AttributeError:
            raise ValueError("Not a raw PGM file: '%s'" % file_name)
        return np.frombuffer(buffer,
                                dtype='u1' if int(maxval) < 256 else byte_order+'u2',
                                count=int(width)*int(height),
                                offset=len(header)
                                ).reshape((int(height), int(width)))


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    grid = Grid('map.pgm', 'map.yaml')
    graph, _ = grid.build_graph()

    cords = list()
    for key in graph:
        for vertex in graph[key]:
            l = np.array([key, vertex])
            xs, ys = zip(*l)
            plt.plot(xs,ys)

    plt.show()
