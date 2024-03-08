# Systemy-operacyjne-2-projekt
Projekt realizowany w ramach kursu Systemy operacyjne 2.

Temat projektu: Symulator gry opartej na koncepcji "Among us"

Opis: Symulacja gry, w której gracze współpracują przy rozwiązywaniu zadań, jednocześnie starając się odkryć i wyeliminować oszusta.
Podstawowe założenia:
1. Zarządzanie graczami
Wątki reprezentujące poszczególnych graczy będą odpowiedzialne za sterowanie postaciami i wysyłanie informacji o swoich działaniach. Dodatkowo wątki reprezentujące intruzów będą próbowały utrudnić załodze wykonywanie zadań oraz fałszywie oskarżać niewinnych.
2. Zadania do wykonania
Będą dostępne różne zadania, jak naprawa systemów, czy przeszukiwanie stacji - gracze muszą współpracować, aby je ukończyć. Wątki graczy mogą być synchronizowane, aby uniknąć kolizji podczas wykonywania tych samych zadań.
3. Wykrywanie i eliminacja intruzów
Odbywać będą się debaty i głosowania na potencjalnych intruzów. Gracze mogą próbować odkryć tożsamość intruzów na podstawie ich działań lub zgromadzonych dowodów. Wątki będą odpowiedzialne za gromadzenie i wymianę informacji, a synchronizacja pomoże uniknąć konfliktów w trakcie analizy danych.
