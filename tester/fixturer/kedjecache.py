"""Klona läsklara syntetiska kedjor; aldrig ett muterbart delat byråregister."""
from dataclasses import replace
from pathlib import Path
import shutil
from tester.fixturer.analys_hela_kedjan import BundenKedja


def klona_kedja(bas: BundenKedja, rot: Path) -> BundenKedja:
    rot=rot.resolve();source=bas.fall.byramapp.resolve()
    if rot.is_relative_to(source) or rot.is_relative_to(bas.regelrot.resolve()):
        raise ValueError('Klonens mapp måste ligga utanför originalet.')
    for trad in (source,bas.regelrot):
        if any(p.is_symlink() for p in trad.rglob('*')):
            raise ValueError('Testbasen får inte innehålla symlänk till privat underlag.')
    byra=rot/'byra';regelrot=rot/'regelbas'
    shutil.copytree(source,byra);shutil.copytree(bas.regelrot,regelrot)
    return replace(bas,fall=replace(bas.fall,byramapp=byra),regelrot=regelrot,
        bedomningsmapp=byra/bas.bedomningsmapp.relative_to(source),
        utkastmapp=byra/bas.utkastmapp.relative_to(source),
        granskningsmapp=byra/bas.granskningsmapp.relative_to(source))
