import os

print("[OMEGA] Fáze 2: Spouštím generátor webových stránek...")

THEMES_FILE = 'themes.txt'
TEMPLATE_FILE = 'templates/base.html'
OUTPUT_DIR = 'generated_sites'
sites_created = 0

try:
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_content = f.read()
except FileNotFoundError:
    print(f"[ERROR] Šablona nebyla nalezena: {TEMPLATE_FILE}")
    exit(1)

try:
    with open(THEMES_FILE, 'r', encoding='utf-8') as f:
        themes = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"[ERROR] Seznam témat nebyl nalezen: {THEMES_FILE}")
    exit(1)

for theme in themes:
    site_dir = os.path.join(OUTPUT_DIR, theme)
    os.makedirs(site_dir, exist_ok=True)
    
    title = theme.replace('_', ' ')
    
    site_content = template_content.replace('{{TITLE}}', title)
    site_content = site_content.replace('{{HEADER}}', title)
    site_content = site_content.replace('{{THEME_NAME}}', title)
    
    with open(os.path.join(site_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(site_content)
        
    sites_created += 1

print(f"[OMEGA] Úspěšně vygenerováno {sites_created} webových stránek.")
print("[OMEGA] Fáze 2 dokončena.")
