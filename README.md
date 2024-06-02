# Systemy-operacyjne-2-projekt
Projekt realizowany w ramach kursu Systemy operacyjne 2.

## Table of contents
* [Temat projektu](#temat-projektu)
* [Opis projektu](#opis-projektu)
* [Wynik działania programu](#wynik-działania-programu)
* [Spis wątków i sekcji krytycznych](#spis-wątków-i-sekcji-krytycznych)
* [Autor](#autor)

## Temat projektu
Symulator gry opartej na koncepcji "Among us"

## Opis projektu
Projekt to symulacja gry, w której gracze współpracują przy rozwiązywaniu zadań, jednocześnie starając się odkryć i wyeliminować oszusta. Spełnia on poniższe funkcjonalności:
* Mapa gry

Tworzona jest mapa gry o wymiarach 50 x 50. Na mapie znajduje się 5 pokoi z wejściami w różnych miejscach. Gracze chcąc wejść do danego pokoju, mogą to zrobić tylko i wyłącznie poprzez jedno z wejść. Poprzez żółte kwadraty zaznaczone zostają miejsca, w których znajdują się zadania. Niebieskie kropki reprezentują graczy, a czerwona kropka Impostora. Symulacja wyświetlana jest w aplikacji okienkowej przy użyciu biblioteki pygame.

* Zarządzanie graczami
  
Wątki reprezentujące poszczególnych graczy są odpowiedzialne za sterowanie postaciami. Początkowo generowana jest randomowa pozycja startowa dla każdego gracza, przy czym nie może ona znajdować się na obszarach zarezerwowanych (np. poprzez ściany pokoju). W swojej turze gracz pobiera zadanie z kolejki z zadaniami, a następnie przemieszcza się w lokalizację zadania. Wykonanie zadanie jest równoznaczne z zatrzymaniem gracza w danym miejscu na czas określony dla zadania (time_to_perform) oraz usunięcie zadania z listy. Gracze mają również możliwość głosowań nad podejrzanymi.

* Zarządzanie intruzem

Wątek reprezentujący intruza (dziedziczący po klasie gracza) ma na celu uniemożliwienie graczom wygrania gry poprzez sabotowanie zadań i zabijanie graczy. Impostor ma możliwość poruszanie się dwa razy szybciej po planszy, o ile w pobliżu nie znajduje się inny gracz. Tura impostora polega na wylosowaniu akcji - sabotaż lub zabicie. Zabicie gracza jest równoznaczne z zabiciem wątku gracza. Sabotowane zadania, wymagają od graczy naprawy - naprawa jest dodawana do listy zadań dla graczy.

* Zadania do wykonania

Dostępne są różne zadania dla graczy, część z nich wymaga współpracy kilku graczy do ich ukończenia. Ukończenie wszystkich zadań z gry jest równoznaczne wygraniu Graczy.

* Wykrywanie i eliminacja intruzów]
Kilka razy w ciągu rozgrywki odbywają sie głosowania. Każdy żyjący gracz i impostor głosują randomowo na innego gracza (przy czym zakazane jest głosowanie na samego siebie). Gracz z największa ilością głosów zostaje wyeliminowany z gry.

* Koniec gry
Koniec gry następuje w trzech możliwych sytuacjach. Śmierć Impostora (wygrana graczy), ukończenie wszystkich zadań z listy (wygrana graczy), eliminacja wszystkich graczy poprzez głosowania lub zabicie przez Impostora (wygrana intruza).

## Wynik działania programu

## Spis wątków i sekcji krytycznych
### Wątki
* Wątek gracza - klasa Player (każdy gracz jest reprezentowany przez osobny wątek).
* Wątek intruza - klasa Impostor.
* Wątek odpowiedzialny za nadzór końca gry - end_thread.
* Wątek odpowiedzialny za fazę głosowań - voting_thread.
* Wątek odpowiedzialny za rysowanie planszy - display_thread.

### Sekcje krytyczne

## Autor
Autor: Kinga Foksińska, nr 255591, grupa: wtorek nieparzysty 9:15
