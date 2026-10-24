"""Gemensamma lokala analysoperationer för CLI och loopbackformuläret."""
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from riskanalys.analys import lagring as l, modeller as m, provning as p
from riskanalys.analys.utkast import forifyll_analys
from riskanalys.bedomning.korning import BEDOMNINGAR, las_bedomning
from riskanalys.dokument.skrivning import UTKAST
from riskanalys.drift.modellrisk import Modellbelagg, Modellriskunderlag
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.korningar import senaste_korning
from riskanalys.lagring.manifest import las_manifest
from riskanalys.profil.lagring import las_profil
from riskanalys.regelverk.modeller import hot_dimensioner

from riskanalys.analys.andringar import Blockandring, Scenarioval, Scenarioandring, Modellriskandring, Modellfelandring, hamta_tjanst, hamta_scenario, tillampa_block

RAPPORTID = ('modell:projektrapport', 'modell:valideringsrapport', 'modell:modellfiler')


@dataclass(frozen=True)
class Analysstatus:
    paket: m.Analyspaket | None
    revision: str
    brister: tuple[str, ...]
    profil: object
    bedomning: object


from riskanalys.analys.gemensamma_operationer import GemensammaOperationer


class Analystjanst(GemensammaOperationer):
    def __init__(self, mapp: Path, rb):
        self.mapp = mapp
        self.rb = rb

    def _spara(self, paket, *, forvantad_summa):
        validerat = m.Analyspaket.model_validate(paket.model_dump(mode='json'))
        self._katalogreferenser(validerat)
        self._modellfelovergang(l.las_analys(self.mapp), validerat)
        return l.spara_analys_last(self.mapp, validerat, forvantad_summa=forvantad_summa)

    def _katalogreferenser(self, paket):
        if any(set(b.profilfalt) - set(self.rb.falt) for b in paket.belagg):
            raise RiskanalysFel('Välj profilfält ur den aktuella intagskatalogen.')
        for g in paket.gemensamma_sarbarhetsprovningar:
            if set(g.sarbarheter)-set(self.rb.sarbarheter) or set(g.hot)-set(self.rb.hot) or set(g.profilfalt)-set(self.rb.falt):
                raise RiskanalysFel('Välj gemensamma faktorer, hot och profilfält ur den aktuella katalogen.')
            if any(g.dimension!='bada' and g.dimension not in hot_dimensioner(self.rb.hot[h]) for h in g.hot):
                raise RiskanalysFel('Gemensam post har oförenligt hot och dimension. Välj rätt hot/dimension ur katalogen.')
        for s in paket.gemensamma_scenarier:
            if set(s.hot) - set(self.rb.hot):
                raise RiskanalysFel('Välj gemensamma hot ur den aktuella källkatalogen.')
        for t in paket.tjanster:
            kat = self.rb.tjanster.get(t.tjanst)
            if kat is None:
                raise RiskanalysFel('Importerade tjänster måste finnas i den aktuella källkatalogen.')
            if any(set(s.hot) - set(kat.hot) for s in t.scenarier):
                raise RiskanalysFel('Lokala kataloghot måste höra till tjänsten.')
            if any(set(s.sarbarheter) - set(self.rb.sarbarheter) for s in t.sarbarhetsprovningar):
                raise RiskanalysFel('Välj sårbarheter ur den aktuella källkatalogen.')
            for app in t.sarbarhetstillampningar:
                if app.post not in {g.id for g in paket.gemensamma_sarbarhetsprovningar} or any(x.hot not in self.rb.hot for x in app.hotkopplingar):
                    raise RiskanalysFel('Tillämpningen hänvisar till okänd gemensam post eller hot.')
            if any(x.post not in {g.id for g in paket.gemensamma_verksamhetsposter} for x in t.verksamhetstillampningar):
                raise RiskanalysFel('Tillämpningen hänvisar till okänd verksamhetspost.')
            for k in t.kontroller:
                if k.kontroll not in kat.kontroller:
                    raise RiskanalysFel('Välj kontroller som hör till tjänsten.')
                rader = {r.id for r in self.rb.kontroller[k.kontroll].rackvidd if r.tjanst == t.tjanst}
                if set(k.rackvidd) - rader:
                    raise RiskanalysFel('Välj källräckvidd för rätt kontroll och tjänst.')

    def _modellfelovergang(self, tidigare, nytt):
        """Kända fel försvinner inte genom svarimport eller ny rapportleverans."""
        gamla = tidigare.modellrisk.fel if tidigare and tidigare.modellrisk else ()
        poster = {f.id: f for f in nytt.modellrisk.fel} if nytt.modellrisk else {}
        for f in gamla:
            n = poster.get(f.id)
            if n is None or f.allvar == 'vasentligt' and n.allvar != 'vasentligt':
                raise RiskanalysFel('Kända modellfel måste bevaras. Dokumentera rättning och omprövning i stället för att ta bort eller nedgradera felet.')
            if f.allvar == 'vasentligt' and f.status == 'oppet' and n.status == 'atgardat':
                if (not n.atgard_och_omprovning.strip() or not n.belagg
                        or n.datum > nytt.modellrisk.utvarderad):
                    raise RiskanalysFel('Ett väsentligt modellfel kräver dokumenterad rättning, belägg och aktuell omprövning före stängning.')
                for b in n.belagg:
                    l.las_belaggsfil(self.mapp, b.fil, b.kontrollsumma)

    def _underlag(self, version=m.BINDNINGSVERSION):
        um = senaste_korning(self.mapp, UTKAST, 'skriv ' + self.mapp.name)
        namn = las_manifest(um).metadata.get('bedomning', '')
        if not namn or Path(namn).name != namn:
            raise RiskanalysFel('Skrivutkastets bedömningsreferens är ogiltig. Skapa ett nytt utkast.')
        bm = self.mapp / BEDOMNINGAR / namn
        bindning = l.bygg_bindning(self.mapp, self.rb, bm, um, version=version)
        return bm, um, bindning

    def _last(self, revision, *, aktuell=True):
        """Returnerar aktuell bindning; ett sparat paket prövas mot sin egen bindningsversion."""
        paket = l.las_analys(self.mapp)
        if (p.registersumma(paket) if paket else '') != revision:
            raise RiskanalysFel('Analysen har ändrats i en annan flik. Läs om sidan före nästa svar.')
        bm, um, bindning = self._underlag()
        if aktuell and paket:
            version = paket.bindning.bindningsversion
            sparad = bindning if version == bindning.bindningsversion else self._underlag(version)[2]
            if paket.bindning != sparad:
                raise RiskanalysFel('Analysens underlag har ändrats. Jämför förifyllnaden och förnya bindningen före nästa svar.')
        return paket, bm, um, bindning

    def status(self, datum=None):
        with l.analyslas(self.mapp):
            bm, um, _ = self._underlag()
            s = l.las_analyssnapshot_last(self.mapp, self.rb, datum or date.today(), bedomningsmapp=bm, utkastmapp=um)
            return Analysstatus(s.paket, s.registersumma, s.brister, las_profil(self.mapp), las_bedomning(bm))

    def forslag(self, *, schema=1):
        with l.analyslas(self.mapp):
            bm, _, bindning = self._underlag()
            return forifyll_analys(self.rb, las_profil(self.mapp), las_bedomning(bm), bindning, schema=schema)

    def starta(self, revision, *, schema=1):
        with l.analyslas(self.mapp):
            paket, bm, _, bindning = self._last(revision)
            if paket:
                raise RiskanalysFel('Analysen finns redan. Läs den sparade analysen.')
            nytt = forifyll_analys(self.rb, las_profil(self.mapp), las_bedomning(bm), bindning, schema=schema)
            return self._spara(nytt, forvantad_summa=revision)

    def overfor(self,revision,jamfort):
        from riskanalys.analys.overforing import foresla_overforing
        if jamfort is not True:raise RiskanalysFel('Jämför överföringsförslaget med originalet före överföring.')
        with l.analyslas(self.mapp):
            paket,_,_,bindning=self._last(revision)
            if paket is None:raise RiskanalysFel('Starta ett analysutkast först.')
            nytt=foresla_overforing(self.rb,paket).model_copy(update={'bindning':bindning})
            nytt=m.Analyspaket.model_validate(nytt.model_dump(mode='json'))
            self._katalogreferenser(nytt)
            self._modellfelovergang(paket,nytt)
            for fil,hash in l.analysbelaggsreferenser(paket):l.las_belaggsfil(self.mapp,fil,hash)
            return l.spara_overforing_last(self.mapp,nytt,forvantad_summa=revision)

    def fornya(self, revision):
        """Explicit ny bindning efter jämförelse; inga manuella svar skrivs över."""
        with l.analyslas(self.mapp):
            paket, bm, _, bindning = self._last(revision, aktuell=False)
            if paket is None:
                raise RiskanalysFel('Starta ett analysutkast först.')
            forslag = forifyll_analys(self.rb, las_profil(self.mapp), las_bedomning(bm), bindning, schema=paket.schemaversion)
            tjanster = tuple(t.model_copy(update={'sarbarhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in t.sarbarhetstillampningar), 'verksamhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in t.verksamhetstillampningar), 'tackningsprovningar':tuple(x.model_copy(update={'visad_summa':None}) for x in t.tackningsprovningar), 'block': tuple(b.model_copy(update={'bekraftad_summa': None}) for b in t.block), 'scenariokopplingar': tuple(k.model_copy(update={'bekraftad': False}) for k in t.scenariokopplingar)}) for t in paket.tjanster)
            nya=tuple(t for t in forslag.tjanster if t.tjanst not in {a.tjanst for a in paket.tjanster})
            if paket.schemaversion==2:
                from riskanalys.analys.gemensam import tillampningar_for_poster
                nya=tuple(tillampningar_for_poster(paket,t) for t in nya)
            tjanster += nya
            gemensamma = paket.gemensamma_scenarier + tuple(s for s in forslag.gemensamma_scenarier if s.id not in {a.id for a in paket.gemensamma_scenarier})
            belagg = tuple(b for b in paket.belagg if not b.profilfalt) + forslag.belagg
            nytt = paket.model_copy(update={'bindning': bindning, 'tjanster': tjanster, 'gemensamma_scenarier': gemensamma, 'belagg': belagg})
            return self._spara(nytt, forvantad_summa=revision)

    @staticmethod
    def _forfattare(text):
        namn = text.strip()
        if not namn or len(namn) > 200:
            raise RiskanalysFel('Ange författarens namn eller lokala person-ID (högst 200 tecken).')
        return namn

    def spara_block(self, andring: Blockandring):
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(andring.revision)
            if paket is None:
                raise RiskanalysFel('Starta ett analysutkast först.')
            andring = replace(andring, forfattare=self._forfattare(andring.forfattare))
            nytt = tillampa_block(paket,andring,rb=self.rb)
            return self._spara(nytt,forvantad_summa=andring.revision)

    def spara_scenarioval(self, andring: Scenarioval):
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(andring.revision)
            if paket is None:
                raise RiskanalysFel('Starta ett analysutkast först.')
            a = hamta_tjanst(paket,andring.tjanst)
            gem = hamta_scenario(paket,andring.scenario)
            val = m.Scenariokoppling.model_validate(andring.val.model_dump(mode='json'))
            if val.scenario!=gem.id or val.scenariosumma!=p.scenariosumma(gem):
                raise RiskanalysFel('Det gemensamma scenariot har ändrats. Läs om jämförelsen.')
            if val.tillampning=='avviker' and (val.lokal_scenario not in {s.id for s in a.scenarier} or not val.motivering):
                raise RiskanalysFel('Välj en lokal scenarioanalys för denna tjänst och motivera avvikelsen.')
            if val.tillampning=='samma' and val.lokal_scenario:
                raise RiskanalysFel('En lokal avvikelse kräver valet avviker.')
            if val.tillampning not in ('samma','avviker'):
                raise RiskanalysFel('Välj uttryckligen samma eller avviker efter genomgången.')
            if not set(gem.hot)<=set(self.rb.tjanster[andring.tjanst].hot):
                raise RiskanalysFel('Det gemensamma scenariot hör inte till tjänstens kataloghot.')
            kopplingar = tuple(k for k in a.scenariokopplingar if k.scenario!=gem.id)+(val.model_copy(update={'bekraftad':True}),)
            a = a.model_copy(update={'scenariokopplingar':kopplingar,'forfattare':self._forfattare(andring.forfattare)})
            nytt = paket.model_copy(update={'tjanster':tuple(a if t.tjanst==andring.tjanst else t for t in paket.tjanster)})
            return self._spara(nytt,forvantad_summa=andring.revision)

    def beslut(self, tjanst, godkand, namn, roll, datum, kommentar, revision):
        with l.analyslas(self.mapp):
            paket, bm, um, _ = self._last(revision)
            if paket is None:
                raise RiskanalysFel('Starta och granska analysen först.')
            b = m.Analysbeslut(tjanst=tjanst, revision=paket.revision,
                underlagssumma=p.underlagssumma(paket), svarssumma=p.svarssumma(paket),
                godkand=godkand, namn=namn, roll=roll, datum=datum, kommentar=kommentar or None)
            return l.registrera_analysbeslut_last(self.mapp, self.rb, b, forvantad_summa=revision, bedomningsmapp=bm, utkastmapp=um)

    def importera_svar(self, fil, forfattare, revision):
        from riskanalys.lagring.yamlfil import las_yaml
        try:
            inkommande = m.Analyspaket.model_validate(las_yaml(fil))
        except (ValidationError, ValueError, OSError) as exc:
            raise RiskanalysFel('Analysfilen kan inte läsas. Använd analyspaketets typade YAML- eller JSON-format.') from exc
        if inkommande.beslut:
            raise RiskanalysFel('Svarimport får inte innehålla beslut eller godkännanden.')
        namn = self._forfattare(forfattare)
        with l.analyslas(self.mapp):
            paket, _, _, bindning = self._last(revision, aktuell=False)
            if paket and inkommande.schemaversion!=paket.schemaversion:
                raise RiskanalysFel('Vanlig svarimport får inte byta schema. Använd uttrycklig överföring till schema 2.')
            if inkommande.bindning != bindning:
                raise RiskanalysFel('Svarfilen gäller ett annat underlag. Jämför den aktuella förifyllnaden.')
            tjanster = tuple(t.model_copy(update={'sarbarhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in t.sarbarhetstillampningar), 'verksamhetstillampningar':tuple(x.model_copy(update={'bekraftad':False}) for x in t.verksamhetstillampningar), 'tackningsprovningar':tuple(x.model_copy(update={'visad_summa':None}) for x in t.tackningsprovningar), 'forfattare': namn, 'block': tuple(b.model_copy(update={'bekraftad_summa': None}) for b in t.block), 'scenariokopplingar': tuple(k.model_copy(update={'bekraftad': False}) for k in t.scenariokopplingar)}) for t in inkommande.tjanster)
            nytt = inkommande.model_copy(update={'tjanster': tjanster, 'beslut': paket.beslut if paket else (), 'modellrisk': inkommande.modellrisk.model_copy(update={'godkand': False}) if inkommande.modellrisk else None})
            if paket:
                nytt = self._ateranvand_bekraftelser(paket, nytt)
            return self._spara(nytt, forvantad_summa=revision)

    @staticmethod
    def _ateranvand_bekraftelser(tidigare, nytt):
        """Betro endast tidigare lokala val som matchar samma underlag och innehåll."""
        if tidigare.bindning != nytt.bindning:
            return nytt
        gamla = {t.tjanst: t for t in tidigare.tjanster}
        gem = {s.id: s for s in nytt.gemensamma_scenarier}
        oldgem = {s.id: s for s in tidigare.gemensamma_scenarier}
        tjanster = []
        for t in nytt.tjanster:
            old = gamla.get(t.tjanst)
            kopplingar = []
            for k in t.scenariokopplingar:
                fore = next((x for x in old.scenariokopplingar if x.scenario == k.scenario), None) if old else None
                lika = (fore and fore.bekraftad and k.scenario in gem and k.scenario in oldgem
                    and fore.scenariosumma == p.scenariosumma(oldgem[k.scenario]) == p.scenariosumma(gem[k.scenario])
                    and fore.model_dump(exclude={'bekraftad'}) == k.model_dump(exclude={'bekraftad'}))
                kopplingar.append(k.model_copy(update={'bekraftad': bool(lika)}))
            tjanster.append(t.model_copy(update={'scenariokopplingar': tuple(kopplingar)}))
        nytt = nytt.model_copy(update={'tjanster': tuple(tjanster)})
        tjanster = []
        for t in nytt.tjanster:
            old = gamla.get(t.tjanst)
            poster = []
            for b in t.block:
                fore = next((x for x in old.block if x.nummer == b.nummer), None) if old else None
                lika = (fore and fore.bekraftad_summa
                    and fore.bekraftad_summa == p.blocksumma(tidigare, t.tjanst, b.nummer)
                    and fore.bekraftad_summa == p.blocksumma(nytt, t.tjanst, b.nummer))
                poster.append(b.model_copy(update={'bekraftad_summa': fore.bekraftad_summa if lika else None}))
            tjanster.append(t.model_copy(update={'block': tuple(poster)}))
        return nytt.model_copy(update={'tjanster': tuple(tjanster)})

    def importera_belagg(self, fil, id, datum, revision):
        # Kopiera före låset: den publika importören tar själv analyslas.
        rel, hash = l.importera_belagg(self.mapp, fil)
        b = m.Analysbelagg(id=id.strip(), dokument=rel, kontrollsumma=hash, datum=datum)
        if not b.id or b.id.startswith(('modell:', 'profil:')):
            raise RiskanalysFel('Ange ett unikt beläggs-ID utan de reserverade prefixen modell: och profil:.')
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None or b.id in {b.id for b in paket.belagg}:
                raise RiskanalysFel('Starta analysen och välj ett nytt unikt beläggs-ID.')
            return self._spara(paket.model_copy(update={'belagg': (*paket.belagg, b)}), forvantad_summa=revision)

    def importera_rapport(self, mapp, datum, revision):
        kopior = l.importera_modellrapport(self.mapp, mapp)
        poster = tuple(m.Analysbelagg(id=id, dokument=b.fil, kontrollsumma=b.kontrollsumma, datum=datum) for id, b in zip(RAPPORTID, (kopior.projektrapport, kopior.valideringsrapport, kopior.modellfiler)))
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None:
                raise RiskanalysFel('Starta analysen före rapportregistrering.')
            underlag = paket.modellrisk
            if underlag:
                underlag = underlag.model_copy(update={'projektrapport': kopior.projektrapport, 'valideringsrapport': kopior.valideringsrapport, 'modellfiler': kopior.modellfiler, 'godkand': False})
            nytt = paket.model_copy(update={'belagg': tuple(b for b in paket.belagg if b.id not in RAPPORTID) + poster, 'modellrisk': underlag})
            return self._spara(nytt, forvantad_summa=revision)

    def spara_modellrisk(self, andring: Modellriskandring, revision):
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            belagg = {b.id: b for b in paket.belagg} if paket else {}
            ids = (*RAPPORTID, andring.rutinbelagg)
            if not paket or any(id not in belagg or not belagg[id].dokument for id in ids):
                raise RiskanalysFel('Importera projektets rapportpaket en gång samt registrera byråns modellriskrutin som privat dokumentbelägg.')
            def ref(id):
                b = belagg[id]
                return Modellbelagg(fil=b.dokument, kontrollsumma=b.kontrollsumma)
            u = Modellriskunderlag(modellansvarig=andring.modellansvarig, modellbindning=paket.bindning.modell,
                rutin=ref(ids[3]), projektrapport=ref(ids[0]), valideringsrapport=ref(ids[1]), modellfiler=ref(ids[2]),
                utvarderad=andring.utvarderad, nasta_genomgang=andring.nasta_genomgang,
                feluppfoljning=andring.feluppfoljning, fel=paket.modellrisk.fel if paket.modellrisk else (), godkand=andring.godkand,
                beslutad_av=andring.beslutad_av, beslutsdatum=andring.beslutsdatum)
            return self._spara(paket.model_copy(update={'modellrisk': u}), forvantad_summa=revision)


    def spara_gemensamt(self, andring: Scenarioandring):
        scenario, revision = andring.scenario, andring.revision
        tillatna = {'hot','rubrik','handelseforlopp','relevans','motivering','belagg'}
        data = dict(andring.varden)
        if len(data)!=len(andring.varden) or set(data)-tillatna:
            raise RiskanalysFel('Ändringen innehåller okända scenariofält.')
        namn = self._forfattare(andring.forfattare)
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None:
                raise RiskanalysFel('Starta analysen först.')
            tidigare = hamta_scenario(paket, scenario)
            if andring.visad_summa != p.scenariosumma(tidigare):
                raise RiskanalysFel('Scenariot har ändrats. Läs om sidan före nästa svar.')
            raw = tidigare.model_dump(mode='json')
            for key in ('hot', 'rubrik', 'handelseforlopp', 'relevans', 'motivering', 'belagg'):
                if key in data:
                    raw[key] = data[key]
            a = m.Scenarioanalys.model_validate(raw)
            if (len(a.hot) != len(set(a.hot)) or len(a.belagg) != len(set(a.belagg))
                    or set(a.hot) - set(self.rb.hot) or set(a.belagg) - {b.id for b in paket.belagg}):
                raise RiskanalysFel('Välj unika registrerade kataloghot och belägg.')
            if set(a.hot) != set(tidigare.hot):
                raise RiskanalysFel('Gemensamma kataloghot kan inte flyttas mellan tjänster. Lägg tjänstens extra scenario i dess analys.')
            tjanster = []
            for t in paket.tjanster:
                berord = any(k.scenario == scenario for k in t.scenariokopplingar)
                kopplingar = tuple(k.model_copy(update={'bekraftad': False}) if k.scenario == scenario else k for k in t.scenariokopplingar)
                tjanster.append(t.model_copy(update={'scenariokopplingar': kopplingar, 'forfattare': namn if berord else t.forfattare}))
            nytt = paket.model_copy(update={'gemensamma_scenarier': tuple(a if s.id == scenario else s for s in paket.gemensamma_scenarier), 'tjanster': tuple(tjanster)})
            return self._spara(nytt, forvantad_summa=revision)

    def spara_modellfel(self, andring: Modellfelandring, revision):
        from riskanalys.drift.modellrisk import Modellfel
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None or paket.modellrisk is None:
                raise RiskanalysFel('Registrera paketets lokala modellriskunderlag före feluppföljning.')
            ids = andring.belagg
            b = {b.id: b for b in paket.belagg if b.dokument}
            if len(ids) != len(set(ids)) or set(ids) - set(b):
                raise RiskanalysFel('Välj registrerade privata dokumentbelägg för rättning och omprövning.')
            fel = Modellfel(id=andring.id, datum=andring.datum,
                beskrivning=andring.beskrivning, allvar=andring.allvar, status=andring.status,
                atgard_och_omprovning=andring.atgard_och_omprovning,
                belagg=tuple(Modellbelagg(fil=b[id].dokument, kontrollsumma=b[id].kontrollsumma) for id in ids))
            poster = tuple(f for f in paket.modellrisk.fel if f.id != fel.id) + (fel,)
            u = paket.modellrisk.model_copy(update={'fel': poster, 'godkand': False})
            return self._spara(paket.model_copy(update={'modellrisk': u}), forvantad_summa=revision)
