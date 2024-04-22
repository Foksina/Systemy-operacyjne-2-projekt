import threading
import random
import queue
import time

class Player(threading.Thread):
    def __init__(self, name, game_over_flag):
        threading.Thread.__init__(self)
        self.name = name
        self.task = None
        self.position = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        self.is_alive = True
        self.move_time = 1
        self.game_over_flag = game_over_flag

    def run(self):
        while self.is_alive and not self.game_over_flag.is_set():
            # Players receive their tasks and complete them
            while not task_queue.empty():
                self.task = task_queue.get()
                self.task.is_occupied = True
                print(f"{self.name} is moving to task location: {self.task.location}")
                self.move_to(self.task.location)
                print(f"{self.name} is performing task: {self.task.name}")
                time.sleep(self.task.time_to_perform)  # Time to perform the task
                print(f"{self.name} has completed task: {self.task.name}")
                task_queue.task_done()
    
    def stop(self):
        self.is_alive = False
    
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

class Impostor(Player):
    def __init__(self, name, game_over_flag):
        super().__init__(name, game_over_flag)
        self.move_time = 0.5
    
    def run(self):
        while not self.game_over_flag.is_set():
            # Impostor has a chance to kill another player or sabotage a task
            if not sabotage_task_queue.empty():
                action = random.choice(["kill", "sabotage"])
                if action == "kill":
                    self.kill()
                else:
                    self.sabotage()
            else:
                self.kill()
        
    def kill(self):
        target = random.choice([player for player in players])
        print(f"{self.name} is moving to kill {target.name} at location: {target.position}")
        self.move_to(target.position)
        print(f"{self.name} is killing {target.name} at location: {target.position}")
        players.remove(target)
        print(f"{target.name} has been killed!")
        target.stop()
        target.join()

    def sabotage(self):
        self.task = sabotage_task_queue.get()
        print(f"{self.name} is moving to task location: {self.task.location}")
        self.move_to(self.task.location)
        print(f"{self.name} has sabotaged task: {self.task.name}")
        task_queue.put(self.task)

class Task():
    def __init__(self, name):
        self.name = name
        self.is_occupied = False
        self.is_done = False
        self.time_to_perform = random.randint(1, 5)
        self.location = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))

def end(task_queue, players, game_over):
    while True:
        if not players or task_queue.empty():
            game_over.set()
            break
        time.sleep(1)


def main():
    #global variables
    global map_size
    global task_queue
    global sabotage_task_queue
    global players
    global game_over

    map_size = (50, 50)

    # Creating tasks list
    tasks = [Task("Repair wiring"), Task("Empty garbage"), Task("Fix lights"), Task("Download data"), Task("Repair wiring 2"), Task("Empty garbage 2"), Task("Fix lights 2"), Task("Download data 2"), Task("Repair wiring 3"), Task("Empty garbage 3"), Task("Fix lights 3"), Task("Download data 3")]
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
        player = Player(name, game_over)
        players.append(player)
    
    impostor = Impostor("Impostorrr", game_over)

    # Control the end of game
    game_over_thread = threading.Thread(target=end, args=(task_queue, players, game_over))
    game_over_thread.start()

    # Starting player and impostor threads
    for player in players:
        player.start()
    impostor.start()

    game_over_thread.join()

    for player in players:
        player.join()
    impostor.join()

    if(task_queue.empty()):
        print("Players WON!")
    else:
        print("Impostor WON!")

if __name__ == "__main__":
    main()