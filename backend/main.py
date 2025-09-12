from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import cockpitifié des routes
from api.routes import router as api_router

app = FastAPI(
    title="OliPLUS Cockpit API",
    description="Backend cockpitifié pour la plateforme OliPLUS",
    version="1.0.0",
)

# 🧭 Middleware CORS cockpitifié
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Inclusion des routes cockpitifiées
app.include_router(api_router)

# 🩺 Endpoint de santé cockpitifié
@app.get("/health")
def health_check():
    return {"status": "ok"}
