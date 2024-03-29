'''
TO DO:
- inny przydział tasków 
- zakończenie symulacji, gdy taski zostana wykonane (poza taskami impostora)
- sabotowanie tasków - konsekwencje (moze bedzie sabotowac inne rzeczy niz taski)
- głosowania

def vote(self):
        # Randomly decide whether to skip voting or not
        if random.random() < 0.2:
            print(f"{self.name} is skipping voting")
        else:
            suspect = random.choice(self.discussions)
            print(f"{self.name} is voting for {suspect}")
            self.voting.append(suspect)


w mainie:       
if voting:
    eliminated_player = max(set(voting), key=voting.count)
    print(f"\n{eliminated_player} has been eliminated!")


- dyskusje
- zabijanie watkow
- aplikacja okienkowa z symulacja
- zadania do wykonywania przez wiecej niz jednego gracza
- konczenie symulacji, gdy nie ma wiecej zadan lub gdy impostor zabije kogos lub nie naprawia szkod impostora
- sciany na mapie
- impostor moze poruszac sie szybko jesli wokol nie ma innych (raczej trzeba powiekszyc mapke)
'''