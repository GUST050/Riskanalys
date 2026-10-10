# Provkörning av en implementeringsplan

`provkor_plan.py` bygger projektet ur planens kodblock i en tom mapp, i samma ordning som stegen i planen. Det visar att kodblocken hänger ihop och att testerna passerar innan planen används. Verktyget är inte en del av programmet och har inga egna tester.

```bash
python3 -I docs/superpowers/plans/verktyg/provkor_plan.py docs/superpowers/plans/2026-10-08-m0-m1-grund-och-tunn-kedja.md /tmp/provkorning
cd /tmp/provkorning
git init -q
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

Utmappen ska vara tom och ligga utanför repot. Verktyget kopierar också de repofiler som planens tester läser men planen inte skriver (`REPOFILER`, i dag tillsynsfallen i `docs/research/typfall/`). `git init` behövs eftersom manifestet sparar aktuell commit. Med `--till-task N` byggs bara Task 1–N. Ligger planfilen utanför repot, till exempel en sparad version, anges repots rot med `--repo`.

Skriptet förstår de stegformuleringar som planen använder: "Skriv `fil`", "Lägg till ... sist i `fil`" (med "Lägg till `import x` bland importerna") och "Registrera ... i `src/riskanalys/cli.py`". Ett steg som inte känns igen hoppas över och skrivs ut, så att det går att se vad som inte provkördes, till exempel ändringar i README och STATUS.
