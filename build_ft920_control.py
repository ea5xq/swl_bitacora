#!/usr/bin/env python3
"""
Actualiza la lista de favoritos (SDR#) incrustada en ft920_control.html
a partir de un nuevo export Frequencies.xml.

Uso:
    python3 build_ft920_control.py Frequencies.xml ft920_control.html

Por defecto sobreescribe el mismo fichero HTML que le pases. Si quieres
guardar el resultado en otro sitio, pasa una tercera ruta:

    python3 build_ft920_control.py Frequencies.xml ft920_control.html salida.html

Solo toca los bloques "const STATIONS = [...]" y "const GROUP_LABELS =
{...}" del HTML -- la base EiBi (si ya la incrustaste con build_eibi.py)
y el resto del código no se modifican. Por eso este script y
build_eibi.py son independientes: puedes actualizar una base sin tocar
la otra, en cualquier orden.
"""

import sys
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

MIN_FREQ_HZ = 100_000  # límite inferior de recepción general del FT-920

GROUP_LABELS = {
    'WEFAX': 'WEFAX',
    'VOLMET': 'VOLMET',
    'SWRADIOGRAMA': 'Radio de onda corta',
    'AERO_HF': 'Aeronáutica HF',
    'mil_rus_GF': 'Militar ruso',
    'mil_france': 'Militar francés',
    'VLF_NDB': 'Radiobalizas VLF/NDB',
    'LW': 'Onda larga',
    'MW': 'Onda media',
    'beacons': 'Radiobalizas',
    'NAVTEX': 'NAVTEX',
    'W1AW': 'W1AW (ARRL)',
    'MRHS': 'MRHS',
    'RADIOPIRATAS': 'Radios piratas',
    'RADIO_EUPRIV': 'Radio privada europea',
    'PEGASUS': 'Pegasus (HF militar)',
}


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    entries = []
    excluded = []
    for entry in root.findall('MemoryEntry'):
        freq = int(entry.find('Frequency').text)
        name = entry.find('Name').text.strip()
        mode = entry.find('DetectorType').text
        group = entry.find('GroupName').text
        if freq < MIN_FREQ_HZ:
            excluded.append((name, freq))
            continue
        entries.append({'freq': freq, 'mode': mode, 'name': name, 'group': group})

    entries.sort(key=lambda e: (e['group'], e['freq']))
    for i, e in enumerate(entries, start=1):
        e['ch'] = i

    return entries, excluded


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 build_ft920_control.py Frequencies.xml ft920_control.html [salida.html]")
        sys.exit(1)

    xml_path = sys.argv[1]
    html_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else html_path

    entries, excluded = parse_xml(xml_path)

    print(f"Emisoras incluidas: {len(entries)}")
    if excluded:
        print(f"Excluidas por estar bajo {MIN_FREQ_HZ/1000:.0f} kHz:")
        for name, freq in excluded:
            print(f"  - {name} ({freq/1000:.1f} kHz)")

    html = Path(html_path).read_text(encoding='utf-8')

    labels_used = {g: GROUP_LABELS.get(g, g) for g in sorted(set(e['group'] for e in entries))}
    stations_json = json.dumps(entries, ensure_ascii=False)
    labels_json = json.dumps(labels_used, ensure_ascii=False)

    stations_pattern = re.compile(r'const STATIONS = \[.*?\];', re.DOTALL)
    labels_pattern = re.compile(r'const GROUP_LABELS = \{.*?\};', re.DOTALL)

    if not stations_pattern.search(html) or not labels_pattern.search(html):
        print(f"ERROR: no encuentro 'const STATIONS' o 'const GROUP_LABELS' en {html_path}.")
        sys.exit(1)

    html = stations_pattern.sub(f'const STATIONS = {stations_json};', html, count=1)
    html = labels_pattern.sub(f'const GROUP_LABELS = {labels_json};', html, count=1)

    Path(out_path).write_text(html, encoding='utf-8')
    print(f"\nActualizado: {out_path}")


if __name__ == '__main__':
    main()
