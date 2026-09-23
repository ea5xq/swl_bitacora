#!/usr/bin/env python3
"""
Actualiza la base de datos EiBi incrustada en ft920_control.html a partir
de un nuevo fichero sked-Xzz.csv descargado de eibispace.de.

Uso:
    python3 build_eibi.py sked-b26.csv ft920_control.html

Por defecto sobreescribe el mismo fichero HTML que le pases. Si quieres
guardar el resultado en otro sitio, pasa una tercera ruta:

    python3 build_eibi.py sked-b26.csv ft920_control.html salida.html

Solo toca el bloque "const EIBI = [...]" del HTML -- tu lista de
favoritos (SDR#) y el resto del código no se modifican. Por eso este
script y build_ft920_control.py (para los favoritos) son independientes:
puedes actualizar una base sin tocar la otra, en cualquier orden.

Formato del CSV (ver README.TXT de eibispace.de): separado por punto y
coma, 11 campos por línea:
  kHz; Time(UTC); Days; ITU; Station; Lng; Target; Site; P; Start; Stop
"""

import sys
import csv
import re
import json
from pathlib import Path

MIN_FREQ_KHZ = 100  # límite inferior de recepción general del FT-920


def parse_sked_csv(path):
    with open(path, encoding='iso-8859-1', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        rows = list(reader)

    entries = []
    excluded = 0
    for r in rows:
        if not r or not r[0]:
            continue
        freq_khz = float(r[0])
        if freq_khz < MIN_FREQ_KHZ:
            excluded += 1
            continue
        time_range, days, country, station, lang, target, site, persistence, start_date, stop_date = r[1:11]

        # Heurística de modo (misma logica usada al generar la version original)
        if days in ('LSB', 'USB'):
            mode = days
            days_out = ''
        elif lang == '-CW':
            mode = 'CW'
            days_out = days
        elif lang in ('-TY', '-HF'):
            mode = 'USB'  # RTTY / HFDL, recepcion tipica en USB
            days_out = days
        else:
            mode = 'AM'  # radiodifusion estandar, senales horarias, etc.
            days_out = days

        entries.append({
            'freq': round(freq_khz * 1000),  # Hz
            'time': time_range,
            'days': days_out,
            'country': country,
            'name': station,
            'lang': lang if not lang.startswith('-') else '',
            'target': target,
            'site': site,
            'mode': mode,
            'p': int(persistence) if persistence.isdigit() else 0,
        })

    return entries, excluded


def detect_season(filename):
    m = re.search(r'sked-([ab])(\d{2})\.csv', filename, re.IGNORECASE)
    if not m:
        return None
    kind = 'A (verano)' if m.group(1).lower() == 'a' else 'B (invierno)'
    return f"Temporada {kind} 20{m.group(2)}"


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 build_eibi.py sked-Xzz.csv ft920_control.html [salida.html]")
        sys.exit(1)

    csv_path = sys.argv[1]
    html_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else html_path

    season = detect_season(Path(csv_path).name)
    if season:
        print(f"Detectado: {season}")
    else:
        print("Aviso: el nombre de archivo no sigue el patrón sked-Xzz.csv; sigo igualmente.")

    entries, excluded = parse_sked_csv(csv_path)
    print(f"Entradas incluidas: {len(entries)}")
    print(f"Excluidas (< {MIN_FREQ_KHZ} kHz): {excluded}")

    html = Path(html_path).read_text(encoding='utf-8')

    pattern = re.compile(r'const EIBI = \[.*?\];', re.DOTALL)
    if not pattern.search(html):
        print(f"ERROR: no encuentro 'const EIBI = [...]' en {html_path}. "
              "¿Es la página correcta? ¿Ya tiene la base EiBi incrustada?")
        sys.exit(1)

    new_json = json.dumps(entries, ensure_ascii=False, separators=(',', ':'))
    html = pattern.sub(f'const EIBI = {new_json};', html, count=1)

    Path(out_path).write_text(html, encoding='utf-8')
    print(f"\nActualizado: {out_path}")


if __name__ == '__main__':
    main()
