from node import Node
from collections import deque

# Grid


class Grid:
    # generate Row x Col sized grid of Nodes
    def __init__(self, app, canvas, rows, cols, blocksize, colormap):
        self.app = app
        self.rows = rows
        self.cols = cols
        self.canvas = canvas
        self.blocksize = blocksize
        self.colormap = colormap
        self.start = None
        self.goal = None
        self.grid = [
            [Node(self, r, c, blocksize, colormap) for c in range(self.cols)] for r in range(self.rows)
            ]
        self.drawqueue = deque()
        self.width = blocksize * cols
        self.height = blocksize * rows

    def draw_grid(self):
        for row in self.grid:
            for node in row:
                x_position = node.col * self.blocksize
                y_position = node.row * self.blocksize
                node.rect_id = self.canvas.create_rectangle(x_position,
                                                            y_position,
                                                            x_position + self.blocksize,
                                                            y_position + self.blocksize,
                                                            fill=node.color,
                                                            outline=self.colormap['grid'])

    # call app wait
    def call_wait(self):
        self.app.wait()

    # add visited nodes into queue to be drawn after search
    def draw_queue(self, task, node=None):

        if task is not None and task == "add":
            self.drawqueue.append(node)

        elif task == "draw":

            for node in self.drawqueue:
                if self.app.search_running['path'] == False:
                    break
                self.draw_node(node)
                self.call_wait()

            self.call_wait()
            self.drawqueue.clear()

        elif task == "clear":
            self.drawqueue.clear()

    # Draw single node

    def draw_node(self, selected):
        x_position = selected.col * self.blocksize
        y_position = selected.row * self.blocksize
        selected.rect_id = self.canvas.create_rectangle(x_position,
                                                        y_position,
                                                        x_position + self.blocksize,
                                                        y_position + self.blocksize,
                                                        fill=selected.color,
                                                        outline=self.colormap['grid'])

    # Get node from given mouse coordinates

    def get_node_from_coordinates(self, x, y):
        # subtract the padding from the location and divide it with the blocksize
        x_idx = y // self.blocksize
        y_idx = x // self.blocksize

        # check if valid location
        if 0 <= x_idx and x_idx < self.height and 0 <= y_idx and y_idx < self.width:
            return self.grid[x_idx][y_idx]

        else:
            # if not valid, return none
            return None

    # Get all nodes
    def get_nodes(self):
        temp = [[ele for ele in row] for row in self.grid]
        return temp

    # Clear whole grid to default state
    def empty_grid(self):
        self.grid = []
        self.grid = [[Node(self, r, c, self.blocksize, self.colormap)
                      for c in range(self.cols)] for r in range(self.rows)]
        self.canvas.delete("all")
        self.draw_grid()
        self.app.update_infopanel("Grid Reset")

    # reset the search results (colored path nodes etc)
    def empty_search(self):
        for row in self.grid:
            for node in row:
                node.visited = False
                node.parent = None

                nodetype = node.get_node_type()

                if nodetype == 'start':
                    node.set_node_type('start')

                elif nodetype == 'goal':
                    node.set_node_type('goal')

                elif nodetype == 'road' or nodetype == 'path':
                    node.set_node_type('road')

        self.canvas.delete('all')
        self.draw_grid()

        self.app.update_infopanel(f"search reset")

    # Check all node neighbors
    def neighbors(self):
        for x in range(self.rows):
            for y in range(self.cols):
                current_node = self.grid[x][y]
                if x > 0:
                    current_node.neighbors["left"] = self.grid[x - 1][y]
                if x < len(self.grid) - 1:
                    current_node.neighbors["right"] = self.grid[x + 1][y]
                if y > 0:
                    current_node.neighbors["top"] = self.grid[x][y - 1]
                if y < len(self.grid[0]) - 1:
                    current_node.neighbors["bottom"] = self.grid[x][y + 1]

        self.app.update_infopanel("Neighbors set")
