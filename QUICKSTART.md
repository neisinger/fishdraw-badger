# FishDraw Badger2040 - Schnellstart

Löse FishDraw auf deinem Badger2040 zum Laufen!

## TL;DR - 3 Schritte

### 1. Dateien kopieren
```bash
# Badger2040 mit USB anschließen
# Dann diese Dateien auf den Badger kopieren:
# - fishdraw_complete.py
# - main.py
```

### 2. Badger starten
- Schalter oben rechts auf AN
- Display zeigt "Generating..."

### 3. Fische anschauen
- Taste A drücken für neue Fische
- Taste D zum Ausschalten

## Die Dateien

| Datei | Zweck |
|-------|-------|
| `fishdraw_complete.py` | Fischgenerierungs-Engine |
| `main.py` | Badger2040 App (kopieren als `/main.py`) |
| `INSTALLATION.md` | Ausführliche Installationsanleitung |
| `BADGER2040_README.md` | Technische Dokumentation |
| `test_complete.py` | Testsuites (für Desktop) |

## Features

✓ Prozedurale Fischgenerierung  
✓ Zufälliger oder seed-basiert (reproducible)  
✓ E-Ink optimiert (schwarz/weiß)  
✓ ~80-100 Polylines pro Fisch  
✓ MicroPython kompatibel  

## Auf dem Desktop testen

```bash
# Installation
pip install -r requirements.txt  # Falls eine requirements.txt existiert
# Oder einfach:
python3 main.py
```

## Hilfreiche Links

- 📖 [Ausführliche Installation](INSTALLATION.md)
- 📚 [Technische Docs](BADGER2040_README.md)
- 🐟 [Originalcode](https://github.com/jbum/fishdraw)
- 🔧 [Badger2040 GitHub](https://github.com/pimoroni/badger2040)

## Probleme?

Siehe [INSTALLATION.md - Troubleshooting](INSTALLATION.md#troubleshooting)

## Code-Highlights

### Fisch generieren
```python
from fishdraw_complete import main, draw_svg

# Zufällig
fish = main()

# Mit Seed (reproducible)
fish = main("MyFish")

# Als SVG exportieren
svg = draw_svg(fish)
```

### Parameter anpassen
```python
from fishdraw_complete import fish, default_params

params = default_params()
params['body_length'] = 400
params['tail_length'] = 100
drawing = fish(params)
```

## Performance

- **Generierung**: 1-2 Sekunden
- **Display Update**: 3-5 Sekunden (e-ink)
- **Memory**: ~5-10 KB pro Fisch
- **Code Size**: ~30 KB (beide Python-Dateien)

Perfekt für Badger2040!

## Nächste Schritte

1. ✓ Code zum Laufen bringen (diese Anleitung)
2. → Mit Seed-Strings experimentieren
3. → Parameter anpassen für eigene Fische
4. → Code erweitern/modifizieren

---

**Version**: 1.0  
**Basiert auf**: fishdraw.js von jbum  
**Lizenz**: Gleiche wie Original  
