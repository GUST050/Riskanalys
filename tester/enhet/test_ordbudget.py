from riskanalys.dokument.modeller import Avsnitt, Dokument, Textstycke, Dokumenttabell, Tabellrad, Tabellcell
from riskanalys.dokument.matning import dokumentord

def test_ordbudget_raknar_celler_och_bilaga_separat(minimal_regelbas,profil_fabrik):
    p=profil_fabrik(minimal_regelbas,{})
    a=Avsnitt(id='D-ARB.1',rubrik='Huvudtext',kalla='regelbas',stycken=(),formatversion='D-ARB-tjanst-v5',
       tabeller=(Dokumenttabell(id='TAB',rubrik='Tabell',kolumner=('Kolumn',),rader=(Tabellrad(celler=(Tabellcell(text='två ord'),)),),fore_stycke=0),))
    b=Avsnitt(id='D-ARB.B1',rubrik='Bilaga',kalla='regelbas',stycken=(Textstycke(typ='beskrivning',text='tre små ord',referenser=[]),))
    d=Dokument(id='D-ARB',titel='Titel',avsnitt=(a,b))
    counts=dokumentord(d,p)
    assert counts['huvudtext']==7 # titel + 1 Huvudtext + Tabell + Kolumn + två ord
    assert counts['bilaga']==5 # B1 Bilaga + tre små ord
    assert counts['totalt']==12


def test_langdvarning_bevarar_text_och_utelamnar_bilaga(minimal_regelbas,profil_fabrik):
    from riskanalys.dokument.matning import med_langdvarning
    p=profil_fabrik(minimal_regelbas,{})
    text='underlag '*5001
    a=Avsnitt(id='D-ARB.1',rubrik='Huvudtext',kalla='regelbas',
      stycken=(Textstycke(typ='beskrivning',text=text,referenser=[]),),formatversion='D-ARB-tjanst-v5')
    d=Dokument(id='D-ARB',titel='Titel',avsnitt=(a,))
    ny=med_langdvarning(d,p)
    assert ny.avsnitt[0].stycken[0].text==text
    assert 'Redaktionell längdvarning' in ny.avsnitt[0].stycken[-1].text
    assert med_langdvarning(ny,p)==ny


def test_langdvarning_tar_inte_bort_byrans_text(minimal_regelbas,profil_fabrik):
    from riskanalys.dokument.matning import med_langdvarning
    p=profil_fabrik(minimal_regelbas,{})
    text='Redaktionell längdvarning: denna synpunkt kommer från byrån.'
    a=Avsnitt(id='D-ARB.1',rubrik='Text',kalla='regelbas',stycken=(Textstycke(typ='beskrivning',text=text,referenser=['P-A']),))
    d=Dokument(id='D-ARB',titel='Titel',avsnitt=(a,))
    assert med_langdvarning(d,p)==d
