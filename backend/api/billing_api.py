# 💳 billing_api.py — API de facturation cockpitifiée
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

class Invoice(BaseModel):
    client: str
    amount: float

@app.post("/api/billing")
async def create_invoice(invoice: Invoice):
    # 🔐 Logique cockpitifiée : validation + enregistrement fictif
    if invoice.amount <= 0:
        return JSONResponse(status_code=400, content={"message": "Montant invalide"})
    
    # Simuler l’enregistrement
    print(f"Facture enregistrée : {invoice.client} - {invoice.amount}€")
    return {"message": f"Facture envoyée à {invoice.client} pour {invoice.amount}€"}
