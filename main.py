from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

with open("ariza_tablosu.json", encoding="utf-8") as f:
    ARIZA_DB = {a["id"]: a for a in json.load(f)}

with open("soru_akisi.json", encoding="utf-8") as f:
    SORU_AKISI = json.load(f)

OTURUMLAR = {}

class Basla(BaseModel):
    belirti: str
    kullanici_id: str

class Cevap(BaseModel):
    kullanici_id: str
    cevap: str

@app.post("/basla")
def basla(data: Basla):
    akisi = SORU_AKISI["basinc"]

    OTURUMLAR[data.kullanici_id] = {
        "puanlar": {},
        "soru": akisi["ilk_soru"],
        "akisi": akisi
    }

    return {
        "soru": akisi["ilk_soru"],
        "butonlar": ["Evet", "Hayır"]
    }

@app.post("/cevap")
def cevapla(data: Cevap):
    oturum = OTURUMLAR.get(data.kullanici_id)
    if not oturum:
        return {"hata": "Oturum bulunamadı"}

    soru = oturum["soru"]
    secim = data.cevap
    adim = oturum["akisi"]["sorular"][soru][secim]

    for ariza_id, puan in adim.get("puan", {}).items():
        oturum["puanlar"][ariza_id] = oturum["puanlar"].get(ariza_id, 0) + puan

    if adim.get("bitir"):
        sonuc = sorted(
            oturum["puanlar"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        if not sonuc:
            return {"sonuc": "Net arıza tespit edilemedi"}

        ariza = ARIZA_DB[sonuc[0][0]]
        return {
            "teshis": ariza["ariza"],
            "olasi_sebepler": ariza["olasi_sebepler"],
            "ilk_kontrol": ariza["ilk_kontrol"]
        }

    oturum["soru"] = adim["sonraki_soru"]
    return {
        "soru": adim["sonraki_soru"],
        "butonlar": ["Evet", "Hayır"]
    }
