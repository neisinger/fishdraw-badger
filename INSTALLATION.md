# FishDraw auf Badger2040 installieren

Dieser Guide zeigt, wie man FishDraw auf einem Pimoroni Badger2040 installiert und ausführt.

## Schritt 1: Hardware vorbereiten

1. **Badger2040 kaufen/erhalten**
   - Pimoroni Badger2040: https://shop.pimoroni.com/products/badger2040
   
2. **Badger2040 an Computer anschließen**
   - USB-C Kabel verwenden
   - Der Badger sollte als USB-Laufwerk erscheinen

3. **MicroPython auf Badger2040 flashen (falls nötig)**
   - Download: https://github.com/pimoroni/badger2040/releases
   - Anleitung: https://github.com/pimoroni/badger2040#getting-started
   - Empfohlene Version: MicroPython 1.20+

## Schritt 2: Dateien kopieren

Es gibt zwei Möglichkeiten: USB-Dragging oder über ein Tool.

### Option A: USB Drag & Drop (einfach)

1. Badger2040 mit USB-Kabel anschließen
2. Badger sollte als USB-Laufwerk sichtbar sein
3. Diese Dateien auf den Badger kopieren:
   ```
   fishdraw_complete.py  →  /fishdraw_complete.py
   main.py               →  /main.py
   ```

4. Fertig! Der Badger startet automatisch.

### Option B: Mit ampy Tool (professionell)

Wenn Sie das `ampy` Tool haben:

```bash
# Installation (einmalig)
pip install adafruit-ampy

# Dateien kopieren (COM-Port anpassen!)
ampy --port /dev/ttyACM0 put fishdraw_complete.py
ampy --port /dev/ttyACM0 put main.py

# Auf Windows:
ampy --port COM3 put fishdraw_complete.py
ampy --port COM3 put main.py
```

## Schritt 3: Testen

Nach dem Kopieren:

1. **Badger ein/aus schalten** (kleiner Schalter oben rechts)
2. **Display sollte sich einschalten** mit "Generating..." Text
3. **Fisch wird generiert und angezeigt**
4. **Done!** - Ein prozeduraler Fisch ist sichtbar

## Bedienung

### Badger2040 Buttons

- **A** (oben links) - Neuer Fisch (zufällig)
- **B** (unten links) - Speichern (für zukünftige Erweiterung)
- **C** (oben rechts) - Infos anzeigen
- **D** (unten rechts) - Aus/Standby

### Auf dem Desktop testen

Für Entwicklung ohne Hardware:

```bash
# Python (direkt)
python3 main.py

# Oder spezifischer
python3 -c "from fishdraw_complete import main; drawing = main(); print(f'Generated {len(drawing)} polylines')"
```

## Troubleshooting

### Problem: "Dateiaufbereitung" oder "Keine Dateien"

**Lösung:**
1. Badger mit USB anschließen
2. Warten, bis USB-Laufwerk sichtbar ist (kann 5-10 Sekunden dauern)
3. Dateien kopieren

### Problem: Badger zeigt nichts an

**Mögliche Ursachen:**
1. **Keine Stromversorgung:** USB-Kabel prüfen oder mit AAA-Batterien versuchen
2. **MicroPython nicht richtig installiert:** MicroPython neu flashen
3. **main.py nicht vorhanden:** Datei nochmal kopieren

**Lösung:**
```bash
# Terminal öffnen und mit Badger verbinden:
picocom /dev/ttyACM0  # Oder COM3 auf Windows

# Dann in der REPL:
import main
```

### Problem: "ImportError: No module named 'badger2040'"

**Ursache:** Badger2040-Bibliotheken fehlen

**Lösung:**
1. Die neueste Badger2040-Firmware installieren: https://github.com/pimoroni/badger2040/releases
2. Oder: Auf dem Desktop testen (funktioniert im Simulationsmodus)

### Problem: Display bleibt schwarz/unlesbar

**Mögliche Ursachen:**
1. Display-Kontrast zu niedrig
2. Display-Treiber-Problem

**Lösung:**
- Im Badger2040 Settings-Menü nach Display-Einstellungen suchen
- Oder: Neue Firmware flashen

### Problem: Fisch wird nicht richtig gezeichnet

**Ursachen:**
- Bestimmte Finnen-Kombinationen sehen anders aus
- Das ist normal!

**Lösungen:**
- Anderen Seed versuchen: Taste A drücken
- Mit Seed-String generieren: `main("MeinName")`

## Erweiterte Verwendung

### Seed-basierte Regeneration

Umlenken Sie einen bestimmten Fisch immer wieder:

```python
from fishdraw_complete import main

# Erzeuge den gleichen Fisch immer
drawing = main("MyFish123")
```

### SVG-Export

Fische als SVG-Dateien speichern:

```python
from fishdraw_complete import main, draw_svg

drawing = main("MyFish")
svg = draw_svg(drawing)

with open("myfish.svg", "w") as f:
    f.write(svg)
```

### Parameter anpassen

Steuern Sie die Fischmerkmale:

```python
from fishdraw_complete import fish, default_params

params = default_params()
params['body_length'] = 400  # Längerer Körper
params['tail_type'] = 2  # Andere Schwanzform
params['eye_size'] = 15  # Größeres Auge

drawing = fish(params)
```

## Speicherverwaltung

Falls der Badger Speicherprobleme hat:

```python
# Im main.py oder REPL:
import gc
gc.collect()  # Speicher freigeben

# Oder reduzieren Sie in fishdraw_complete.py:
# Zeile mit: n = 20  → n = 10  (weniger Details)
```

## Performance-Optimierungen

Für schnellere Fischgenerierung:

### In `fishdraw_complete.py`:

```python
# Reduzieren Sie diese Werte:
n = 10  # Statt 20 (weniger Punkte in Kurven)

# Oder erhöhen Sie diese:
# In cleanup():
simplified = approx_poly_dp(poly, 1.0)  # Statt 0.5 (mehr Vereinfachung)
```

## Fehlerbehebung REPL-Zugriff

Falls Sie Zugriff auf die REPL benötigen:

```bash
# Mit picocom
picocom /dev/ttyACM0 -b 115200

# Mit screen
screen /dev/ttyACM0 115200

# Mit miniterm (Python)
python3 -m serial.tools.miniterm /dev/ttyACM0 115200
```

Dann können Sie interaktiv testen:
```python
>>> from fishdraw_complete import main
>>> drawing = main("Test")
>>> len(drawing)
75
```

## Weitere Hilfe

- **Badger2040 Docs:** https://learn.pimoroni.com/article/getting-started-with-badger-2040
- **MicroPython REPL:** https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html
- **Originalcode:** https://github.com/jbum/fishdraw

## Notizen zur Portierung

Diese Python/Badger2040-Version unterscheidet sich vom Original-JavaScript:

- **Vereinfachter Code:** Fokus auf Kern-Features
- **E-Ink optimiert:** Schwarz/Weiß, keine Farben
- **MicroPython-kompatibel:** Speicher und CPU-Optimierungen
- **Modular:** `fishdraw_complete.py` kann eigenständig verwendet werden

## Lizenz

Basierend auf fishdraw.js von jbum: https://github.com/jbum/fishdraw

Diese Portierung steht unter der gleichen Lizenz.
