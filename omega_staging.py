# Tento skript identifikuje technologický stack na základě existence souborů.
import os

print("\nINFO: Detekuji technologický stack...")

tech_stack = []
files = {
    "requirements.txt": "Python",
    "package.json": "Node.js/JavaScript",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java/Kotlin (Gradle)",
    "Dockerfile": "Kontejnerizace (Docker)",
    "docker-compose.yml": "Orchestrace (Docker Compose)",
    "go.mod": "Go",
    "composer.json": "PHP (Composer)"
}

for file, tech in files.items():
    if os.path.exists(file):
        tech_stack.append(tech)

if tech_stack:
    print(f"ÚSPĚCH: Detekován stack: {', '.join(tech_stack)}")
    if "Python" in tech_stack:
        print("--- Python závislosti (prvních 10) ---")
        with open("requirements.txt", "r") as f:
            for i, line in enumerate(f):
                if i >= 10: break
                print(line.strip())
else:
    print("VAROVÁNÍ: Nepodařilo se automaticky detekovat technologický stack.")
