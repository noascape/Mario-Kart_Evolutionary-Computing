# Detaillierte Repräsentationsentwürfe für Mario Kart GA

Diese Dokumentation beschreibt die drei primären Repräsentationsalternativen für den evolutionären Controller. Das gemeinsame Ziel aller Varianten ist die Optimierung eines neuronalen Steuerungssystems ("Gehirn"), das basierend auf Telemetriedaten (Position, Speed, Wandabstand) die optimalen Controller-Eingaben berechnet.

---

## 1. Repräsentation: Linear Weight Vector (Fixed Topology)
In diesem Modell ist die Architektur des neuronalen Netzes (Anzahl der Schichten und Neuronen) statisch. Das Genom kodiert lediglich die Stärke der Verbindungen.

### Genom-Struktur
Das Genom ist ein **1D-Vektor aus Fließkommazahlen** (Floats). Jeder Wert entspricht einem Gewicht ($w$) oder einem Bias ($b$) im Netzwerk.

**Demo-Tabelle (Ausschnitt eines Individuums):**
| Index | Komponente | Beschreibung | Beispiel-Wert |
| :--- | :--- | :--- | :--- |
| 0 | $w_{in1 \to h1}$ | Gewicht: Input 1 (Wand links) zu Hidden 1 | `0.452` |
| 1 | $w_{in2 \to h1}$ | Gewicht: Input 2 (Wand rechts) zu Hidden 1 | `-0.128` |
| ... | ... | ... | ... |
| 42 | $b_{h1}$ | Bias des ersten Hidden-Neurons | `0.010` |
| 85 | $w_{h10 \to out1}$ | Gewicht: Hidden 10 zu Output 1 (Gas) | `0.982` |

### Evolutionäre Operatoren
*   **Selektion:** **Rank-Based Selection**. Die Population wird nach Fitness sortiert; die Wahrscheinlichkeit zur Paarung basiert auf dem Rangplatz, nicht auf dem absoluten Fitnesswert (verhindert Dominanz einzelner "Super-Individuen").
*   **Mutation:** **Gaussian Noise**. $w' = w + \sigma$ wobei $\sigma \sim N(0, I)$. Kleine, zufällige Störungen der Gewichte erlauben feines Nachjustieren.
*   **Crossover:** **Uniform Crossover**. Für jedes Gen wird mit einer 50/50 Chance entschieden, ob es von Elternteil A oder B übernommen wird.

---

## 2. Repräsentation: Augmented Topology (Dynamic NEAT)
Dieser Ansatz evolviert sowohl die Gewichte als auch die **Topologie** (Verknüpfungsstruktur) des Netzwerks. Das Netz wächst mit der Komplexität der Aufgabe.

### Genom-Struktur
Das Genom besteht aus zwei Listen: **Node Genes** (Neuronen) und **Connection Genes** (Verbindungen). Jedes Gen besitzt eine globale **Innovationsnummer**, um historische Herkunft zu tracken.

**Demo-Tabelle (Connection Genes):**
| Innov-Nr. | In-Node | Out-Node | Gewicht | Aktiviert |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 1 (SensL) | 4 (OutL) | 0.7 | Ja |
| 2 | 2 (SensR) | 4 (OutL) | -0.5 | Nein (deaktiviert durch Mutation) |
| 3 | 2 (SensR) | 5 (OutR) | 0.2 | Ja |
| 4 | 4 (OutL) | 6 (NewH) | 0.1 | Ja (neue Verbindung) |

### Evolutionäre Operatoren
*   **Selektion:** **Tournament Selection with Speciation**. Individuen treten in kleinen Gruppen gegeneinander an. "Speziation" schützt innovative neue Strukturen, indem sie nur innerhalb ähnlicher Topologien verglichen werden.
*   **Mutation:**
    *   *Strukturell:* "Add Node" (spaltet Verbindung auf) oder "Add Connection" (verbindet zwei lose Neuronen).
    *   *Gewicht:* Klassische Gaußsche Störung.
*   **Crossover:** **Innovation-Based Alignment**. Eltern werden anhand ihrer Innovationsnummern abgeglichen. Matching-Gene werden gemischt, "Disjoint"-Gene (neue Strukturen) werden vom fitteren Elternteil übernommen.

---

## 3. Repräsentation: 2D "Gnome" Matrix (State-Action Indices)
Dieser Ansatz betrachtet das Genom als eine 2D-Matrix, die den Zustandsraum direkt auf Aktions-Indizes abbildet. Ein "Gnome" entspricht hier einer Spalte der Matrix (einem spezifischen Verhaltensset).

### Genom-Struktur
Das Genom ist eine **Matrix ($M \times N$)**. Zeilen repräsentieren Zustands-Kategorien (z.B. Oberflächentyp, Geschwindigkeit, Kurvenradius), Spalten repräsentieren diskrete Zeitabschnitte oder Sektoren.

**Demo-Tabelle (Genom als Entscheidungsmatrix):**
| Zustand / Sektor | Sektor 1 (Start) | Sektor 2 (Kurve 1) | Sektor 3 (Gerade) |
| :--- | :--- | :--- | :--- |
| **Geschwindigkeit** | 1 (Beschleunigen) | 2 (Halten) | 1 (Beschleunigen) |
| **Lenkung** | 0 (Gerade) | -1 (Links Driften) | 0 (Gerade) |
| **Item-Nutzen** | 0 (Nein) | 0 (Nein) | 1 (Turbo nutzen) |

*Jede Zelle enthält einen Index für eine vordefinierte Aktions-Palette.*

### Evolutionäre Operatoren
*   **Selektion:** **Elitismus**. Die besten 2-5% der Generation werden direkt und unverändert in die nächste übernommen, um mühsam gelernte Ideallinien ("Gnomes") nicht zu verlieren.
*   **Mutation:** **Violated Directed Mutation**. Eine gesamte Spalte (ein "Gnome") wird durch eine neue, zufällige Strategie ersetzt oder ein einzelner Aktions-Index wird geflippt.
*   **Crossover:** **One-Point Matrix Crossover**. Es wird ein vertikaler Schnitt durch die Matrix gemacht. Sektoren 1-10 kommen von A, Sektoren 11-Ende kommen von B.

---

## Zusammenfassung der Strategie
| Rep.-Typ | Datenstruktur | Primäre Einheit | Beste Selektion |
| :--- | :--- | :--- | :--- |
| **Fixed** | 1D Float Array | Einzelnes Gewicht | Rank-Based |
| **Dynamic** | Graph / Link List | Connection/Node Gene | Tournament |
| **2D Matrix** | Matrix of Indices | Spalte ("Gnome") | Elitismus |
