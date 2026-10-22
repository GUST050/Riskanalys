"""Stabilt skrivsvarsunderlag för jämförelser; bara anropens klockslag undantas."""


def frysta_skrivsvar(resultat):
    undanta={'delar':{'__all__':{'forsok':{'__all__':{'anrop':{'tidpunkt'}}}}}}
    return {id:r.model_dump(mode='json',exclude=undanta) for id,r in resultat.items()}
