import threading
import random
import queue
import time
import pygame

# Define rooms and walls
def generate_rooms_and_walls():
    # Define the layout of rooms and their doors
    rooms = [
        {"x": 0, "y": 0, "width": 10, "height": 15, "doors": [(5, 0), (5, 15), (0, 7), (10, 7)]},
        {"x": 15, "y": 0, "width": 20, "height": 10, "doors": [(25, 0), (25, 10), (15, 5), (35, 5)]},
        {"x": 0, "y": 20, "width": 15, "height": 15, "doors": [(7, 20), (7, 35), (0, 27), (15, 27)]},
        {"x": 30, "y": 15, "width": 15, "height": 15, "doors": [(37, 15), (37, 30), (30, 22), (45, 22)]},
        {"x": 20, "y": 30, "width": 20, "height": 20, "doors": [(30, 30), (30, 50), (20, 40), (40, 40)]},
    ]

    # Create walls based on room dimensions and door locations
    for room in rooms:
        for x in range(room["width"]):
            obstacles.add((room["x"] + x, room["y"]))
            obstacles.add((room["x"] + x, room["y"] + room["height"] - 1))
        for y in range(room["height"]):
            obstacles.add((room["x"], room["y"] + y))
            obstacles.add((room["x"] + room["width"] - 1, room["y"] + y))
        for door in room["doors"]:
            if door in obstacles:
                obstacles.remove(door)

# Class representing a player in the game
class Player(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.task = None
        self.position = self.generate_random_position(obstacles)
        self.is_alive = threading.Event()
        self.is_alive.set()
        self.move_time = 1.0 / speed
        self.votes = 0
    
    # Generate a random start position for the player
    def generate_random_position(self, obstacles):
        position = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        while position in obstacles:
            position = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        return position

    # Method representing the player's actions during the game
    def run(self):
        # Perform tasks while alive and the game is not over
        while self.is_alive.is_set() and not game_over.is_set():
            with task_semaphore:                
                with task_queue_lock:       
                    
                    # Get a task from the task queue if available
                    if not task_queue.empty():
                        self.task = task_queue.get()
                        self.task.increment_players()
                
                if self.task:
                    # Move to the task location and perform it
                    print(f"{self.name} is moving to task location: {self.task.location}")
                    self.move_to(self.task.location)
                    print(f"{self.name} is performing task: {self.task.name}")
                    
                    # Wait for other players to join the task (if necessary)
                    while self.task.current_players < self.task.required_players and self.is_alive.is_set():
                        time.sleep(0.1) 

                    time.sleep(self.task.time_to_perform)   # Wait for the task to complete
                    
                    with task_queue_lock:
                        self.task.decrement_players()
                        # Mark the task as done if all players completed it
                        if self.task.current_players == 0 and self.task.required_players <= self.task.players_done:
                            self.task.is_done = True
                            print(f"{self.name} has completed task: {self.task.name}")
                            task_queue.task_done()
                        else:
                            task_queue.put(self.task)

    # Method for moving the player to the target location
    def move_to(self, target):
        path = self.find_path(self.position, target)
        for step in path:
            self.position = step
            time.sleep(self.move_time)

    # Method for finding the path from the start to the goal using A* algorithm
    def find_path(self, start, goal):
        from queue import PriorityQueue

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: heuristic(start, goal)}
        oheap = PriorityQueue()
        oheap.put((fscore[start], start))

        while not oheap.empty():
            current = oheap.get()[1]

            if current == goal:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data[::-1]

            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = gscore[current] + 1
                if 0 <= neighbor[0] < map_size[0]:
                    if 0 <= neighbor[1] < map_size[1]:
                        if neighbor in obstacles:
                            continue
                    else:
                        continue
                else:
                    continue

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap.queue]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    oheap.put((fscore[neighbor], neighbor))

        return []

    # Method for players to vote for a suspect
    def vote_for_suspect(self):
        global players
        with players_lock:
            alive_players = [p for p in players if p.is_alive.is_set()]
            alive_players.append(impostor)
            suspect = random.choice(alive_players)
            while suspect == self:
                suspect = random.choice(alive_players)
            suspect.vote()

    # Method for incrementing votes for a player
    def vote(self):
        with players_lock:
            self.votes += 1

# Class representing the impostor in the game
class Impostor(Player):
    def __init__(self, name):
        super().__init__(name)
        self.move_time = 0.5 / speed
        self.killed_last_turn = False

    # Method representing the actions of the impostor during the game
    def run(self):
        # Perform actions while the game is not over and there are still players
        while not game_over.is_set() and len(players) > 0:
            if not sabotage_task_queue.empty():                 # Check if there are any sabotage tasks in the queue
                action = random.choice(["kill", "sabotage"])    # Randomly choose between killing a player or sabotaging a task
                if action == "kill":
                    self.kill()                                 # Execute kill action
                else:
                    self.sabotage()                             # Execute sabotage action

    # Method for the impostor to kill a player
    def kill(self):
        with players_lock:
            # Get a list of alive players
            alive_players = [p for p in players if p.is_alive.is_set()]
            if alive_players:
                # Randomly choose a target player
                target = random.choice(alive_players)
                print(f"{self.name} is moving to kill {target.name} at location: {target.position}")
                self.move_to(target.position)                   # Move to the target player's position
                print(f"{self.name} is killing {target.name} at location: {target.position}")
                players.remove(target)                          # Remove the killed player from the game
                print(f"{target.name} has been killed!")
                target.is_alive.clear()                         # Set the target player as not alive
                self.killed_last_turn = True                    # Set the flag to indicate that a kill occurred

    # Method for the impostor to sabotage a task
    def sabotage(self):
        with sabotage_task_queue_lock:
            self.task = sabotage_task_queue.get()               # Get a task from the sabotage task queue
        print(f"{self.name} is moving to task location: {self.task.location}")
        self.move_to(self.task.location)                        # Move to the location of the task to sabotage
        with task_queue_lock:
            print(f"{self.name} has sabotaged task: {self.task.name}")
            task_queue.put(self.task)                           # Add the sabotaged task to the main task queue

    # Method to move the impostor to a target location
    def move_to(self, target):
        self.check_for_other_players()                          # Check for other players nearby
        path = self.find_path(self.position, target)            # Find the path to the target location
        for step in path:
            self.position = step                                # Move to the next step in the path
            time.sleep(self.move_time)                          # Wait for the move time

    # Method to check for other players nearby and adjust impostor's speed accordingly
    def check_for_other_players(self):
        with players_lock:
            nearby_players = [p for p in players if self.distance(self.position, p.position) <= 2]
            if nearby_players:
                self.move_time = 1.0 / speed  # Impostor moves with normal player speed
            else:
                self.move_time = 0.5 / speed  # Impostor moves with impostor speed

    # Method to calculate the distance between two points
    def distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
# Class representing a task in the game
class Task():
    def __init__(self, name, required_players=1):
        self.name = name
        self.is_occupied = False
        self.is_done = False
        self.time_to_perform = random.randint(1, 5) / speed
        self.location = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        while self.location in obstacles:
            self.location = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        self.current_players = 0
        self.required_players = required_players
        self.players_done = 0
        self.lock = threading.Lock()

    def increment_players(self):
        with self.lock:
            self.current_players += 1

    def decrement_players(self):
        with self.lock:
            self.current_players -= 1
            self.players_done += 1

# Function to check end conditions of the game
def end():
    global game_over
    while True:
        # Check if any of the end conditions are met: no players left, task queue empty, or impostor eliminated
        if not players or task_queue.empty() or impostor_is_eliminated.is_set():
            game_over.set()                                     # Set the game over event
            for player in players:
                player.is_alive.clear()
            impostor.is_alive.clear()

            # Wait for all player and impostor threads to join
            for player in players:
                player.join()
            impostor.join()

            # Determine the winner of the game and print the result
            if impostor_is_eliminated.is_set():
                print("Game Over! Players win!")
            else:
                print("Game Over! Impostor wins!")
            break
        time.sleep(1 / speed)

# Function to handle the voting phase
def voting_phase(players, impostor, impostor_is_eliminated, impostor_is_eliminated_lock):
    time.sleep(5 / speed)
    while not game_over.is_set():
        print("Time for voting...")

        with condition:
            # Wait for all players before starting the voting
            condition.wait_for(lambda: all(player.is_alive.is_set() for player in players) or impostor.is_alive.is_set())
            # Allow each player to vote for a suspect
            for player in players:
                if player.is_alive.is_set():
                    player.vote_for_suspect()
            impostor.vote_for_suspect()

        # Eliminate player based on votes
        eliminate_player(players, impostor, impostor_is_eliminated, impostor_is_eliminated_lock)
        
        time.sleep(20 / speed)

# Function to eliminate a player based on votes
def eliminate_player(players, impostor, impostor_is_eliminated, impostor_is_eliminated_lock):
    global game_over
    with players_lock:
        # Get a list of alive players and the impostor
        alive_players = [p for p in players if p.is_alive.is_set()]
        alive_players.append(impostor)

        # Find the player with the maximum number of votes
        max_votes_player = max(alive_players, key=lambda x: x.votes)
        print(f"{max_votes_player.name} is eliminated!")

        # Check if the impostor is eliminated
        if max_votes_player == impostor:
            with impostor_is_eliminated_lock:
                impostor_is_eliminated.set()
                game_over.set()                         # Set game over when the impostor is eliminated
        else:
            max_votes_player.is_alive.clear()
            if not any(player.is_alive.is_set() for player in players):
                game_over.set()                         # Set game over when all players are eliminated

# Function to draw the game map on the canvas
def draw_map(screen, players, impostor, tasks):
    cell_size = 20                                      # Size of each cell on the map
    screen.fill((0, 0, 0))                              # Fill the screen with black color
    
    # Draw obstacles on the map
    for obstacle in obstacles:
        x, y = obstacle
        pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Draw tasks on the map
    for task in tasks:
        if not task.is_done:
            x, y = task.location
            pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Draw players on the map
    for player in players:
        if player.is_alive.is_set():
            x, y = player.position
            pygame.draw.ellipse(screen, (0, 0, 255), pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Draw impostor on the map
    if impostor.is_alive.is_set():
        x, y = impostor.position
        pygame.draw.ellipse(screen, (255, 0, 0), pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Update the display
    pygame.display.flip() 

# Function to continuously update the game map
def display_map_loop(screen, players, impostor, tasks):
    while not game_over.is_set():
        draw_map(screen, players, impostor, tasks)
        time.sleep(0.1)

def main():
    # Define global variables
    global map_size
    global task_queue
    global sabotage_task_queue
    global players
    global game_over
    global impostor
    global impostor_is_eliminated
    global impostor_is_eliminated_lock
    global speed
    global obstacles
    global tasks

    # Set the game speed
    speed = 5

    # Initialize locks and synchronization primitives
    global task_queue_lock
    global sabotage_task_queue_lock
    global players_lock
    global task_semaphore
    global condition

    task_queue_lock = threading.Lock()
    sabotage_task_queue_lock = threading.Lock()
    players_lock = threading.RLock()
    task_semaphore = threading.Semaphore(3)
    condition = threading.Condition()

    # Set map size and generate obstacles
    map_size = (50, 50)
    obstacles = set()  
    generate_rooms_and_walls()

    # Define tasks and queues
    tasks = [
        Task("Repair wiring", required_players=2),
        Task("Empty garbage", required_players=1),
        Task("Fix lights", required_players=3),
        Task("Download data", required_players=1)
    ]
    task_queue = queue.Queue(maxsize=20)
    for task in tasks:
        task_queue.put(task)

    sabotage_tasks = [Task("XXXX", required_players=1), Task("YYYY", required_players=1), Task("ZZZ", required_players=1)]
    sabotage_task_queue = queue.Queue(maxsize=20)
    for task in sabotage_tasks:
        sabotage_task_queue.put(task)

    # Initialize players and impostor
    players = [Player(f"Player {i}") for i in range(10)]
    impostor = Impostor("Impostor")

    # Initialize game-related events and locks
    game_over = threading.Event()
    impostor_is_eliminated = threading.Event()
    impostor_is_eliminated_lock = threading.Lock()

    # Start player and impostor threads
    for player in players:
        player.start()
    impostor.start()

    # Start threads for game phases
    end_thread = threading.Thread(target=end)
    end_thread.start()

    voting_thread = threading.Thread(target=voting_phase, args=(players, impostor, impostor_is_eliminated, impostor_is_eliminated_lock))
    voting_thread.start()

    # Initialize Pygame and screen
    pygame.init()
    screen = pygame.display.set_mode((map_size[0] * 20, map_size[1] * 20))
    pygame.display.set_caption("Among Us Simulation")

    display_thread = threading.Thread(target=display_map_loop, args=(screen, players, impostor, tasks))
    display_thread.start()

    running = True
    while running and not game_over.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False     

    # Join threads and quit Pygame
    voting_thread.join()
    pygame.quit()
    display_thread.join()
    end_thread.join()

if __name__ == "__main__":
    main()
