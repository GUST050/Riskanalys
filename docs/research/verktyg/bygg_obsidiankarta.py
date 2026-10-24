"""Bygg återbyggbara Obsidian-filkort från Git-urvalet; ändrar aldrig originalfiler.

Kör från repot med python3.12 docs/research/verktyg/bygg_obsidiankarta.py.
--check verifierar att kartans innehåll motsvarar dagens filbytes och importer.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = 'docs/kodkarta'
MARK = '<!-- AUTO-RISKANALYS-KARTA -->'
AREAS = {
    'Intag': ('Intag och formulär', 'Aktiva frågor, svar, gemensamma underlag och lokala HTML-formulär.', ('Profil', 'Foretagsdata', 'Lokal-analys'), 'src/riskanalys/intag/webb.py', 'tester/intag'),
    'Profil': ('Byråprofil', 'Bekräftade fakta, tjänsteplaner, förändringar och uttryckligt införande med atomisk profilsparning.', ('Regelverk', 'Drift-och-lagring'), 'src/riskanalys/profil/modeller.py', 'tester/enhet/test_profil.py'),
    'Foretagsdata': ('Företagsdata', 'SCB, Bolagsverket och avgränsad iXBRL-tolkning till källbundna förslag.', ('Profil', 'Drift-och-lagring'), 'src/riskanalys/foretagsdata/samlad.py', 'tester/foretagsdata'),
    'Regelverk': ('Regelverk och regeldata', 'Källor, krav, kataloger, datumurval, typade villkor och separat sakkunniggranskning.', ('Drift-och-lagring',), 'src/riskanalys/regelverk/laddning.py', 'tester/regelkontrakt'),
    'Riskmotor': ('Deterministisk riskmotor', 'Risk per tjänst och hot, scenarier, kontrollsänkningar och generiska kundmallar.', ('Profil', 'Regelverk'), 'src/riskanalys/bedomning/motor.py', 'tester/regelkontrakt/test_scenariomotor.py'),
    'Lokal-analys': ('Lokal verksamhetsanalys', 'Gemensamt underlag i schema 2, tjänstens tillämpning, täckningsprövning och uttryckliga analysbeslut.', ('Profil', 'Riskmotor', 'Drift-och-lagring'), 'src/riskanalys/analys/tjanst.py', 'tester/enhet/test_gemensamma_operationer.py'),
    'AI-skrivning': ('AI-skrivning', 'Tillåtet faktablad, promptar, textleverantör, svarsvalidering och sparade omförsök.', ('Profil', 'Riskmotor', 'Regelverk'), 'src/riskanalys/dokument/skrivning.py', 'tester/intag/test_skyddad_begaran.py'),
    'Rapport': ('Rapportens innehåll', 'V10-resultatrapport från full V8-analys, fakta, källbundna konstruktioner och bevarade original.', ('Riskmotor', 'Lokal-analys', 'AI-skrivning'), 'src/riskanalys/dokument/arb_v10.py', 'tester/enhet/test_resultatrapport_v10.py'),
    'Word-och-leverans': ('Word och leverans', 'Fryst V10-presentation, resultatrapport, analysbilaga A och underlagsbilaga B1 som ett paket.', ('Rapport', 'Granskning', 'Drift-och-lagring'), 'src/riskanalys/dokument/rendering_v10.py', 'tester/enhet/test_rapportpaket_v10.py'),
    'Granskning': ('Granskning och fastställelse', 'Maskinella fynd, frysta underlag, mänsklig sakgranskning och låsta versionspaket.', ('Rapport', 'Lokal-analys', 'Regelverk', 'Drift-och-lagring'), 'src/riskanalys/granskning/korning.py', 'tester/enhet/test_faststall.py'),
    'Drift-och-lagring': ('Drift och lagring', 'Datamapp, kontrollsummor, manifest, modellidentitet, modellrisk och historik.', ('Regelverk',), 'src/riskanalys/lagring/manifest.py', 'tester/enhet/test_manifest.py'),
    'CLI': ('Kommandorad och start', 'Programmets start, nyckelläsning, användarfel och CLI-adaptrar till kärnan.', ('Intag', 'Riskmotor', 'AI-skrivning', 'Granskning'), 'src/riskanalys/cli.py', 'tester/enhet/test_cli.py'),
    'Tester': ('Tester och syntetiska underlag', 'Enhet, intag, regelkontrakt, M2, typfall och frysta historiska fixturer.', ('Riskmotor', 'AI-skrivning', 'Rapport', 'Granskning'), 'tester/conftest.py', 'tester'),
    'Projekt': ('Projektets dokumentation', 'Befintlig spec, status, planer, research, verktyg och gemensamma arbetsregler.', ('CLI', 'Tester'), 'AGENTS.md', 'docs/STATUS.md'),
}
AI = {'aischema.py', 'claude.py', 'delskrivning.py', 'delvalidering.py', 'faktablad.py', 'leverantor.py', 'likhet.py', 'matning.py', 'platshallare.py', 'skrivning.py', 'skrivversion.py', 'underlag.py', 'validering.py'}
WORD = {'export.py', 'leverans_v8.py', 'presentation_v8.py', 'rapportpaket_v8.py', 'rapportvyer.py', 'rendering.py', 'wordstil.py'}
WORD_PREFIXES = ('leverans_', 'presentation_', 'rapportpaket_', 'rapportvyer_', 'rendering_', 'wordstil_', 'redaktionell_', 'redaktionmodell_', 'redaktionspresentation_', 'presentationsval_')


def owner(path: str) -> str:
    if path.startswith(('tester/', 'scripts/test')): return 'Tester'
    if path=='src/riskanalys/konfiguration.py': return 'AI-skrivning'
    if path=='src/riskanalys/arbetsfloden.py': return 'Word-och-leverans'
    if path.startswith(('regelbas/', 'src/riskanalys/regelverk/')): return 'Regelverk'
    for folder, area in [('intag','Intag'), ('profil','Profil'), ('foretagsdata','Foretagsdata'), ('bedomning','Riskmotor'), ('analys','Lokal-analys'), ('granskning','Granskning'), ('faststallelse','Granskning'), ('drift','Drift-och-lagring'), ('lagring','Drift-och-lagring'), ('kommandon','CLI')]:
        if path.startswith('src/riskanalys/'+folder+'/'): return area
    if path.startswith('src/riskanalys/dokument/'):
        if '/promptar/' in path or Path(path).name in AI: return 'AI-skrivning'
        return 'Word-och-leverans' if Path(path).name in WORD or Path(path).name.startswith(WORD_PREFIXES) else 'Rapport'
    return 'CLI' if path.startswith('src/riskanalys/') else 'Projekt'


def inventory() -> list[str]:
    raw = subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'], cwd=ROOT).decode()
    # Git-indexet innehåller även filer som tagits bort i arbetskopian.
    deleted = subprocess.check_output(['git','ls-files','-d','-z'],cwd=ROOT).decode().split('\0')
    files = sorted(set(raw.split('\0'))-{''}-set(deleted))
    for p in files:
        if p.startswith(('.obsidian/', OUT+'/')) or Path(p).name.startswith('.env'):
            raise ValueError('Privat eller genererad fil hamnade i Git-urvalet: '+p)
        if not (ROOT/p).resolve().is_relative_to(ROOT):
            raise ValueError('Kartlägg inte original utanför repot: '+p)
    return files


def old_descriptions() -> dict[str,str]:
    text = (ROOT/'docs/PROGRAMKARTA.md').read_text()
    if '<!-- filtrad-start -->' not in text: return {}
    body = text.split('<!-- filtrad-start -->',1)[1].split('<!-- filtrad-slut -->',1)[0]
    result = {}; stack = []
    for line in body.splitlines():
        m = re.fullmatch(r'((?:│   |    )*)(?:├── |└── )(.+?) — (.+)',line)
        if not m: continue
        depth = len(m[1])//4
        stack = stack[:depth]
        name = re.sub(r' \[[^\]]+\]$','',m[2])
        path = '/'.join([*stack,name.rstrip('/')])
        if name.endswith('/'): stack.append(name.rstrip('/'))
        else: result[path] = m[3]
    return result


def card(path: str) -> str:
    original = Path(path)
    visible = original.with_name('fil-'+original.name) if original.name.startswith('.') else original
    return f'{OUT}/filer/{visible.as_posix()}.md'


def wiki(path: str, label: str | None = None) -> str:
    return '[['+path+('|' + label if label else '')+']]'


def generated(text: str) -> bool:
    return text.startswith(MARK) or (text.startswith('---\n') and '\n'+MARK+'\n' in text[:600])


def build() -> tuple[dict[str,str],dict]:
    files = inventory(); descriptions = old_descriptions(); records = {}; trees = {}; modules = {}
    for p in files:
        data = (ROOT/p).read_bytes()
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = None
        row = {'path':p,'sha256':hashlib.sha256(data).hexdigest(),'lines':len(text.splitlines()) if text is not None else None,'area':owner(p)}
        if text is None: row.update(binary=True, bytes=len(data))
        if (ROOT/p).is_symlink():
            row['link_target'] = (ROOT/p).resolve().relative_to(ROOT).as_posix()
        if p.endswith('.py'):
            if text is None: raise ValueError('Pythonfilen är inte UTF-8: '+p)
            t = ast.parse(text); trees[p] = t
            row['symbols'] = [n.name for n in t.body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and not n.name.startswith('_')]
            doc = ast.get_docstring(t)
            if p not in descriptions and doc: descriptions[p] = ' '.join(doc.split())
            mod = p.removeprefix('src/').removesuffix('.py').replace('/','.')
            if mod.endswith('.__init__'): mod = mod.removesuffix('.__init__')
            modules[mod] = p
        records[p] = row
    deps = defaultdict(set)
    for mod,p in modules.items():
        pkg = mod if p.endswith('/__init__.py') else mod.rpartition('.')[0]
        for n in ast.walk(trees[p]):
            targets = []
            if isinstance(n,ast.Import): targets = [a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom):
                base = n.module or ''
                if n.level: base = '.'.join(pkg.split('.')[:len(pkg.split('.'))-n.level+1]+([base] if base else []))
                targets = [base+'.'+a.name if base+'.'+a.name in modules else base for a in n.names]
            for target in targets:
                if target in modules and modules[target]!=p: deps[p].add(modules[target])
    output = {}; counts = {}
    for area,(title,purpose,related,entry,tests) in AREAS.items():
        subset = [p for p in files if owner(p)==area]; counts[area] = len(subset)
        lines = ['---', 'typ: filregister', f'omrade: {area}', 'tags: [riskanalys, genererat]', '---', MARK, '', '# Filer: '+title, '',
                 wiki('docs/omraden/'+area+'.md', 'Områdets läsguide')+' · '+wiki('docs/START.md','Start'), '',
                 'Genererade filkort. Originalen är källan; områdesgruppering är en läshjälp.', '', f'{len(subset)} projektfiler.', '']
        for p in subset:
            size = f'{records[p]["bytes"]} byte, binär fil' if records[p].get('binary') else f'{records[p]["lines"]} rader'
            lines.append('- '+wiki(card(p),p)+' — '+size+'.')
        output[f'{OUT}/omraden/{area}.md'] = '\n'.join(lines)+'\n'
    for p,row in records.items():
        desc = descriptions.get(p)
        if not desc:
            if row.get('binary'): desc = 'Binär projektresurs; filstorlek och kontrollsumma inventeras utan texttolkning.'
            elif p.startswith('docs/omraden/'): desc = 'Kort läsguide med ansvar, ingångar och samband till befintlig kod/spec.'
            elif p=='docs/START.md': desc = 'Gemensam projektingång för Obsidian, Codex och Claude Code.'
            elif p.endswith('.md'):
                headings = re.findall(r'^# (.+)$',(ROOT/p).read_text(),re.M)
                desc = 'Dokumentation: '+(headings[0] if headings else Path(p).stem)+'.'
            else: desc = 'Projektfil i området '+AREAS[row['area']][0]+'. Se originalfilen för fullständigt innehåll.'
        # Samma ansvarstext har en daterad källa; hash och importer kommer från dagens bytes.
        front = ['---','typ: filkort',f'omrade: {row["area"]}', 'kallfil: '+json.dumps(p,ensure_ascii=False), 'rader: '+('null' if row['lines'] is None else str(row['lines'])),f'kall_sha256: {row["sha256"]}',
                 'tags: [riskanalys, filkort, '+('kod' if p.startswith('src/') else 'test' if p.startswith('tester/') else 'regeldata' if p.startswith('regelbas/') else 'dokumentation')+']','---',MARK,'', '# '+p,'',desc,'',
                 '**Område:** '+wiki('docs/omraden/'+row['area']+'.md',AREAS[row['area']][0]), '',
                 '**Original:** '+f'[{p}]({os.path.relpath(p, str(Path(card(p)).parent))})','',
                 '## Direkta interna importer','']
        if row.get('link_target') in records:
            front += ['Intern fillänk till '+wiki(card(row['link_target']),row['link_target'])+'.', '']
        front += ['- '+wiki(card(d),d) for d in sorted(deps[p])] or ['Ingen direkt statisk intern import hittad (eller filen är inte Python).']
        front += ['', '## Definitioner', '', ', '.join('`'+n+'`' for n in row.get('symbols',[])) or 'Inga publika funktioner/klasser på modulnivå, eller ingen Pythonfil.', '',
                  '## Tolka relationerna','', 'Importer visar statiska beroenden, även lokala/villkorade importer. Bakåtlänkar visar vilka andra filkort som länkar hit. Testimporter är inte ett mått på testtäckning.', '',
                  'Ansvarstexten hämtas från den daterade programkartan eller modulens dokumentationssträng. Original, radantal, SHA-256 och importer läses på nytt vid generering.', '']
        if row.get('binary'):
            front.insert(front.index('---', 1), 'byte: '+str(row['bytes']))
        output[card(p)] = '\n'.join(front)
    summary = {'schema':1,'project_files':len(files),'python_files':len(trees),'source_files':sum(p.startswith('src/') for p in files),'source_lines':sum(r['lines'] for p,r in records.items() if p.startswith('src/')),'import_edges':sum(len(x) for x in deps.values()),'areas':counts,'files':records}
    index = ['---','typ: kodkarta','tags: [riskanalys, genererat]','---',MARK,'','# Alla projektfiler','',wiki('docs/START.md','Start')+' · '+wiki('docs/PROGRAMKARTA.md','Fullständigt annoterat filträd'),'',
             f'{len(files)} originalfiler, {summary["source_files"]} programfiler och {summary["source_lines"]} programrader. Genererade anteckningar och lokala Obsidian-inställningar ingår inte i originalurvalet.','',
             'Filkorten speglar originalen och kan byggas om. De är inte nya moduler i programmet.','']
    index += ['- '+wiki(f'{OUT}/omraden/{k}.md',AREAS[k][0])+f' — {v} filer' for k,v in counts.items()]
    index += ['', '## Uppdatera', '', '```bash', 'python3.12 docs/research/verktyg/bygg_obsidiankarta.py', 'python3.12 docs/research/verktyg/bygg_obsidiankarta.py --check', '```', '']
    output[f'{OUT}/INDEX.md'] = '\n'.join(index)
    output[f'{OUT}/inventering.json'] = json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    return output,summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    output,summary = build()
    root = ROOT/OUT
    existing = {p.relative_to(ROOT).as_posix() for p in root.rglob('*') if p.is_file()} if root.exists() else set()
    missing = [p for p,v in output.items() if not (ROOT/p).is_file() or (ROOT/p).read_text()!=v]
    extra = sorted(existing-set(output))
    if args.check:
        if missing or extra:
            print(json.dumps({'aktuell':False,'nya_eller_andrade':missing,'extra':extra},ensure_ascii=False,indent=2));return 1
    else:
        for p in extra:
            file = ROOT/p
            if file.is_symlink() or not generated(file.read_text()):
                raise ValueError('Tar inte bort en okänd fil i den genererade mappen: '+p)
        for p,v in output.items():
            file=ROOT/p
            if file.is_symlink(): raise ValueError('Skriver inte genom en symbolisk länk: '+p)
            if file.exists() and p not in missing: continue
            if file.exists() and p.endswith('.md') and not generated(file.read_text()):
                raise ValueError('Skriver inte över en handskriven anteckning: '+p)
            file.parent.mkdir(parents=True,exist_ok=True);file.write_text(v)
        for p in extra: (ROOT/p).unlink()
    print(json.dumps({k:summary[k] for k in ('project_files','python_files','source_files','source_lines','import_edges','areas')},ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
