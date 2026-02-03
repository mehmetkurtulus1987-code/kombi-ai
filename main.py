from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Soru(BaseModel):
    belirti: str

@app.get("/")
def root():
    return {"status": "Kombi AI çalışıyor"}

@app.post("/teshis")
def teshis(soru: Soru):
    if "sıcak su" in soru.belirti.lower() and "petek" in soru.belirti.lower():
        return {
            "olasi_nedenler": [
                "Üç yollu vana sıkışmış olabilir",
                "Plakalı eşanjör kaçırıyor olabilir"
            ],
            "ilk_kontrol": "Üç yollu vana motoru ve hareketi kontrol edilmeli"
        }

    return {
        "mesaj": "Bu belirti için henüz veri yok"
    }
