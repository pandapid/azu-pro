import csv
import os
from pathlib import Path
import re

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def read_contacts_from_txt(path, encoding='utf-8'):
    contacts = []
    with open(path, 'r', encoding=encoding, errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Accept formats: name,phone OR phone,name OR phone only
            parts = [p.strip() for p in re.split('[,;\t]+', line) if p.strip()]
            if len(parts) == 1:
                contacts.append({'name': '', 'phone': parts[0]})
            elif len(parts) >= 2:
                contacts.append({'name': parts[0], 'phone': parts[1]})
    return contacts

def save_to_csv(contacts, out_path):
    ensure_dir(os.path.dirname(out_path) or '.')
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name','phone'])
        writer.writeheader()
        for c in contacts:
            writer.writerow(c)

def contacts_to_vcf(contacts, out_path):
    ensure_dir(os.path.dirname(out_path) or '.')
    with open(out_path, 'w', encoding='utf-8') as f:
        for c in contacts:
            name = c.get('name','').replace('\n',' ').strip() or ''
            phone = c.get('phone','').strip()
            f.write('BEGIN:VCARD\nVERSION:3.0\n')
            if name:
                f.write(f'N:{name}\nFN:{name}\n')
            if phone:
                f.write(f'TEL;TYPE=CELL:{phone}\n')
            f.write('END:VCARD\n')

def read_vcf(path, encoding='utf-8'):
    # naive parser: split by BEGIN:VCARD
    contacts = []
    with open(path, 'r', encoding=encoding, errors='ignore') as f:
        data = f.read()
    cards = data.split('BEGIN:VCARD')
    for c in cards:
        if 'TEL' in c or 'FN' in c or 'N:' in c:
            name = ''
            phone = ''
            for line in c.splitlines():
                if line.startswith('FN:') or line.startswith('N:'):
                    name = line.split(':',1)[1].strip()
                if 'TEL' in line:
                    phone = line.split(':',1)[1].strip()
            if phone:
                contacts.append({'name': name, 'phone': phone})
    return contacts

def save_to_xlsx(contacts, out_path):
    # lazy import to keep requirements minimal until needed
    import pandas as pd
    ensure_dir(os.path.dirname(out_path) or '.')
    df = pd.DataFrame(contacts)
    df.to_excel(out_path, index=False)
