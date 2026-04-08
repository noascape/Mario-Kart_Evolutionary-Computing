# Projekt-Dokumentation: Evolutionäres Pathfinding in Mario Kart
**Thema:** Optimierung von Speedruns mittels Genetischer Algorithmen (GA)
**Kontext:** Modul Evolutionary Computing (DHBW Mosbach)
**Basierend auf:** Vorlesung 5, Folie 6 (Ablauf des Entwurfs)

---

## 1. Einleitung & Zielsetzung
Ziel dieses Projekts ist die Entwicklung und der Vergleich verschiedener evolutionärer Ansätze zur Pfadfindung in Mario Kart (SNES). Der Fokus liegt auf der Optimierung der Fahrlinie für einen "Time Trial"-Modus, um eine minimale Rundenzeit zu erreichen.

---

## 2. Anforderungsanalyse (Gemäß Folie 6)
*   **Systemumgebung:** Integration über OpenAI Gym Retro (SNES) oder Emulator-Schnittstelle (BizHawk).
*   **Eingaberaum:** Digitale Steuerung (Gas, Bremse, Links, Rechts, Drift).
*   **Leistungsziel:** Erreichen einer Rundenzeit, die deutlich über der Zufallssuche liegt und sich der menschlichen Performance annähert.
*   **Priorität:** Stabilität der Steuerung und Überwindung von Hindernissen/Kurven ohne Wandkollision.

---

## 3. Problemanalyse & Risikobewertung
*   **Zielfunktion (Fitness):** 
    *   Primär: Zurückgelegte Distanz auf der Strecke innerhalb eines Zeitlimits.
    *   Sekundär: Minimale Rundenzeit (sobald Ziel erreicht wird).
    *   Penalty: Abzug für Wandberührungen oder Verlassen der Strecke.
*   **Entscheidungsvektor:** Binäre oder diskrete Belegung der Controller-Buttons pro Frame/Zeitintervall.
*   **Nebenbedingungen:** Streckenbegrenzung, Offroad-Terrain (Verlangsamung).
*   **Risiken:** Lokale Optima (Hängenbleiben an einer Kurveninnenseite), "Stall" (Agent fährt im Kreis oder bleibt stehen).

---

## 4. Repräsentationsalternativen (Detaillierter Entwurf)
Das Herzstück des Agenten ist ein **Neuronales Netz (Controller)**, das Inputs (Sensordaten wie Wandabstände, Geschwindigkeit, Kurvenwinkel) verarbeitet und Outputs (Controller-Eingaben) liefert. Die folgenden drei Repräsentationsvarianten beschreiben unterschiedliche Wege, wie dieses "Gehirn" im GA kodiert und optimiert wird.

---

### Alternative 1: Fixed Topology Neuroevolution (Vektor-Kodierung)
Dies ist der klassische ML-Ansatz. Die Struktur des Netzes (Anzahl Layer, Neuronen pro Layer) ist fest vorgegeben. Nur die Stärke der Verbindungen (Gewichte) wird optimiert.

*   **Genom-Struktur:** Ein 1D-Fließkomma-Vektor (Float-Array). 
    *   *Beispiel:* Ein Netz mit 5 Inputs, 10 Hidden-Nodes und 3 Outputs hätte ca. 80-100 Gewichte. Das Genom ist schlicht die Liste dieser Werte: `[w1, w2, w3, ..., wn]`.
*   **Operatoren:**
    *   **Mutation:** *Gaußsche Mutation.* Zu zufällig gewählten Gewichten wird ein kleiner Wert aus einer Normalverteilung addiert (z.B. `w = w + N(0, σ)`). Dies erlaubt eine feine Justierung des Verhaltens.
    *   **Crossover:** *Uniform Crossover.* Für jedes Gewicht im "Kind-Gehirn" wird gewürfelt, ob es vom Vater oder von der Mutter stammt. Dies kombiniert erfolgreiche Teil-Strategien (z.B. "Bremsen-Logik" von A mit "Lenk-Logik" von B).
*   **Fokus:** Optimierung der bestehenden Gehirnkapazität.

---

### Alternative 2: Evolving Topology (NEAT-Ansatz)
Hier ist das Gehirn nicht starr. Die Evolution entscheidet selbst, wie komplex das Netz sein muss, um die Strecke zu meistern.

*   **Genom-Struktur:** Eine Liste von zwei Listen:
    1.  **Node-Genes:** Liste der Neuronen (Input, Hidden, Output).
    2.  **Connection-Genes:** Liste der Verbindungen mit Attributen wie `(In-Node, Out-Node, Gewicht, Aktiviert-Status, Innovations-Nummer)`.
*   **Operatoren:**
    *   **Mutation:** 
        *   *Gewicht-Mutation:* Wie bei Alt. 1.
        *   *Struktur-Mutation:* Ein neues Neuron wird mitten in eine bestehende Verbindung "eingeschleust" oder eine völlig neue Verbindung zwischen zwei bisher unverbundenen Neuronen wird gewürfelt.
    *   **Crossover:** *Innovation-Alignment.* Dank der Innovations-Nummern können zwei unterschiedlich komplexe Gehirne "übereinandergelegt" werden. Das Kind übernimmt die passenden Teile beider Eltern und behält die strukturellen Fortschritte bei.
*   **Fokus:** Evolution der Gehirn-Architektur (von einfach zu komplex).

---

### Alternative 3: Discrete Action-Logic (Sequence-Net)
Anstatt kontinuierlicher Gewichte wird das Gehirn hier als eine Art "Zustands-Aktions-Matrix" betrachtet, die wie ein extrem vereinfachtes, diskretes Netz funktioniert.

*   **Genom-Struktur:** Ein 2D-Array (Matrix).
    *   Die Zeilen repräsentieren diskrete Zustände (z.B. "Ich bin in Kurve 1", "Ich bin auf der Geraden").
    *   Die Spalten enthalten die optimale Controller-Aktion für diesen Moment.
    *   *Genom-Logik:* `[Zustand_0: Aktion_A, Zustand_1: Aktion_B, ...]`.
*   **Operatoren:**
    *   **Mutation:** *Bit-Flip / Integer-Swap.* Eine Aktion für einen bestimmten Zustand wird zufällig gegen eine andere getauscht (z.B. "In Kurve 1 nicht mehr Driften, sondern nur Lenken").
    *   **Crossover:** *Multi-Point Crossover.* Ganze "Sektoren" der Logik werden zwischen den Eltern getauscht (z.B. das Verhalten für die erste Streckenhälfte kommt von Parent A, die zweite von Parent B).
*   **Fokus:** Optimierung der Entscheidungslogik in diskreten Schritten.

---

## 5. Roadmap & Implementierungsplan (Prozess nach Folie 6)
Um den Anforderungen gerecht zu werden, werden wir **Alternative 1** und **Alternative 2** (oder 3) implementieren, da diese den größten wissenschaftlichen Kontrast in der Optimierung des Neuronalen Netzes bieten.

### Phase 1: Setup & Baselines (Woche 1)
1.  **Framework-Integration:** Anbindung des Spiels an das Python-Skript.
2.  **Baselines:** Implementierung der **Zufallssuche (Naive)** und einer einfachen **lokalen Suche (Hill Climbing)** als Vergleichswerte.

### Phase 2: Implementierung & GA-Entwurf (Woche 2)
1.  **GA 1 (Direct Path):** Entwicklung der Operatoren (Mutation von Dauer/Aktion, Crossover von Teilpfaden).
2.  **GA 2 (Fixed NN):** Definition der Netzstruktur und Abbildung auf den Genvektor.
3.  **Fitness-Funktion:** Feinjustierung des Belohnungssystems (Fitness Shaping).

### Phase 3: Parametrisierung & Studie (Woche 3)
1.  Durchführung von Testläufen zur Ermittlung optimaler Mutationsraten und Populationsgrößen.
2.  **Iterative Schleife (Folie 6):** Bei Unzufriedenheit Re-Design der Operatoren oder Parameter.

### Phase 4: Vergleich & Evaluierung (Woche 4)
1.  **Benchmarking:** 2x GA vs. 1x Naiv vs. 1x Lokale Suche.
2.  **Metriken:** Konvergenz (Fitness über Generationen), Best-of-Run Visualisierung (Heatmap der Ideallinie).
3.  **Dokumentation:** Zusammenführung der Ergebnisse im finalen Bericht.

---

## 6. Metriken & Vergleichskriterien
*   **Güte:** Maximale Fitness / Minimale Zeit pro Runde.
*   **Effizienz:** Anzahl der Generationen bis zur Konvergenz.
*   **Robustheit:** Varianz der Ergebnisse über mehrere Läufe.
