import threading
import random
import queue
import time
import tkinter as tk

# Class representing a player in the game
class Player(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.task = None
        self.position = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        self.is_alive = threading.Event()
        self.is_alive.set()
        self.move_time = 1.0/speed
        self.votes = 0

    def run(self):
        while self.is_alive.is_set() and not game_over.is_set():
            # Players receive their tasks and complete them
            # Acquiring semaphore to limit the number of players accessing tasks simultaneously
            with task_semaphore:
                with task_queue_lock: # Entering critical section to safely access the task queue
                        if not task_queue.empty():
                            self.task = task_queue.get()
                            self.task.is_occupied = True
                if self.task:
                    print(f"{self.name} is moving to task location: {self.task.location}")
                    self.move_to(self.task.location)
                    print(f"{self.name} is performing task: {self.task.name}")
                    time.sleep(self.task.time_to_perform)  # Time to perform the task
                    with task_queue_lock: # Re-entering critical section to mark the task as done
                            print(f"{self.name} has completed task: {self.task.name}")
                            task_queue.task_done()

    # Method for moving the player to the target location
    def move_to(self, target):
        while self.position != target:
            x, y = self.position
            tx, ty = target
            if x < tx:
                x += 1
            elif x > tx:
                x -= 1
            if y < ty:
                y += 1
            elif y > ty:
                y -= 1
            self.position = (x, y)
            time.sleep(self.move_time)  # Time to move

    # Method for players to vote for a suspect
    def vote_for_suspect(self):
        global players
        with players_lock: # Entering critical section to safely access the players list
            all_players = players.copy()
            all_players.append(impostor)
            suspect = random.choice(all_players)
            while suspect == self:
                suspect = random.choice(all_players)
            suspect.vote()

    # Method for incrementing votes for a player
    def vote(self):
        self.votes += 1

# Class representing the impostor in the game
class Impostor(Player):
    def __init__(self, name):
        super().__init__(name)
        self.move_time = 0.5/speed
    
    def run(self):
        while not game_over.is_set() and len(players)>0:
            # Impostor has a chance to kill another player or sabotage a task
            if not sabotage_task_queue.empty():
                action = random.choice(["kill", "sabotage"])
                if action == "kill":
                    self.kill()
                else:
                    self.sabotage()
    
    # Method for the impostor to kill a player 
    def kill(self):
        with players_lock: # Entering critical section to safely access and modify the players list
            if players:
                target = random.choice(players)
                print(f"{self.name} is moving to kill {target.name} at location: {target.position}")
                self.move_to(target.position)
                print(f"{self.name} is killing {target.name} at location: {target.position}")
                players.remove(target)
                print(f"{target.name} has been killed!")
                target.is_alive.clear()

    # Method for the impostor to sabotage a task
    def sabotage(self):
        with sabotage_task_queue_lock: # Entering critical section to safely access the sabotage task queue
            self.task = sabotage_task_queue.get()
        print(f"{self.name} is moving to task location: {self.task.location}")
        self.move_to(self.task.location)
        with task_queue_lock: # Re-entering critical section to add the sabotaged task back to the task queue
            print(f"{self.name} has sabotaged task: {self.task.name}")
            task_queue.put(self.task)

# Class representing a task in the game
class Task():
    def __init__(self, name):
        self.name = name
        self.is_occupied = False
        self.is_done = False
        self.time_to_perform = random.randint(1, 5)/speed
        self.location = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))

# Function to check end conditions of the game
def end():
    global game_over
    while True:
        #with task_queue_lock:
        if not players or task_queue.empty() or impostor_is_eliminated.is_set():
            game_over.set()

            for player in players:
                player.is_alive.clear()
        
            impostor.is_alive.clear()  

            for player in players:
                player.join()   

            impostor.join()
            #root.destroy()

            break
        time.sleep(1/speed)

# Function to handle the voting phase
def voting_phase(players, impostor, impostor_is_eliminated):
    time.sleep(5/speed)
    while not game_over.is_set():
        print("Time for voting...")
        with condition:  # Condition variable to wait for all players to be ready
            condition.wait_for(lambda: all(player.is_alive.is_set() for player in players) or impostor.is_alive.is_set())
            for player in players:
                if player.is_alive.is_set():
                    player.vote_for_suspect()
            impostor.vote_for_suspect()

        eliminate_player(players, impostor, impostor_is_eliminated)
        time.sleep(20/speed)

# Function to eliminate a player based on votes
def eliminate_player(players, impostor, impostor_is_eliminated):
    with players_lock: # Entering critical section to safely access and modify the players list
        all_players = players.copy()
        all_players.append(impostor)
        max_votes_player = max(all_players, key=lambda x: x.votes)  
        print(f"{max_votes_player.name} is eliminated!")
        if (max_votes_player == impostor):
            impostor_is_eliminated.set()
        else:
            max_votes_player.is_alive.clear()

# Function to draw the game map on the canvas
def draw_map(canvas, players, impostor, tasks):
    canvas.delete("all")
    cell_size = 20
    for task in tasks:
        if not task.is_done: 
            x, y = task.location
            canvas.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="yellow", outline="black")
    
    for player in players:
        if player.is_alive.is_set():
            x, y = player.position
            canvas.create_oval(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="blue", outline="black")
    
    if impostor.is_alive.is_set():
        x, y = impostor.position
        canvas.create_oval(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="red", outline="black")

# Function to continuously update the game map
def display_map_loop(canvas, players, impostor, tasks):
    if not game_over.is_set():
        draw_map(canvas, players, impostor, tasks)
        canvas.after(int(1000/speed), display_map_loop, canvas, players, impostor, tasks)

# Main function to initialize and start the game
def main():
    #global variables
    global map_size
    global task_queue
    global sabotage_task_queue
    global players
    global game_over
    global impostor
    global impostor_is_eliminated
    
    global speed
    speed = 5

    # critical section
    global task_queue_lock
    global sabotage_task_queue_lock
    global players_lock
    global task_semaphore
    global condition

    players_lock = threading.RLock()
    task_queue_lock = threading.Lock()
    sabotage_task_queue_lock = threading.Lock()
    task_semaphore = threading.Semaphore(3)
    condition = threading.Condition()

    map_size = (20, 20)

    # Creating tasks list
    tasks = [Task("Repair wiring"), Task("Empty garbage"), Task("Fix lights"), Task("Download data")]
    task_queue = queue.Queue(maxsize=20)
    for task in tasks:
        task_queue.put(task)

    # Creating sabotage tasks list
    sabotage_tasks = [Task("XXXX"), Task("YYYY"), Task("ZZZ")]
    sabotage_task_queue = queue.Queue(maxsize=10)
    for task in sabotage_tasks:
        sabotage_task_queue.put(task)

    # Creating game over flag
    game_over = threading.Event()
    game_over.clear()  # Setting the flag to False

    # Creating players and impostor
    players = []
    number_of_players = 5

    for i in range(number_of_players-1):
        name = f"Player-{i+1}" 
        player = Player(name)
        players.append(player)
    
    impostor = Impostor("Impostorrr")
    impostor_is_eliminated = threading.Event()
    voting = threading.Thread(target=voting_phase, args=(players, impostor, impostor_is_eliminated))

    # Control the end of game
    game_over_thread = threading.Thread(target=end)
    game_over_thread.start()

    voting.start()

    # Starting player and impostor threads
    for player in players:
        player.start()
    impostor.start()

    root = tk.Tk()
    root.title("Game Map")
    canvas = tk.Canvas(root, width=map_size[0]*20, height=map_size[1]*20, bg="white")
    canvas.pack()

    canvas.after(int(1000/speed), display_map_loop, canvas, players, impostor, tasks)
        
    root.mainloop()

    game_over_thread.join()
    voting.join()
    if(task_queue.empty()):
        print("Players WON!")
    else:
        print("Impostor WON!")

if __name__ == "__main__":
    main()
