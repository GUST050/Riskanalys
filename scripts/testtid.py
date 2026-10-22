"""Summera befintlig JUnit; startar aldrig en ny testkörning."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def sammanstall(fil: Path) -> dict:
    data=fil.read_bytes();rot=ET.fromstring(data);prov=rot.findall('.//testcase')
    filer=defaultdict(float);rader=[]
    for p in prov:
        tid=float(p.get('time','0'));filnamn=p.get('classname','')
        filer[filnamn]+=tid
        rader.append({'prov':filnamn+'.'+p.get('name',''),'sekunder':tid})
    fel=sum(p.find('failure') is not None or p.find('error') is not None for p in prov)
    skippade=sum(p.find('skipped') is not None for p in prov)
    return dict(antal=len(prov),provtid_s=sum(filer.values()),per_fil=dict(sorted(filer.items(),key=lambda x:-x[1])),
        per_prov=sorted(rader,key=lambda x:-x['sekunder']),fel=fel,skippade=skippade,
        godkanda=len(prov)-fel-skippade,kalla_sha256=sha256(data).hexdigest())


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('junit',type=Path)
    a=p.parse_args(argv);print(json.dumps(sammanstall(a.junit),ensure_ascii=False,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
