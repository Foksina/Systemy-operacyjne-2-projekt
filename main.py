import threading
import random
import time
import queue
import math

class Player(threading.Thread):
    def __init__(self, name, task_queue, players, map_size):
        super(Player, self).__init__()
        self.name = name
        self.task_queue = task_queue
        self.players = players
        self.map_size = map_size
        self.position = (random.randint(0, map_size[0] - 1), random.randint(0, map_size[1] - 1))
        self.is_impostor = False
        self.is_alive = True
    
    def run(self):
        if not self.is_impostor:
            while (not self.task_queue.empty()):
                task = self.task_queue.get()
                print(f"{self.name} is moving to task location: {task['location']}")
                self.move_to(task['location'])
                print(f"{self.name} is performing task: {task['name']}")
                time.sleep(random.randint(1, 5))  # Time to perform the task
                print(f"{self.name} has completed task: {task['name']}")
                self.task_queue.task_done()
                time.sleep(1)  # Time to "rest"
            print(f"{self.name} has completed all tasks and is waiting for voting...")
        else:
            while (not self.task_queue.empty()):
                # Impostor has a chance to kill another player or sabotage a task
                action = random.choice(["kill", "sabotage"])
                if action == "kill":
                    self.kill()
                else:
                    self.sabotage()

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
            time.sleep(1)  # Time to move

    def kill(self):
        target = random.choice([player for player in self.players if player != self])
        print(f"{self.name} is moving to kill {target.name} at location: {target.position}")
        self.move_to(target.position)
        print(f"{self.name} is killing {target.name} at location: {target.position}")
        time.sleep(1)
        self.players.remove(target)
        target.is_alive = False
        print(f"{target.name} has been killed!")

    def sabotage(self):
        sabotaged_task = self.task_queue.get()
        print(f"{self.name} is moving to task location: {sabotaged_task['location']}")
        self.move_to(sabotaged_task['location'])
        print(f"{self.name} is sabotaging task: {sabotaged_task}")
        time.sleep(random.randint(1, 5))  # Time to sabotage
        print(f"{self.name} has sabotaged task: {sabotaged_task}")

        # Find second nearest player to the sabotaged task
        nearest_player = self.find_nearest_player(sabotaged_task['location'])
        print(f"{nearest_player.name} is nearest to the sabotaged task.")
        nearest_player.repair_task(sabotaged_task['location'])

    def find_nearest_player(self, target_location):
        min_distance = float('inf')
        nearest_player = None
        second_min_distance = float('inf')
        second_nearest_player = None
        for player in self.players:
            distance = math.sqrt((player.position[0] - target_location[0]) ** 2 + (player.position[1] - target_location[1]) ** 2)
            if distance < min_distance:
                second_min_distance = min_distance
                min_distance = distance
                second_nearest_player = nearest_player
                nearest_player = player
            elif distance < second_min_distance:
                second_min_distance = distance
                second_nearest_player = player
        return second_nearest_player

    def repair_task(self, task_location):
        print(f"{self.name} is moving to repair task at location: {task_location}")
        self.move_to(task_location)
        print(f"{self.name} is repairing task at location: {task_location}")
        time.sleep(random.randint(1, 5))  # Time to repair the task
        print(f"{self.name} has repaired the task at location: {task_location}")


def main():
    map_size = (20, 20)
    tasks = [{"name": "Repair wiring", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))},
             {"name": "Empty garbage", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))},
             {"name": "Fix lights", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))},
             {"name": "Download data", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))}]
    task_queue = queue.Queue(maxsize=10)  # Queue for tasks
    for task in tasks:
        task_queue.put(task)
    
    sabotage_tasks = [{"name": "xxxx", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))},
             {"name": "yyyy", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))},
             {"name": "zzz", "location": (random.randint(0, map_size[0]), random.randint(0, map_size[1]))},]
    sabotage_task_queue = queue.Queue(maxsize=10)
    for task in sabotage_tasks:
        sabotage_task_queue.put(task)

    players = []
    number_of_players = 5

    # Impostor
    impostor_index = random.randint(0, number_of_players - 1)

    # Creating players
    for i in range(number_of_players):
        name = f"Player-{i+1}" 
        if i != impostor_index: 
            player = Player(name, task_queue, players, map_size)
        else:
            player = Player(name, sabotage_task_queue, players, map_size)
            player.is_impostor = True
        players.append(player)
    
    # Starting player threads
    for player in players:
        player.start()

    # Waiting for all tasks to be completed
    task_queue.join()
    
if __name__ == "__main__":
    main()