"""En byrås intag, med explicit grunddata och skydd mot gamla formulär."""
from datetime import date
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.svar import besvara
from riskanalys.intag.tackning import tackning
from riskanalys.lagring.datamapp import byramapp
from riskanalys.profil.hantering import skapa_profil, bekrafta
from riskanalys.profil.lagring import PROFILFIL, las_profil, spara_profil, profilrevision
from riskanalys.profil.modeller import Byra
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.tillsyn import tillsynsomrade
from riskanalys.regelverk.urval import valj


class Intagstjanst:
    def __init__(self, byra_id: str, rb: Regelbas):
        self.mapp = byramapp(byra_id)
        self.rb = rb

    def finns(self):
        return (self.mapp / PROFILFIL).is_file()

    def profil(self):
        return las_profil(self.mapp)

    def skapa(self, lan: str, filial: bool, datum: date, kalla: str, roll: str, *, filialkalla: str | None = None, svar: tuple[IntagSvar, ...] = ()):
        if self.finns():
            raise RiskanalysFel('Byrån finns redan. Återuppta det sparade intaget.')
        if type(filial) is not bool or datum > date.today() or not roll.strip() or len(roll)>200:
            raise RiskanalysFel('Bekräfta filial, ett bedömningsdatum senast idag och ansvarig funktion.')
        paket = tillsynsomrade(lan, filial)
        valj(self.rb, paket, datum, "Stockholm" if filial else lan)
        p = skapa_profil(self.rb, Byra(id=self.mapp.name, lan="Stockholm" if filial else lan, regelpaket=paket, datum=datum))
        for id,text in [('P-ORG.sateslan',lan),('P-ORG.utlandsk_filial','ja' if filial else 'nej')]:
            p=bekrafta(p,self.rb,id,text,filialkalla if id=='P-ORG.utlandsk_filial' and filialkalla is not None else kalla,roll,date.today())
        for uppgift in svar:
            p=besvara(self.rb,p,uppgift)
        self.mapp.mkdir(parents=True, exist_ok=True, mode=0o700)
        spara_profil(self.mapp,p,revision='')
        return p

    def spara(self, svar: IntagSvar, revision: str, *, rattelse=None):
        return self.spara_flera((svar,),revision, rattelse=rattelse)

    def spara_flera(self, svar: tuple[IntagSvar, ...], revision: str, *, rattelse=None):
        """Validera hela urvalet innan en enda atomisk profilsparning."""
        p=self.profil()
        if profilrevision(p) != revision:
            raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan; det nya svaret skrevs inte över.')
        nytt=p
        for uppgift in svar:
            nytt=besvara(self.rb,nytt,uppgift)
        from riskanalys.profil.forandringar import spara_andring
        return spara_andring(self.mapp,self.rb,nytt,revision,rattelse=rattelse)

    def spara_plan(self, plan, revision):
        from riskanalys.profil.forandringar import spara_andring
        p = self.profil()
        planer = tuple(plan if t.id == plan.id else t for t in p.tjansteplaner)
        if not any(t.id == plan.id for t in planer):
            planer = (*planer, plan)
        return spara_andring(self.mapp,self.rb,p.model_copy(update={'tjansteplaner':planer}),revision,lokalt_underlag=True)

    def spara_kombinationsgrupp(self, grupp, revision):
        from riskanalys.profil.forandringar import spara_andring
        p = self.profil()
        grupper = tuple(grupp if g.id == grupp.id else g for g in p.kombinationsgrupper)
        if not any(g.id == grupp.id for g in grupper):
            grupper = (*grupper, grupp)
        return spara_andring(self.mapp,self.rb,p.model_copy(update={'kombinationsgrupper':grupper}),revision,lokalt_underlag=True)

    def oversikt(self, profil=None):
        return tackning(self.rb,self.profil() if profil is None else profil)
