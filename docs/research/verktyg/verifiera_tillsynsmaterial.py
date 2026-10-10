"""Kontrollerar granskningsfall och, valfritt, det lokala källarkivet. Bedömer inte programmet."""

import argparse
import hashlib
import json
import re
from pathlib import Path


RESEARCH = Path(__file__).resolve().parents[1]


def krav(villkor, meddelande):
    if not villkor:
        raise ValueError(meddelande)


def las_json(fil):
    return json.loads(fil.read_text(encoding="utf-8"))


def saker_fil(rot, relativ):
    fil = (rot / relativ).resolve()
    krav(fil.is_relative_to(rot.resolve()), "Filreferens utanför underlagsmappen.")
    krav(fil.is_file(), f"Fil saknas: {relativ}")
    return fil


def kontrollera_fall(data):
    krav(data["schema_version"] == 1, "Okänd version av fallformatet.")
    krav(data["status"] == "facitutkast_ej_sakkunniggranskat", "Facitets granskningsstatus måste prövas separat.")
    krav(data["utvarderingsstatus"] == "ej_kord", "Detta verktyg bekräftar inte körda produktutvärderingar.")
    monster = set(re.findall(r"B-\d{2}", (RESEARCH / "03-tillsyn-och-sanktioner.md").read_text()))
    dokument = {post["id"]: post["sidor"] for post in data["dokumentkarta"]}
    krav(len(dokument) == len(data["dokumentkarta"]), "Dubbletter i dokumentkartan.")
    fall_id, fynd_id = set(), set()
    for fall in data["fall"]:
        krav(fall["id"] not in fall_id, "Dubblett av fall-ID.")
        fall_id.add(fall["id"])
        krav(fall["indata_typ"] == "syntetisk_omskrivning", "Testindata måste vara syntetiska.")
        krav(bool(fall["indata"]["riskbedomning"]), "Riskbedömning saknas i testindata.")
        for fynd in fall["forvantade_fynd"]:
            krav(fynd["id"] not in fynd_id, "Dubblett av fynd-ID.")
            fynd_id.add(fynd["id"])
            krav(fynd["omrade"] in {"allman_riskbedomning", "rutiner"}, "Okänd granskningsomfattning.")
            krav(fynd["ska_hittas"] is True, "Förväntade fynd måste ha uttryckligt klarkriterium.")
            krav(bool(fynd["bristmonster"]) and set(fynd["bristmonster"]) <= monster, "Okänt bristmönster.")
            krav(bool(fynd["observation"]) and bool(fynd["forvantad_atgard"]), "Förklaring eller åtgärd saknas.")
            krav(bool(fynd["belagg"]), "Belägg saknas.")
            for belagg in fynd["belagg"]:
                krav(belagg["dokument"] in dokument, "Okänd dokumentreferens.")
                krav(bool(belagg["sidor"]), "Sidhänvisning saknas.")
                krav(all(type(s) is int and 1 <= s <= dokument[belagg["dokument"]] for s in belagg["sidor"]),
                     "Sidhänvisning utanför dokumentet.")
    varianter = data["kontrollvarianter"]
    krav(len({v["id"] for v in varianter}) == len(varianter), "Dubblett av kontrollvariant.")
    krav(all(v["fall"] in fall_id and v["andring"] and v["forvantat"] for v in varianter),
         "Kontrollvariant saknar fall, ändring eller förväntat utfall.")
    return len(fall_id), len(fynd_id), len(varianter)


def kontrollera_arkiv(rot, data):
    manifest = las_json(rot / "manifest.json")
    krav(manifest["schema_version"] == 1, "Okänd manifestversion.")
    for relativ, vantad in manifest["filer"].items():
        aktuell = "sha256:" + hashlib.sha256(saker_fil(rot, relativ).read_bytes()).hexdigest()
        krav(aktuell == vantad, f"Kontrollsumma stämmer inte: {relativ}")
    dokument = {d["id"]: d for d in manifest["dokument"]}
    krav(len(dokument) == len(manifest["dokument"]), "Dubblett av dokument-ID i arkivet.")
    original, ocr = [], []
    for doc in dokument.values():
        krav([p["sida"] for p in doc["sidor"]] == list(range(1, len(doc["sidor"]) + 1)),
             "Dokumentets sidföljd är ofullständig.")
        krav(doc["sammanstalld_ocr"] in manifest["filer"], "Sammanställd OCR saknar kontrollsumma.")
        for page in doc["sidor"]:
            for typ in ("original", "ocr"):
                krav(page[typ] in manifest["filer"], "Sida saknar kontrollsumma.")
            original.append(page["original"])
            ocr.append(page["ocr"])
    krav(len(set(original)) == len(original) == 79, "Originalen ska vara 79 unika sidor.")
    krav(len(set(ocr)) == len(ocr) == 79, "OCR-filerna ska vara 79 unika sidor.")
    krav(set(original) == {p for p in manifest["filer"] if p.startswith("original/")},
         "Original finns utanför dokumentkartan.")
    for doc in data["dokumentkarta"]:
        krav(doc["id"] in dokument and len(dokument[doc["id"]]["sidor"]) == doc["sidor"],
             "Testfallens dokumentkarta stämmer inte med källarkivet.")
    return len(dokument), len(original), len(manifest["filer"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fall", type=Path, default=RESEARCH / "typfall/tillsyn-2026.json")
    parser.add_argument("--underlag", type=Path, help="Lokalt arkiv med manifest.json; råtext skrivs inte ut.")
    args = parser.parse_args()
    try:
        data = las_json(args.fall)
        fall, fynd, varianter = kontrollera_fall(data)
        print(f"Fallformat OK: {fall} fall, {fynd} förväntade fynd, {varianter} kontrollvarianter.")
        if args.underlag:
            dokument, sidor, filer = kontrollera_arkiv(args.underlag, data)
            print(f"Källarkiv OK: {dokument} dokument, {sidor} original, {filer} kontrollsummor.")
        else:
            print("Källarkivet ej kontrollerat; ange --underlag för kontroll mot original och OCR.")
        print("Facit är ej sakkunniggranskat. Programmets granskningsförmåga är ej utvärderad av detta verktyg.")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as fel:
        print(f"Fel: {fel}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
