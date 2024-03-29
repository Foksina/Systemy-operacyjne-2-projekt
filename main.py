import threading
import random
import time

class Player(threading.Thread):
    def __init__(self, name, tasks, task_queue, discussions, voting):
        super(Player, self).__init__()
        self.name = name
        self.tasks = tasks
        self.task_queue = task_queue
        self.discussions = discussions
        self.voting = voting
        self.is_imposter = False

    def run(self):
        while True:
            if not self.is_imposter:
                # Player performs a random task
                task = self.task_queue.get()
                print(f"{self.name} is performing task: {task}")
                time.sleep(random.randint(1, 5))  # Time to perform the task
                print(f"{self.name} has completed task: {task}")
                self.task_queue.task_done()
                time.sleep(1)  # Time to "rest"
            else:
                # Imposter sabotages a random task
                sabotaged_task = random.choice(self.tasks)
                print(f"{self.name} is sabotaging task: {sabotaged_task}")
                time.sleep(random.randint(1, 5))  # Time to sabotage
                print(f"{self.name} has sabotaged task: {sabotaged_task}")
                time.sleep(1)  # Time to "rest"

            # Player participates in discussions and voting
            if not self.is_imposter:
                self.discuss()
                self.vote()

    def discuss(self):
        print(f"{self.name} is discussing...")
        time.sleep(random.randint(1, 3))  # Time for discussion

    def vote(self):
        suspect = random.choice(self.discussions)
        print(f"{self.name} is voting for {suspect}")
        self.voting.append(suspect)

class Imposter(Player):
    def __init__(self, name, tasks, task_queue, discussions, voting):
        super(Imposter, self).__init__(name, tasks, task_queue, discussions, voting)
        self.is_imposter = True

    def run(self):
        while True:
            # Imposter sabotages a random task
            sabotaged_task = random.choice(self.tasks)
            print(f"{self.name} is sabotaging task: {sabotaged_task}")
            time.sleep(random.randint(1, 5))  # Time to sabotage
            print(f"{self.name} has sabotaged task: {sabotaged_task}")
            time.sleep(1)  # Time to "rest"

            # Imposter participates in discussions and voting
            self.discuss()
            self.vote()

def main():
    tasks = ["Repair wiring", "Empty garbage", "Fix lights", "Download data"]
    task_queue = threading.Queue(maxsize=10)  # Queue for tasks
    for task in tasks:
        task_queue.put(task)

    discussions = ["Player-1", "Player-2", "Player-3", "Player-4", "Player-5", "Player-6"]
    voting = []

    players = []

    # Creating players
    for i in range(6):
        name = f"Player-{i+1}"
        if i == 0:  # The first player becomes an imposter
            player = Imposter(name, tasks, task_queue, discussions, voting)
        else:
            player = Player(name, tasks, task_queue, discussions, voting)
        players.append(player)

    # Starting player threads
    for player in players:
        player.start()

    # Waiting for all tasks to be completed
    task_queue.join()

    # Voting results
    print("\nVoting Results:")
    for player in players:
        print(f"{player.name}: {voting.count(player.name)} votes")

if __name__ == "__main__":
    main()
