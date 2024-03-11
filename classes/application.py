
import tkinter as tk
import customtkinter as ctk
import heapq
import text
from collections import deque
from math import sqrt
from PIL import Image
from grid import Grid

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
# Themes: blue (default), dark-blue, green
ctk.set_default_color_theme("dark-blue")


# Colors
COLORMAP = {
    'button':       "#0047AB",  # Cobalt blue
    'toggle':       "#5F9EA0",  # Cadet blue
    'theme':        "#1a1a1a",  # Dark gray
    'grid':         "#36454F",  # Charcoal
    'wall':         "#000000",  # BLack
    'road':         "#5a5a5a",  # Gray
    'start':        "#FF0000",  # Green
    'goal':         "#00FFFF",  # Purple
    'path':         "#4169E1",  # Royal blue
    'frame_theme':  "#D3D3D3",  # Light Gray
    'visited':      "#DFFF00",  # Chartreuse
}

# Background
BGCOL = COLORMAP['theme']

# Window min dimensions
WIDTH = 1366
HEIGHT = 768
framerate = 1000 // 60

# Grid Dimensions
ROWS = 12
COLS = 30
BLOCKSIZE = (WIDTH-50)//COLS


# Main GUI
class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Zlatan's Maze Fiesta")
        self.configure(bg=BGCOL)
        self.resizable(False, False)

        # Bannerimage
        self.banner = ctk.CTkImage(
            dark_image=Image.open("banner1.png"), size=(241, 120))

        # Create top row with banner text and buttons
        self.top_frame = tk.Frame(self, bg=BGCOL)
        self.top_frame.pack(side=tk.TOP, pady=5, anchor='center', expand=True)

        # Add banner text and description text field
        self.banner_text = ctk.CTkLabel(self.top_frame, image=self.banner, text="",
                                        compound=tk.LEFT, fg_color=BGCOL, font=("Roboto", 16), corner_radius=5)
        self.banner_text.pack(side=tk.LEFT, padx=(2, 2),
                              pady=(2, 2), fill='both')

        # Add buttons
        self.save_frame = ctk.CTkFrame(self, fg_color=BGCOL)
        self.save_frame.pack(side=tk.TOP, anchor="center", expand=True)

        self.save_input_field = ctk.CTkEntry(self.save_frame)
        self.save_grid_btn = ctk.CTkButton(self.save_frame, text="SAVE GRID", corner_radius=10,
                                           fg_color=COLORMAP['button'], command=lambda: self.save_grid(self.save_input_field), state="disabled")
        self.quit_btn = ctk.CTkButton(self.save_frame, text="QUIT GAME",
                                      corner_radius=10, fg_color=COLORMAP['button'], command=self.quit_app)

        self.add_walls_btn = ctk.CTkButton(
            self.top_frame, text="ADD WALLS", corner_radius=10, fg_color=COLORMAP['button'], command=self.toggle_draw)
        self.set_start_btn = ctk.CTkButton(
            self.top_frame, text="SET START", corner_radius=10, command=self.toggle_start)
        self.set_goal_btn = ctk.CTkButton(
            self.top_frame, text="SET GOAL", corner_radius=10, command=self.toggle_goal)
        self.reset_grid_btn = ctk.CTkButton(
            self.top_frame, text="RESET GRID", corner_radius=10, command=self.reset_grid)
        self.reset_search_btn = ctk.CTkButton(
            self.top_frame, text="RESET SEARCH", corner_radius=10, command=self.reset_search)

        self.save_input_field.pack(side=ctk.LEFT, padx=10)
        self.save_grid_btn.pack(side=ctk.LEFT, padx=10)
        self.quit_btn.pack(side=ctk.LEFT, padx=10)

        self.add_walls_btn.pack(side=ctk.LEFT, padx=10)
        self.reset_grid_btn.pack(side=ctk.LEFT, padx=10)
        self.set_start_btn.pack(side=ctk.LEFT, padx=10)
        self.set_goal_btn.pack(side=ctk.LEFT, padx=10)
        self.reset_search_btn.pack(side=ctk.LEFT, padx=10)

        # Canvas and grid for maze
        self.canvas = tk.Canvas(
            self, bg=COLORMAP['road'], width=BLOCKSIZE*COLS, height=BLOCKSIZE*ROWS)
        self.canvas.pack(side=ctk.TOP, pady=10, padx=10)

        # infopanel and frame
        self.infoframe = ctk.CTkFrame(self, fg_color=COLORMAP['frame_theme'])
        self.infoframe.pack(side=tk.LEFT, padx=10, pady=(5, 10), fill='both')

        self.infolabel = ctk.CTkLabel(self.infoframe, text="ACTION LOG", fg_color="#14375e", font=(
            "Roboto", 12), width=WIDTH*0.20, height=20, corner_radius=5)
        self.infolabel.pack(side=ctk.TOP, padx=5, pady=5)

        self.info_del = ctk.CTkButton(self.infoframe, width=WIDTH*0.2, height=20,
                                      text="CLEAR LOGS", corner_radius=5, command=self.clear_info)
        self.info_del.pack(side=ctk.TOP, padx=5, pady=5)

        self.infopanel = ctk.CTkTextbox(
            self.infoframe, wrap=ctk.WORD, width=WIDTH*0.20, height=HEIGHT//4, corner_radius=5)
        self.infopanel.insert(0.0, 'App started')
        self.infopanel.configure(state='disabled')
        self.infopanel.pack(side=ctk.LEFT, padx=5, pady=5, fill='both')

        # description and frame
        self.desc_frame = ctk.CTkFrame(self, fg_color=COLORMAP['frame_theme'])
        self.desc_frame.pack(side=tk.LEFT, padx=10, pady=(5, 10), fill='both')

        self.desc_label = ctk.CTkLabel(self.desc_frame, text="README", fg_color="#14375e", font=(
            "Roboto", 12), width=WIDTH*0.5, height=20, corner_radius=5)
        self.desc_label.pack(side=ctk.TOP, padx=5, pady=5, fill='both')

        self.description_text = ctk.CTkTextbox(
            self.desc_frame, wrap=ctk.WORD, width=WIDTH*0.5, height=HEIGHT//4)
        self.description_text.insert("0.0", text.info)
        # make read-only
        self.description_text.configure(state="disabled")
        self.description_text.pack(side=ctk.LEFT, padx=5, pady=5, fill='both')

        # Solvers and frame

        self.solver_frame = ctk.CTkFrame(
            self, fg_color=COLORMAP['frame_theme'])
        self.solver_frame.pack(side=tk.LEFT, padx=10,
                               pady=(5, 10), fill='both')

        self.solver_label = ctk.CTkLabel(self.solver_frame, text="SELECT SOLVER", fg_color="#14375e", font=(
            "Roboto", 12), width=WIDTH*0.20, height=50, corner_radius=5)
        self.solver_label.pack(side=ctk.TOP, padx=5, pady=5)

        self.dfs_btn = ctk.CTkButton(self.solver_frame, width=WIDTH*0.2, height=50,
                                     text="Depth First Search", corner_radius=5, command=self.start_dfs)
        self.bfs_btn = ctk.CTkButton(self.solver_frame, width=WIDTH*0.2, height=50,
                                     text="Breadth First Search", corner_radius=5, command=self.start_bfs)
        self.astar_btn = ctk.CTkButton(self.solver_frame, width=WIDTH*0.2,
                                       height=50, text="A* Search", corner_radius=5, command=self.start_astar)
        self.cancel_search_btn = ctk.CTkButton(
            self.solver_frame, width=WIDTH*0.2, height=50, text="Cancel Search", corner_radius=5, command=self.cancel_search)

        self.dfs_btn.pack(side=ctk.TOP, padx=5, pady=5)
        self.bfs_btn.pack(side=ctk.TOP, padx=5, pady=5)
        self.astar_btn.pack(side=ctk.TOP, padx=5, pady=5)
        self.cancel_search_btn.pack(side=ctk.TOP, padx=5, pady=5)

        self.grid = Grid(self, self.canvas, ROWS, COLS, BLOCKSIZE, COLORMAP)
        self.grid.draw_grid()

        self.disable_during_search = [
            self.add_walls_btn,
            self.set_start_btn,
            self.set_goal_btn,
            self.reset_grid_btn,
            self.reset_search_btn,
            self.dfs_btn,
            self.bfs_btn,
            self.astar_btn,
            self.save_grid_btn]

        # set search running states (for cancels)
        self.search_running = {
            'path': False,
            'dfs': False,
            'bfs': False,
            'astar': False,
        }

        # button press checks
        self.toggle_buttons = {

            'draw_wall': False,
            'reset_grid': False,
            'set_start': False,
            'set_goal': False,
            'reset_search': False,
        }

    # Update window (framerate intervals)

    def update_window(self):
        self.after(framerate, self.update_window)

    # Quit app from button
    def quit_app(self):
        if any(self.search_running):
            self.search_running = {key: False for key in self.search_running}
        searchApp.quit()

    # Set True for activated button and set False to others
    def activate_button(self, button):
        self.toggle_buttons = {key: (key == button)
                               for key in self.toggle_buttons}

    # Cancel search from button

    def cancel_search(self):
        if any(self.search_running.values()):
            self.search_running = {key: False for key in self.search_running}
            self.reset_search()
            self.update_infopanel('Search Interrupted')
        else:
            self.update_infopanel("No searches running")

    # Set button states (lock: disabled, unlock: normal)
    def button_state(self, buttons, state):
        for button in buttons:
            button.configure(state=state)

    # Set mouse binding according to the activated button
    def bind_mouse(self, selection):

        self.canvas.unbind_all("<Button-1>")
        self.canvas.unbind_all("<B1-Motion>")

        binds = {

            'draw_wall': (self.draw_wall, self.remove_wall, True),
            'set_start': (self.set_start, False, False),
            'set_goal': (self.set_goal, False, False),
        }

        if selection == 'reset':
            return

        self.canvas.bind("<Button-1>", binds[selection][0])

        if binds[selection][1]:
            self.canvas.bind("<Button-3>", binds[selection][1])

        if binds[selection][2]:
            self.canvas.bind("<B1-Motion>", binds[selection][0])

    # Clear log-window

    def clear_info(self):

        self.infopanel.configure(state="normal")
        self.infopanel.delete("0.0", "end")
        self.infopanel.insert("end", "Cleared")
        self.infopanel.mark_set(tk.INSERT, tk.END)
        self.infopanel.configure(state="disabled")

    # Update log-window
    def update_infopanel(self, text):

        # unlock field and add log
        self.infopanel.configure(state="normal")
        self.infopanel.insert("end", "\n" + text)
        # autoscroll the textbox into latest line added
        self.infopanel.mark_set(tk.INSERT, tk.END)
        self.infopanel.see(tk.INSERT)
        self.infopanel.configure(state="disabled")

    # Reset all grid nodes
    def reset_grid(self):
        self.activate_button('reset_grid')
        self.bind_mouse('reset')
        self.grid.empty_grid()
        self.update_infopanel(f"Nodes reset to default")

    # Reset search nodes
    def reset_search(self):
        self.activate_button('reset_search')
        self.bind_mouse('reset')
        self.grid.empty_search()
        self.grid.draw_grid()

    # Toggle drawing

    def toggle_draw(self):

        self.activate_button('draw_wall')
        self.bind_mouse('draw_wall')

    # Toggle start node selection
    def toggle_start(self):

        self.activate_button('set_start')
        self.bind_mouse('set_start')

    # Toggle goal node selection
    def toggle_goal(self):

        self.activate_button('set_goal')
        self.bind_mouse('set_goal')

    # Draw walls

    def draw_wall(self, event):

        if self.toggle_buttons['draw_wall']:

            x_pos, y_pos = event.x, event.y
            node = self.grid.get_node_from_coordinates(x_pos, y_pos)

            if node == None:
                self.update_infopanel('Out of bounds')

            elif node.get_node_type() == 'road':

                node.set_node_type('wall')
                self.grid.draw_node(node)
                self.update_infopanel(f"Wall added at {node}")

    # Remove walls

    def remove_wall(self, event):

        if self.toggle_buttons['draw_wall']:

            x_pos, y_pos = event.x, event.y
            node = self.grid.get_node_from_coordinates(x_pos, y_pos)

            if node == None:
                self.update_infopanel('Out of bounds')

            elif node.get_node_type() == 'wall':

                node.set_node_type('road')
                self.grid.draw_node(node)
                self.update_infopanel(f"Wall removed at {node}")

    # Set start node (cant replace walls or goal)

    def set_start(self, event):
        if self.toggle_buttons['set_start']:
            x_pos, y_pos = event.x, event.y
            node = self.grid.get_node_from_coordinates(x_pos, y_pos)
            n_type = node.get_node_type()

            if n_type == 'goal':
                self.update_infopanel('Invalid Node (goal assigned)')

            elif n_type == 'wall':
                self.update_infopanel('Invalid Node (wall assigned)')

            else:
                if self.grid.start is not None:
                    temp = self.grid.start
                    temp.set_node_type('road')
                    self.grid.draw_node(temp)
                    self.grid.start = None

                node.set_node_type('start')
                self.grid.start = node
                self.grid.draw_node(self.grid.start)
                self.update_infopanel(f"Start set at: {node}")

    # Set goal node (cant replace walls or start)

    def set_goal(self, event):
        if self.toggle_buttons['set_goal']:
            x_pos, y_pos = event.x, event.y
            node = self.grid.get_node_from_coordinates(x_pos, y_pos)
            n_type = node.get_node_type()

            if n_type == 'start':
                self.update_infopanel('Invalid Node (start assigned)')

            elif n_type == 'wall':
                self.update_infopanel('Invalid Node (wall assigned)')
            else:
                if self.grid.goal is not None:
                    temp = self.grid.goal
                    temp.set_node_type('road')
                    self.grid.draw_node(temp)
                    self.grid.goal = None

                node.set_node_type('goal')
                self.grid.goal = node
                self.grid.draw_node(self.grid.goal)
                self.update_infopanel(f"Goal set at: {node}")

    # Depth First Search

    def dfs(self, start_node, goal_node):
        self.update_infopanel(f"DFS started")
        stack = [start_node]
        steps = 0
        while stack:

            if self.search_running['dfs']:

                current_node = stack.pop()
                nodetype = current_node.get_node_type()
                if not current_node.visited and not nodetype == 'wall':

                    current_node.visited = True
                    if current_node == goal_node:
                        return (True, steps)

                    current_node.visit_color()
                    if nodetype != "start":
                        self.grid.draw_queue("add", current_node)

                    valid_neighbors = current_node.get_valid_neighbors()
                    for neighbor in valid_neighbors:
                        if neighbor and not neighbor.visited:
                            stack.append(neighbor)
                            neighbor.parent = current_node
                steps += 1
            else:
                self.reset_search()
                return (False, steps)
        return (False, steps)

    # Breadth-First-Search
    def bfs(self, start_node, goal_node):

        self.update_infopanel(f"BFS started")
        steps = 0
        queue = deque()
        queue.append(start_node)
        start_node.visited = True
        while queue:
            if self.search_running['bfs']:
                current_node = queue.popleft()
                valid_neighbors = current_node.get_valid_neighbors()
                for neighbor in valid_neighbors:
                    queue.append(neighbor)
                    neighbor.parent = current_node
                    if neighbor == goal_node:
                        return (True, steps)

                    neighbor.visited = True
                    neighbor.visit_color()
                    self.grid.draw_queue("add", current_node)
                    steps += 1
            else:
                self.reset_search()
                return (False, steps)
        return (False, steps)

    # Calculate and returnr G-Score

    def distance(self, node_a, node_b):

        dx = node_a.col - node_b.col
        dy = node_a.row - node_b.row
        return sqrt(dx*dx + dy*dy)

    # Calculate and return heuristic score
    def manhattan_dist(self, node_a, node_b):
        # Manhattan distance between nodes
        dx = abs(node_a.col - node_b.col)
        dy = abs(node_a.row - node_b.row)
        return dx + dy

    # a* search
    def astar(self, start_node, goal_node):

        # init distances
        steps = 0
        # G - distance from current node to start
        start_node.g = 0
        # H - heuristic, estimation for current node to goal node
        start_node.h = self.manhattan_dist(start_node, goal_node)
        # F - total cost of the node
        start_node.f = start_node.g + start_node.h

        # add start node to set (visited nodes but not expanded)
        open_set = []
        heapq.heappush(open_set, (start_node.f, start_node))

        # closed set (visited and expanded)
        closed_set = set()

        # average cost of the maze for relaxation limit
        total_cost = 0
        total_edges = 0
        # iterate grid and get cost and edges
        self.update_infopanel(f"Calculating relaxation limit")
        for row in self.grid.grid:
            for node in row:
                neighbors = node.get_valid_neighbors()
                for neighbor in neighbors:
                    total_cost += self.distance(node, neighbor)
                    total_edges += 1

        # Calc avg cost
        average_cost = total_cost / total_edges
        self.update_infopanel(f"Relaxation limit set to {average_cost}")
        # Set the relaxation limit
        relaxation_limit = average_cost

        while open_set:

            if self.search_running['astar']:
                self.wait()
                # Get node with lowest F-score
                _, current_node = heapq.heappop(open_set)

                # If goal node, return path
                if current_node == goal_node:
                    return (True, steps)

                # visuals
                current_node.visited = True
                steps += 1
                current_node.visit_color()
                self.grid.draw_queue("add", current_node)

                # add current node to closed set
                closed_set.add(current_node)

                # get valid neighbors and iterate
                valid_neighbors = current_node.get_valid_neighbors()
                for neighbor in valid_neighbors:

                    if neighbor in closed_set:
                        continue

                    # Calculate G-score
                    tentative_g = current_node.g + \
                        self.distance(current_node, neighbor)

                    # add neighbor to open set and calculate new distances with relaxation taken into account
                    if tentative_g <= relaxation_limit or neighbor not in open_set:
                        neighbor.g = tentative_g
                        neighbor.h = self.manhattan_dist(neighbor, goal_node)
                        neighbor.f = neighbor.g + neighbor.h
                        neighbor.parent = current_node

                        if neighbor not in open_set:
                            heapq.heappush(open_set, (neighbor.f, neighbor))

                    elif tentative_g < neighbor.g:
                        # Update g, f scores and update parent
                        neighbor.g = tentative_g
                        neighbor.f = neighbor.g + neighbor.h
                        neighbor.parent = current_node

            else:
                self.reset_search()
                return (False, steps)
        return (False, steps)

    # Backtrack the found path by iterating parent nodes from goal to start

    def reconstruct_path(self, goal_node):
        path = []
        current_node = goal_node

        while current_node.parent is not None:
            path.append(current_node)
            self.grid.draw_queue("add", current_node)
            current_node = current_node.parent
            if current_node != self.grid.start:
                current_node.set_node_type('path')

        path.append(current_node)
        path.reverse()
        return path

    # init DFS
    def start_dfs(self):
        if self.grid.start and self.grid.goal:
            self.search_running['dfs'] = True
            self.button_state(self.disable_during_search, "disabled")
            self.reset_search()
            self.grid.neighbors()

            found_path, steps = self.dfs(self.grid.start, self.grid.goal)
            self.search_running['path'] = True
            self.grid.draw_queue("draw")
            if found_path:
                self.grid.draw_queue("clear")
                path = self.reconstruct_path(self.grid.goal)
                self.grid.draw_queue("draw")
                self.update_infopanel(
                    f"Shortest path (blue) found at {len(path)} steps\nTotal steps taken:{steps}")
            else:
                self.update_infopanel("No path found")

            self.search_running['dfs'] = False
            self.search_running['path'] = False
            self.button_state(self.disable_during_search, "normal")

        else:
            self.update_infopanel("Select start and goal nodes before search")

    # Init BSF

    def start_bfs(self):

        if self.grid.start and self.grid.goal:

            self.search_running['bfs'] = True
            self.button_state(self.disable_during_search, "disabled")
            self.reset_search()
            self.grid.neighbors()

            found_path, steps = self.bfs(self.grid.start, self.grid.goal)
            self.search_running['path'] = True
            self.grid.draw_queue("draw")

            if found_path:
                self.grid.draw_queue("clear")
                path = self.reconstruct_path(self.grid.goal)
                self.grid.draw_queue("draw")
                self.update_infopanel(
                    f"Shortest path (blue) found at {len(path)} steps\nTotal steps taken:{steps}")
            else:
                self.update_infopanel("No path found")

            self.search_running['bfs'] = False
            self.search_running['path'] = False
            self.button_state(self.disable_during_search, "normal")

        else:
            self.update_infopanel("Select start and goal nodes before search")

    # Init
    def start_astar(self):

        if self.grid.start and self.grid.goal:

            self.search_running['astar'] = True
            self.button_state(self.disable_during_search, "disabled")
            self.reset_search()
            self.grid.neighbors()
            self.update_infopanel(f"A* initialized")
            found_path, steps = self.astar(self.grid.start, self.grid.goal)
            self.search_running['path'] = True
            self.update_infopanel(f"a* started")
            self.grid.draw_queue("draw")

            if found_path:

                self.grid.draw_queue("clear")
                path = self.reconstruct_path(self.grid.goal)
                self.grid.draw_queue("draw")
                self.update_infopanel(
                    f"Shortest path (blue) found at {len(path)} steps\nTotal steps taken:{steps}")

            else:

                self.update_infopanel("No path found")

            self.search_running['astar'] = False
            self.search_running['path'] = False
            self.button_state(self.disable_during_search, "normal")

        else:

            self.update_infopanel("Select start and goal nodes before search")

    def wait(self):

        self.after(1)
        self.update()


if __name__ == "__main__":

    searchApp = App()
    searchApp.after(framerate, searchApp.update_window)
    searchApp.mainloop()
