from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

with open("ariza_tablosu.json", "r", encoding="utf-8") as f:
    ARIZA_DB = json.load(f)

class Soru(BaseModel):
    belirti: str

@app.get("/")
def root():
    return {"status": "Kombi AI çalışıyor"}

@app.post("/teshis")
def teshis(soru: Soru):
    sonuc = []

    for ariza in ARIZA_DB:
        for b in ariza["belirtiler"]:
            if b.lower() in soru.belirti.lower():
                sonuc.append({
                    "ariza": ariza["ariza"],
                    "olasi_sebepler": ariza["olasi_sebepler"],
                    "ilk_kontrol": ariza["ilk_kontrol"],
                    "puan": ariza["puan"]
                })

    if not sonuc:
        return {"mesaj": "Bu belirti için kayıtlı arıza yok"}

    sonuc = sorted(sonuc, key=lambda x: x["puan"], reverse=True)
    return sonuc
