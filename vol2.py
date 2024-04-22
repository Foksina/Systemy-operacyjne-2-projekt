import threading
import random
import queue
import time

class Player(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.task = None
        self.position = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        self.is_alive = threading.Event()
        self.is_alive.set()
        self.move_time = 1
        self.votes = 0

    def run(self):
        while self.is_alive.is_set() and not game_over.is_set() and not task_queue.empty():
            # Players receive their tasks and complete them
            if self in players:
                self.task = task_queue.get()
                self.task.is_occupied = True
                print(f"{self.name} is moving to task location: {self.task.location}")
                self.move_to(self.task.location)
                print(f"{self.name} is performing task: {self.task.name}")
                time.sleep(self.task.time_to_perform)  # Time to perform the task
                print(f"{self.name} has completed task: {self.task.name}")
                task_queue.task_done()
    
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

    def vote_for_suspect(self):
        global players
        all_players = players.copy()
        all_players.append(impostor)
        suspect = random.choice(all_players)
        while suspect == self:
            suspect = random.choice(all_players)
        suspect.vote()

    def vote(self):
        self.votes += 1

class Impostor(Player):
    def __init__(self, name):
        super().__init__(name)
        self.move_time = 0.5
    
    def run(self):
        while not game_over.is_set() and len(players)>0:
            # Impostor has a chance to kill another player or sabotage a task
            while not sabotage_task_queue.empty():
                action = random.choice(["kill", "sabotage"])
                if action == "kill":
                    self.kill()
                else:
                    self.sabotage()
        
    def kill(self):
        target = random.choice([player for player in players])
        print(f"{self.name} is moving to kill {target.name} at location: {target.position}")
        self.move_to(target.position)
        print(f"{self.name} is killing {target.name} at location: {target.position}")
        players.remove(target)
        print(f"{target.name} has been killed!")
        target.is_alive.clear()

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

def end(task_queue, players, impostor, impostor_is_eliminated):
    global game_over
    while True:
        if not players or task_queue.empty() or impostor_is_eliminated.is_set():
            game_over.set()

            for player in players:
                player.is_alive.clear()
        
            impostor.is_alive.clear()  

            for player in players:
                player.join()   

            impostor.join()

            break
        time.sleep(1)

def voting_phase(players, impostor, impostor_is_eliminated):
    time.sleep(5)
    while not game_over.is_set():
        print("Time for voting...")
        for player in players:
            if player.is_alive.is_set():
                player.vote_for_suspect()
        impostor.vote_for_suspect()

        eliminate_player(players, impostor, impostor_is_eliminated)

        time.sleep(7)

def eliminate_player(players, impostor, impostor_is_eliminated):
    all_players = players.copy()
    all_players.append(impostor)
    max_votes_player = max(all_players, key=lambda x: x.votes)  
    print(f"{max_votes_player.name} is eliminated!")
    if (max_votes_player == impostor):
        impostor_is_eliminated.set()
    else:
        max_votes_player.is_alive.clear()

def main():
    #global variables
    global map_size
    global task_queue
    global sabotage_task_queue
    global players
    global game_over
    global impostor
    global impostor_is_eliminated

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
        player = Player(name)
        players.append(player)
    
    impostor = Impostor("Impostorrr")
    impostor_is_eliminated = threading.Event()
    voting = threading.Thread(target=voting_phase, args=(players, impostor, impostor_is_eliminated))

    # Control the end of game
    game_over_thread = threading.Thread(target=end, args=(task_queue, players, impostor, impostor_is_eliminated))
    game_over_thread.start()

    voting.start()

    # Starting player and impostor threads
    for player in players:
        player.start()
    impostor.start()

    game_over_thread.join()
    voting.join()
    if(task_queue.empty()):
        print("Players WON!")
    else:
        print("Impostor WON!")


if __name__ == "__main__":
    main()
