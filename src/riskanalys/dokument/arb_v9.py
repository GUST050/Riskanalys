"""Nytt presentationsformat från oförändrade V8-skrivresultat och analyskällor."""
from riskanalys.dokument.arb_v8 import bygg_arb_v8,HELHET
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.rapportversion import V9
from riskanalys.dokument.resultatmodell_v9 import (ResultatbyggeV9,TransformationV9,KonstruktionV9,
    kallartefakter,referens)
from riskanalys.dokument.resultatunderlag_v9 import bygg_resultatunderlag
from riskanalys.dokument.resultatrapport_v9 import bygg_resultatavsnitt

HELHET_V9 = ('Resultatrapport, bilaga A Analys och bilaga B1 Underlag utgör tillsammans fullständig '
             'dokumentation. Alla tre delarna ska granskas och fastställas i samma paket.')


def bygg_resultatpaket_v9(rb,profil,bedomning,resultat,historik,*,analys,gransindex=None,modellrapport=None):
    original=bygg_arb_v8(rb,profil,bedomning,resultat,historik,analys=analys,
                       gransindex=gransindex,modellrapport=modellrapport)
    underlag=bygg_resultatunderlag(rb,profil,bedomning,resultat,historik,analys=analys,analysdokument=original)
    huvud=bygg_resultatavsnitt(rb,profil,bedomning,resultat,historik,analys=analys,underlag=underlag)
    transformer, bilagor = [], []
    for n,a in enumerate(original.avsnitt):
        del_='underlagsbilaga' if a.leveransdel=='underlagsbilaga' else 'analysbilaga'
        nummer='B1' if a.id=='D-ARB.B1' else 'A15' if a.id=='D-ARB.B2' else 'A'+(a.visningsnummer or str(n+1))
        stycken=[]
        for j,s in enumerate(a.stycken):
            text=s.text
            radata=('Råa lokala svar: ordagranna kompletteringar och fältsökvägar. '
                    'Läsrapport och kompletterande underlagsbilaga utgör tillsammans hela riskbedömningens dokumentation.')
            if (a.id=='D-ARB.B1' and text==radata and s.proveniens=='lokal' and not s.literala_spann):
                efter='Råa lokala svar: ordagranna kompletteringar och fältsökvägar. '+HELHET_V9
                transformer.append(TransformationV9(pointer=f'/avsnitt/{n}/stycken/{j}/text',fore=text,efter=efter,orsak='tredelsforklaring'))
                s=s.model_copy(update={'text':efter})
            if (a.id in ('D-ARB.1','D-ARB.B2') and text == HELHET
                    and s.proveniens in (None,'regelbas') and not s.literala_spann):
                efter=text.replace(HELHET,HELHET_V9)
                transformer.append(TransformationV9(pointer=f'/avsnitt/{n}/stycken/{j}/text',
                    fore=text,efter=efter,orsak='tredelsforklaring'))
                s=s.model_copy(update={'text':efter})
            stycken.append(s)
        for f,fore,efter,orsak in (('formatversion',a.formatversion,V9,'format'),
            ('leveransdel',a.leveransdel,del_,'leveransdel'),('visningsnummer',a.visningsnummer,nummer,'visningsnummer')):
            transformer.append(TransformationV9(pointer=f'/avsnitt/{n}/{f}',fore=str(fore),efter=efter,orsak=orsak))
        bilagor.append(a.model_copy(update={'formatversion':V9,'leveransdel':del_,'visningsnummer':nummer,'stycken':tuple(stycken)}))
    dokument=Dokument.model_validate(Dokument(id='D-ARB',titel=original.titel,
                                   avsnitt=(*huvud,*bilagor)).model_dump(mode='json'))
    from riskanalys.dokument.rendering import renderat_avsnitt,synliga_texter
    huvudord=sum(len(x.split()) for a in huvud for x in synliga_texter(renderat_avsnitt(a,profil)))
    if huvudord>4000 or sum(a.id.startswith('D-ARB.R5.') for a in huvud)>4:
        from riskanalys.dokument.modeller import Textstycke
        varning=Textstycke(typ='beskrivning',proveniens='regelbas',text=(
            'Redaktionell längdvarning: fler tjänster eller långa originaltexter kan ge mer än åtta resultatsidor. '
            'Kontrollera sidantal och läsbarhet i Word/PDF; ingen text har kapats.'),
            referenser=['kalla:bedomning#','kalla:analys#'])
        a=dokument.avsnitt[0]
        dokument=dokument.model_copy(update={'avsnitt':(a.model_copy(update={'stycken':(*a.stycken,varning)}),*dokument.avsnitt[1:])})
        huvud=(dokument.avsnitt[0],*huvud[1:])
    kallor=kallartefakter(rb,profil,bedomning,resultat,historik,analys,original)
    konstruktioner=[]
    for a in huvud:
        positioner=[(f'{a.id}/stycken/{n}',s.referenser) for n,s in enumerate(a.stycken)]
        positioner.extend((f'{a.id}/tabeller/{t.id}/rader/{ri}/celler/{ci}',c.referenser)
                          for t in a.tabeller for ri,r in enumerate(t.rader) for ci,c in enumerate(r.celler))
        for pos,refs in positioner:
            k=[]
            for kod in refs:
                if kod.startswith('kalla:'):
                    art,ptr=kod.removeprefix('kalla:').split('#',1)
                    k.append(referens(kallor,art,ptr))
            konstruktioner.append(KonstruktionV9(placering=pos,mall='D-ARB-v9-konstruktion-1',kallor=tuple(k)))
    return ResultatbyggeV9(dokument=dokument,analysdokument=original,underlag=underlag,
                          transformationer=tuple(transformer),konstruktioner=tuple(konstruktioner))
