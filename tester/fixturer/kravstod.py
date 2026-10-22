"""Enbart syntetiskt jämförelseunderlag; ingen beslutad ny riskmetod."""
from riskanalys.profil.modeller import Tjansteplan, Kombinationsgrupp, Uppgift


def planerad_tjanst(rb, profil, tjanst='T-RED-02'):
    t=rb.tjanster[tjanst]; slug=t.erbjuds_falt.removesuffix('_erbjuds')
    mall=profil.uppgifter[t.erbjuds_falt]
    plan=Tjansteplan(id='planerad_tjanst',tjanst=tjanst,typ='ny_tjanst',
        beskrivning='Planerade bokslutsuppdrag för ägarledda bolag. Inget betalningsmandat; bankunderlag via kunden. Digital leverans inom Sverige.',
        uppgifter={slug+'_arbetssatt':Uppgift(varde='Planerade arbetsmoment: avstämning och bokslut; insyn genom lämnade handlingar.',status='föreslagen')})
    return profil.model_copy(update={'uppgifter':{**profil.uppgifter,t.erbjuds_falt:mall.model_copy(update={'varde':False})},'tjansteplaner':(plan,)})


def gruppvariant(rb, profil, variant):
    """Samma deklarerade marginaltal 8 X och 8 Y av 100 uppdrag; tre överlapp."""
    u=profil.uppgifter['P-KUND.antal_aktiva']
    ids=tuple(rb.tjanster['T-RED-01'].sarbarheter[:2])
    def grupp(id, sarbarheter, antal, beskrivning):
        return Kombinationsgrupp(id=id,tjanst='T-RED-01',population='uppdrag',
            avgransning='100 löpande uppdrag under samma period; X=8 och Y=8 enligt syntetisk sammanställning.',
            beskrivning=beskrivning,sarbarheter=sarbarheter,antal=u.model_copy(update={'varde':antal}) if antal is not None else Uppgift(),
            bas=u.model_copy(update={'varde':100}))
    grupper={
        'samtidig':(grupp('bada',ids,8,'Samma åtta uppdrag har både X och Y enligt gemensamt underlag.'),),
        'atskild':(grupp('bara_x',ids[:1],8,'Endast X; belagt åtskild från Y-gruppen.'),grupp('bara_y',ids[1:],8,'Endast Y; belagt åtskild från X-gruppen.')),
        'okand':(grupp('okant_overlapp',ids,None,'Marginaltalen är kända men överlappet är okänt. Ingen belagd kombination.'),),
    }[variant]
    return profil.model_copy(update={'kombinationsgrupper':grupper})
