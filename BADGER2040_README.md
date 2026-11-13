# FishDraw für Badger2040

Prozedural generierte Fischzeichnungen für das Pimoroni Badger2040 e-ink Display.

Dies ist eine Python-Portierung von [fishdraw.js](https://github.com/jbum/fishdraw), optimiert für die MicroPython/Badger2040 Hardware.

## Features

- 🐟 **Prozedurale Fischgenerierung** - Jeder Fisch ist einzigartig
- 📊 **Perlin Noise** - Natürliche, organische Formen
- 🎨 **Verschiedene Körper-Stile** - Mehrere Fischtypen
- ⚫ **E-Ink optimiert** - Schwarz/Weiß Rendering für das Badger2040
- 🔄 **Seedbar** - Zuverlässige Rekonstruktion von Fischen mit Seed-Strings

## Installation

### Hardware-Anforderungen
- Pimoroni Badger2040
- USB-Kabel für Programmierung

### Software-Setup

1. **Badger2040 vorbereiten:**
   ```bash
   # MicroPython auf Badger2040 flashen (falls nötig)
   # Siehe: https://github.com/pimoroni/badger2040/releases
   ```

2. **Code auf Badger2040 kopieren:**
   ```bash
   # Mit ampy oder ähnlichem Tool:
   ampy --port /dev/ttyACM0 put fishdraw_complete.py /
   ampy --port /dev/ttyACM0 put badger2040_fish.py /main.py
   ```

## Verwendung

### Auf dem Badger2040:

Das System startet automatisch beim Boot und zeigt einen zufälligen Fisch an.

**Button-Steuerung:**
- **A** - Neuer Fisch (Zufall)
- **B** - Speichern (für zukünftige Erweiterung)
- **C** - Info anzeigen
- **D** - Power-off

### Auf dem Desktop (zum Testen):

```python
from fishdraw_complete import main, draw_svg

# Zufälligen Fisch generieren
drawing = main()

# Mit bestimmtem Seed
drawing = main("MeinFisch123")

# Als SVG speichern
svg = draw_svg(drawing)
with open("fish.svg", "w") as f:
    f.write(svg)
```

## Architektur

### `fishdraw_complete.py`
Hauptmodul mit allen Fischgenerierungsfunktionen:
- **Perlin Noise** - Pseudozufallsalgorithmus für Naturalism
- **Geometrische Funktionen** - Punktoperationen, Polygone
- **Fischgenerierung** - `fish()`, `main()`, `generate_params()`
- **Hilfsfunktionen** - Sampling, Vereinfachung, etc.

### `badger2040_fish.py`
Badger2040-spezifische Integra integration:
- **Display-Treiber** - Hardware-Abstraction für e-ink
- **Rendering** - Polyline-Rendering mit Bresenham-Linien
- **UI-Steuerung** - Button-Handling, Menüs

## Code-Struktur

```
fishdraw_complete.py
├── Perlin Noise
│   ├── noise()
│   └── _scaled_cosine()
├── Geometrie-Utilities
│   ├── dist(), lerp(), lerp2d()
│   ├── get_bbox()
│   └── trsl_poly(), rot_poly(), scl_poly()
├── Fischgeneration
│   ├── fish() - Hauptfunktion
│   ├── fin_a(), fin_b() - Finnen
│   ├── fish_head() - Kopf
│   └── default_params(), generate_params()
└── Ausgabe
    └── draw_svg() - SVG-Export

badger2040_fish.py
├── BadgerFish - Controller-Klasse
│   ├── draw_polylines()
│   ├── _draw_line() - Bresenham
│   └── generate_and_display()
└── main_badger() - Entry Point
```

## Performance-Tipps

- **Speicher**: Fischgenerierung nutzt ~5-10 KB RAM
- **Zeit**: Generierung dauert 1-2 Sekunden
- **Display**: Refresh dauert ~3-5 Sekunden auf e-ink

Die Perlin-Noise-Tabelle wird gecacht für Performance.

## Anpassungen

### Display-Größe ändern
In `fishdraw_complete.py`:
```python
def reframe(drawing, ...):
    max_width, max_height = 296, 128  # Badger2040 Größe
    # Ändern Sie diese für andere Displays
```

### Komplexität reduzieren
Für kleinere Fische oder Performance:
```python
def fish(params):
    n = 10  # Statt 20 Punkte für die Kurve
```

### Weitere Finnentypen
Erweitern Sie `fish()` um weitere Finnen-Generierungsfunktionen.

## Portierungsnotizen

Diese Implementation ist eine Vereinfachung des Originalcodes:
- **Weggelassen**: Komplexe Polygon-Clipping, alle Shader-Typen
- **Vereinfacht**: Pattern-Generierung, Zahngenierung
- **Optimiert**: Für MicroPython-Speicherbeschränkungen

Der vollständige JavaScript-Code mit allen Features ist hier:
https://github.com/jbum/fishdraw

## Troubleshooting

### "ImportError: No module named 'badger2040'"
- Sie führen auf dem Desktop aus - das ist normal
- Für Badger2040: Müssen Sie die Badger2040-Bibliothek installiert haben

### Fisch wird nicht angezeigt
- Prüfen Sie die Display-Verbindung
- Badger2040 muss MicroPython 1.13+ haben

### Speicher-Fehler
- Reduce `n` in der Kurven-Generierung
- Reduzieren Sie die Anzahl der Polylines
- Größere Vereinfachungs-Toleranz in `cleanup()`

## Lizenz

Diese Portierung steht unter der gleichen Lizenz wie das Original.

Basierend auf: [fishdraw.js](https://github.com/jbum/fishdraw)

## Weitere Ressourcen

- [Badger2040 GitHub](https://github.com/pimoroni/badger2040)
- [MicroPython Docs](https://docs.micropython.org/)
- [Original FishDraw](https://github.com/jbum/fishdraw)
