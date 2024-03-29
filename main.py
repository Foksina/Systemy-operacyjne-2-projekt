import threading
import random
import time
import queue

class Player(threading.Thread):
    def __init__(self, name, tasks, task_queue, discussions, voting, tasks_completed, players):
        super(Player, self).__init__()
        self.name = name
        self.tasks = tasks
        self.task_queue = task_queue
        self.discussions = discussions
        self.voting = voting
        self.tasks_completed = tasks_completed
        self.players = players
        self.is_imposter = False

    def run(self):
        while not self.task_queue.empty():
            if not self.is_imposter:
                task = self.task_queue.get()
                print(f"{self.name} is performing task: {task}")
                time.sleep(random.randint(1, 5))  # Time to perform the task
                print(f"{self.name} has completed task: {task}")
                self.task_queue.task_done()
                self.tasks_completed[0] += 1
                time.sleep(1)  # Time to "rest"
            else:
                # Imposter has a chance to kill another player
                self.kill()

                # Player participates in discussions and voting
                self.discuss()
                self.vote()

        print(f"{self.name} has completed all tasks and is waiting for voting...")

    def kill(self):
        target = random.choice(self.players)
        if target != self:
            print(f"{self.name} is killing {target.name}")
            time.sleep(1)
            self.players.remove(target)
            print(f"{target.name} has been killed!")

    def discuss(self):
        print(f"{self.name} is discussing...")
        time.sleep(random.randint(1, 3))  # Time for discussion

    def vote(self):
        # Randomly decide whether to skip voting or not
        if random.random() < 0.5:
            print(f"{self.name} is skipping voting")
        else:
            suspect = random.choice(self.discussions)
            print(f"{self.name} is voting for {suspect}")
            self.voting.append(suspect)

class Imposter(Player):
    def __init__(self, name, tasks, task_queue, discussions, voting, tasks_completed, players):
        super(Imposter, self).__init__(name, tasks, task_queue, discussions, voting, tasks_completed, players)
        self.is_imposter = True

    def run(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            print(f"{self.name} is performing task: {task}")
            time.sleep(random.randint(1, 5))  # Time to perform the task
            print(f"{self.name} has completed task: {task}")
            self.task_queue.task_done()
            self.tasks_completed[0] += 1
            time.sleep(1)  # Time to "rest"

            # Imposter has a chance to kill another player
            self.kill()

            # Player participates in discussions and voting
            self.discuss()
            self.vote()

        print(f"{self.name} has completed all tasks and is waiting for voting...")

def main():
    tasks = ["Repair wiring", "Empty garbage", "Fix lights", "Download data"]
    task_queue = queue.Queue(maxsize=10)  # Queue for tasks
    for task in tasks:
        task_queue.put(task)

    discussions = ["Player-1", "Player-2", "Player-3", "Player-4", "Player-5", "Player-6"]
    voting = []
    tasks_completed = [0]  # Counter for completed tasks

    players = []

    # Creating players
    for i in range(6):
        name = f"Player-{i+1}"
        if i == 0:  # The first player becomes an imposter
            player = Imposter(name, tasks, task_queue, discussions, voting, tasks_completed, players)
        else:
            player = Player(name, tasks, task_queue, discussions, voting, tasks_completed, players)
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

    # Eliminate the player with the most votes
    if voting:
        eliminated_player = max(set(voting), key=voting.count)
        print(f"\n{eliminated_player} has been eliminated!")

    # End simulation if all tasks are completed or all non-imposter players are eliminated
    if tasks_completed[0] == len(tasks) or all(player.is_imposter for player in players[1:]):
        print("\nSimulation ended.")
    else:
        # Continue simulation with remaining players
        main()

if __name__ == "__main__":
    main()


'''
Zadania zależne od siebie: 
Wprowadź zadania, które wymagają współpracy wielu graczy do ukończenia. 
Na przykład, jeden gracz może musieć włączyć zasilanie, 
a inny musi ustawiać przełączniki, aby to osiągnąć.

Zadania dynamiczne: 
Utwórz mechanizm, który generuje nowe zadania dynamicznie w trakcie gry. 
Na przykład, po zakończeniu jednego zadania, 
może pojawić się kolejne losowo wybrane zadanie.

Debaty i głosowania: 
Implementuj system, który umożliwia graczom debatowanie 
na temat podejrzanych graczy i głosowanie na ich wykluczenie. 
Możesz użyć semaforów lub innych mechanizmów synchronizacji do zapewnienia, 
że tylko jeden gracz mówi w danym czasie.

Interaktywne zadania: 
Dodaj zadania, które wymagają interakcji z graczami, 
takie jak przekazywanie przedmiotów lub 
wykonywanie określonych czynności w określonym czasie.

Szczegółowe raportowanie: 
Utwórz mechanizm raportowania, który umożliwia graczom 
raportowanie podejrzanych zachowań lub zdarzeń, które mogą wskazywać na obecność intruzów.


Drugi impostor
Duch pierwszego zabitego impostora pomaga w sabotowaniu
'''