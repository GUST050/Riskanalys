"""V9 prövas mot full V8-analys och en återbyggd spårbar presentation."""
from riskanalys.dokument.resultatmodell_v9 import kallartefakter,los_referens
from riskanalys.dokument.resultatunderlag_v9 import bygg_resultatunderlag
from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9

# Presentationens väg till den oförändrade kravkartan i analysen.
KRAVKARTA={
 'D-ARB.1':('D-ARB.R1','D-ARB.R3'), 'D-ARB.2':('D-ARB.R3',),
 'D-ARB.3':('D-ARB.R2','D-ARB.R3'), 'D-ARB.4':('D-ARB.R4',),
 'D-ARB.5':('D-ARB.R4',), 'D-ARB.6':('D-ARB.R5',),
 'D-ARB.7':('D-ARB.R5','D-ARB.R6'), 'D-ARB.8':('D-ARB.R2','D-ARB.R5'),
 'D-ARB.9':('D-ARB.R6',), 'D-ARB.10':('D-ARB.R7',), 'D-ARB.11':('D-ARB.R7',)}


def resultatfynd_v9(rb,profil,bedomning,resultat,historik,*,analys,bygge,dokument,
                    modellrapport=None,analysbrister_filer=(),granskningsdatum=None):
    fynd=[]
    def lagg(id,text):
        fynd.append(dict(typ='tackning',allvar='blockerande',grund='metodval',avsnitt=id,
            beskrivning=text,atgard='Komplettera underlaget och granska hela resultatrapporten med bilagor på nytt.'))
    for brist in bygge.underlag.brister:lagg(brist.avsnitt,brist.beskrivning)
    expected=bygge.dokument;actual=dokument.avsnitt_med_id()
    if (dokument.titel,dokument.formatversion,tuple(actual))!=(expected.titel,expected.formatversion,tuple(a.id for a in expected.avsnitt)):
        lagg('D-ARB','V9-dokumentets titel, format eller ordning avviker från återbyggnaden.')
    for a in expected.avsnitt:
        if actual.get(a.id)!=a:lagg(a.id,'Text, tabeller, nivåer, åtgärdsstatus eller placering avviker från V9-källan.')
    kallor=kallartefakter(rb,profil,bedomning,resultat,historik,analys,bygge.analysdokument)
    refs=[r for p in bygge.underlag.poster for r in p.kallor]
    refs.extend(r for b in bygge.underlag.brister for r in b.kallor)
    refs.extend(r for k in bygge.konstruktioner for r in k.kallor)
    refs.extend(r for row in bygge.underlag.matris for r in (*row.mekanismkallor,*(r for c in row.celler for r in c.kallor)))
    for r in refs:
        try:los_referens(kallor,r)
        except ValueError as exc:lagg('D-ARB',str(exc))
    underlag=bygg_resultatunderlag(rb,profil,bedomning,resultat,historik,analys=analys,analysdokument=bygge.analysdokument)
    if underlag!=bygge.underlag:lagg('D-ARB.R4','Urval, matris, medlemskap eller källsummor avviker från analysen.')
    for rad in kravkarta_v9(rb,profil,bedomning,bygge):
        if not rad['analys'] or not rad['sammanfattning']:
            lagg('D-ARB','Kravkartan saknar analys eller R-sammanfattning för '+rad['krav'])
    return fynd


def kravkarta_v9(rb,profil,bedomning,bygge):
    """Tillämpligt krav-ID → verkliga analys-/R-avsnitt och fulla belägg i B1."""
    from riskanalys.dokument.omfattning import krav_for_dokument,dokumentmal
    from riskanalys.regelverk.urval import valj
    from riskanalys.dokument.resultatmodell_v9 import referens
    u=valj(rb,bedomning.regelpaket,bedomning.datum,bedomning.lan)
    original=bygge.analysdokument.model_dump(mode='json');k={'analysdokument':original}
    r=[]
    for valt in krav_for_dokument(rb,u,profil,'D-ARB'):
        for mal in dokumentmal(valt.krav,'D-ARB'):
            analyser=[(i,a) for i,a in enumerate(bygge.analysdokument.avsnitt) if a.id==mal or a.id.startswith(mal+'.')]
            samman=[a.id for a in bygge.dokument.avsnitt if any(a.id==x or a.id.startswith(x+'.') for x in KRAVKARTA.get(mal,()))]
            r.append({'krav':valt.krav.id,'mal':mal,'analys':[a.id for _,a in analyser],
                'sammanfattning':samman,'underlag':['D-ARB.B1'],
                'kallor':[referens(k,'analysdokument',f'/avsnitt/{i}').model_dump(mode='json') for i,_ in analyser]})
    return r
