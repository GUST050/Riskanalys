"""Gemensamma lokala analysoperationer för CLI och loopbackformuläret."""
from dataclasses import dataclass
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

RAPPORTID = ('modell:projektrapport', 'modell:valideringsrapport', 'modell:modellfiler')


@dataclass(frozen=True)
class Analysstatus:
    paket: m.Analyspaket | None
    revision: str
    brister: tuple[str, ...]
    profil: object
    bedomning: object


class Analystjanst:
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

    def forslag(self):
        with l.analyslas(self.mapp):
            bm, _, bindning = self._underlag()
            return forifyll_analys(self.rb, las_profil(self.mapp), las_bedomning(bm), bindning)

    def starta(self, revision):
        with l.analyslas(self.mapp):
            paket, bm, _, bindning = self._last(revision)
            if paket:
                raise RiskanalysFel('Analysen finns redan. Läs den sparade analysen.')
            nytt = forifyll_analys(self.rb, las_profil(self.mapp), las_bedomning(bm), bindning)
            return self._spara(nytt, forvantad_summa=revision)

    def fornya(self, revision):
        """Explicit ny bindning efter jämförelse; inga manuella svar skrivs över."""
        with l.analyslas(self.mapp):
            paket, bm, _, bindning = self._last(revision, aktuell=False)
            if paket is None:
                raise RiskanalysFel('Starta ett analysutkast först.')
            forslag = forifyll_analys(self.rb, las_profil(self.mapp), las_bedomning(bm), bindning)
            tjanster = tuple(t.model_copy(update={'block': tuple(b.model_copy(update={'bekraftad_summa': None}) for b in t.block), 'scenariokopplingar': tuple(k.model_copy(update={'bekraftad': False}) for k in t.scenariokopplingar)}) for t in paket.tjanster)
            tjanster += tuple(t for t in forslag.tjanster if t.tjanst not in {a.tjanst for a in paket.tjanster})
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

    def spara_block(self, tjanst, nummer, data, revision):
        from riskanalys.intag.analysformular import las_blockformular
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None:
                raise RiskanalysFel('Starta ett analysutkast först.')
            andring = las_blockformular(paket, tjanst, nummer, data, rb=self.rb)
            a = andring.tjanst.model_copy(update={'forfattare': self._forfattare(andring.forfattare)})
            nytt = paket.model_copy(update={'tjanster': tuple(a if t.tjanst == tjanst else t for t in paket.tjanster)})
            if andring.operation == 'bekrafta':
                summa = p.blocksumma(nytt, tjanst, nummer)
                a = a.model_copy(update={'block': tuple(b.model_copy(update={'bekraftad_summa': summa}) if b.nummer == nummer else b for b in a.block)})
                nytt = nytt.model_copy(update={'tjanster': tuple(a if t.tjanst == tjanst else t for t in nytt.tjanster)})
            return self._spara(nytt, forvantad_summa=revision)

    def spara_scenarioval(self, tjanst, scenario, data, revision):
        from riskanalys.intag.analysformular import hamta_tjanst, las_scenarioval
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None:
                raise RiskanalysFel('Starta ett analysutkast först.')
            val = las_scenarioval(paket, tjanst, scenario, data)
            a = hamta_tjanst(paket, tjanst)
            katalog = self.rb.tjanster[tjanst]
            gem = next(s for s in paket.gemensamma_scenarier if s.id == scenario)
            if not set(gem.hot) <= set(katalog.hot):
                raise RiskanalysFel('Det gemensamma scenariot hör inte till tjänstens kataloghot.')
            kopplingar = tuple(k for k in a.scenariokopplingar if k.scenario != scenario) + (val.model_copy(update={'bekraftad': True}),)
            a = a.model_copy(update={'scenariokopplingar': kopplingar, 'forfattare': self._forfattare(data.get('forfattare', ''))})
            nytt = paket.model_copy(update={'tjanster': tuple(a if t.tjanst == tjanst else t for t in paket.tjanster)})
            return self._spara(nytt, forvantad_summa=revision)

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
            if inkommande.bindning != bindning:
                raise RiskanalysFel('Svarfilen gäller ett annat underlag. Jämför den aktuella förifyllnaden.')
            tjanster = tuple(t.model_copy(update={'forfattare': namn, 'block': tuple(b.model_copy(update={'bekraftad_summa': None}) for b in t.block), 'scenariokopplingar': tuple(k.model_copy(update={'bekraftad': False}) for k in t.scenariokopplingar)}) for t in inkommande.tjanster)
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

    def spara_modellrisk(self, data, revision):
        tillatna = {'csrf', 'revision', 'rutinbelagg', 'modellansvarig', 'utvarderad', 'nasta_genomgang', 'feluppfoljning', 'godkand', 'beslutad_av', 'beslutsdatum'}
        if set(data) - tillatna or data.get('godkand') not in ('ja', 'nej'):
            raise RiskanalysFel('Pröva modellens lokala användning och välj uttryckligen ja eller nej.')
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            belagg = {b.id: b for b in paket.belagg} if paket else {}
            ids = (*RAPPORTID, data.get('rutinbelagg', ''))
            if not paket or any(id not in belagg or not belagg[id].dokument for id in ids):
                raise RiskanalysFel('Importera projektets rapportpaket en gång samt registrera byråns modellriskrutin som privat dokumentbelägg.')
            def ref(id):
                b = belagg[id]
                return Modellbelagg(fil=b.dokument, kontrollsumma=b.kontrollsumma)
            u = Modellriskunderlag(modellansvarig=data.get('modellansvarig', ''), modellbindning=paket.bindning.modell,
                rutin=ref(ids[3]), projektrapport=ref(ids[0]), valideringsrapport=ref(ids[1]), modellfiler=ref(ids[2]),
                utvarderad=date.fromisoformat(data.get('utvarderad', '')), nasta_genomgang=date.fromisoformat(data.get('nasta_genomgang', '')),
                feluppfoljning=data.get('feluppfoljning', ''), fel=paket.modellrisk.fel if paket.modellrisk else (), godkand=data['godkand'] == 'ja',
                beslutad_av=data.get('beslutad_av', ''), beslutsdatum=date.fromisoformat(data.get('beslutsdatum', '')))
            return self._spara(paket.model_copy(update={'modellrisk': u}), forvantad_summa=revision)


    def spara_gemensamt(self, scenario, data, revision):
        from riskanalys.intag.analysformular import hamta_scenario, normalisera_urval, referensval, faltlista
        tillatna = {'csrf', 'revision', 'scenario', 'visad_summa', 'forfattare', 'hot', 'rubrik', 'handelseforlopp', 'relevans', 'motivering', 'belagg'}
        namn = self._forfattare(data.get('forfattare', ''))
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None:
                raise RiskanalysFel('Starta analysen först.')
            tidigare = hamta_scenario(paket, scenario)
            val = referensval(paket, m.Tjansteanalys(tjanst=''), self.rb)
            val['hot'] = tuple((id, self.rb.hot[id].namn) for id in tidigare.hot)
            data = normalisera_urval(data, faltlista(m.Scenarioanalys), val)
            if set(data) - tillatna:
                raise RiskanalysFel('Välj bara fält i det gemensamma scenarioformuläret.')
            if data.get('visad_summa') != p.scenariosumma(tidigare):
                raise RiskanalysFel('Scenariot har ändrats. Läs om sidan före nästa svar.')
            raw = tidigare.model_dump(mode='json')
            for key in ('hot', 'rubrik', 'handelseforlopp', 'relevans', 'motivering', 'belagg'):
                if key in data:
                    raw[key] = tuple(x.strip() for x in data[key].split(',') if x.strip()) if key in ('hot', 'belagg') else data[key]
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

    def spara_modellfel(self, data, revision):
        from riskanalys.drift.modellrisk import Modellfel
        from riskanalys.intag.analysformular import normalisera_urval
        tillatna = {'csrf', 'revision', 'id', 'datum', 'beskrivning', 'allvar', 'status', 'atgard_och_omprovning', 'belagg'}
        with l.analyslas(self.mapp):
            paket, _, _, _ = self._last(revision)
            if paket is None or paket.modellrisk is None:
                raise RiskanalysFel('Registrera paketets lokala modellriskunderlag före feluppföljning.')
            val = {'belagg': tuple((b.id, b.id) for b in paket.belagg if b.dokument)}
            data = normalisera_urval(data, [('belagg', tuple[str, ...], tuple[str, ...])], val)
            if set(data) - tillatna:
                raise RiskanalysFel('Välj bara de visade lokala modellfälten.')
            ids = tuple(x.strip() for x in data.get('belagg', '').split(',') if x.strip())
            b = {b.id: b for b in paket.belagg if b.dokument}
            if len(ids) != len(set(ids)) or set(ids) - set(b):
                raise RiskanalysFel('Välj registrerade privata dokumentbelägg för rättning och omprövning.')
            fel = Modellfel(id=data.get('id', ''), datum=date.fromisoformat(data.get('datum', '')),
                beskrivning=data.get('beskrivning', ''), allvar=data.get('allvar', ''), status=data.get('status', ''),
                atgard_och_omprovning=data.get('atgard_och_omprovning', ''),
                belagg=tuple(Modellbelagg(fil=b[id].dokument, kontrollsumma=b[id].kontrollsumma) for id in ids))
            poster = tuple(f for f in paket.modellrisk.fel if f.id != fel.id) + (fel,)
            u = paket.modellrisk.model_copy(update={'fel': poster, 'godkand': False})
            return self._spara(paket.model_copy(update={'modellrisk': u}), forvantad_summa=revision)
