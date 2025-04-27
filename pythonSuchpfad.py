# Python-Suchpfad anzeigen
import sys

print("Python-Suchpfad (sys.path):")
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")