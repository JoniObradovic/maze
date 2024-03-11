
# Node class for the grid blocks
class Node:
    def __init__(self, grid, row, col, blocksize, colormap):
        self.grid       = grid
        self.row        = row
        self.col        = col
        self.blocksize  = blocksize
        self.colormap   = colormap
        self.type       = {
            'road'      : True,
            'wall'      : False,
            'start'     : False,
            'goal'      : False,
            'visited'   : False,
            'path'      : False,
            }
                       
        self.neighbors  = {
            'top'    : None,
            'bottom' : None,
            'left'   : None,
            'right'  : None
            }                     
        
        self.color      = self.colormap[self.get_node_type()] 
        self.parent     = None
        self.visited    = False
        self.rect_id    = None
        
        #distances
        self.g = 0
        self.h = 0
        self.f = 0
    
    def __str__(self):
        return f"({self.row}, {self.col})"
    
    def __repr__(self):
        return f'[{self.get_node_type():<5} x:{self.row} y:{self.col}]'
    
    def __lt__(self, other):
        return self.f < other.f
    
    def get_node_type(self):
        type_key = next((key for key, value in self.type.items() if value), None)
        if type_key is not None:
            return type_key
        else:
            print("No True value (error)")
    
    def set_node_type(self, nodetype):
        nodetype = nodetype
        self.type = {key: key == nodetype for key in self.type}
        self.update_color()
    
    def get_valid_neighbors(self):
        neighbors = []
        for _, neighbor in self.neighbors.items():
            if neighbor and neighbor.type['road'] and not neighbor.visited:
                neighbors.append(neighbor)
            if neighbor and neighbor.type['goal'] and not neighbor.visited:
                neighbors.append(neighbor)
        return neighbors
    
    def get_neighbors(self):
        return self.neighbors
    
    def update_color(self):
        self.color = self.colormap[self.get_node_type()]
    
    def visit_color(self):
        self.color = self.colormap['visited']
        
    def get_pos(self):
        return (self.row,self.col)