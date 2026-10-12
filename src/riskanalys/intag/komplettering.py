"""Koppla även beräknade/äldre AI-referenser till intagets grundfrågor."""


def fragefalt(rb, id: str) -> tuple[str, ...]:
    funna=[]
    besokta=set()
    def besok(id):
        if id in besokta:return
        besokta.add(id)
        f=rb.falt.get(id)
        if not f:return
        if f.alias_for:besok(f.alias_for)
        elif f.basfalt:
            besok(f.antalfalt);besok(f.basfalt)
        elif f.intag:funna.append(id)
    besok(id)
    return tuple(funna)
