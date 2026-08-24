from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Read the configuration from .env
load_dotenv()
PORT = int(os.getenv("PORT", 5001))

app = Flask(__name__)
# Allow the frontend to call paths under /api/*
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# ----------------  Health Checkup ----------------
@app.get("/api/health")
def health():
    return {"ok": True, "service": "flask", "port": PORT}


# ---------------- Blueprints for each functional module ----------------

# IFC Blueprint
from ifc_service import bp as ifc_bp
app.register_blueprint(ifc_bp, url_prefix="/api/ifc")

# LLM Semantic Search Blueprint
try:
    from llm_semantic import bp as llm_bp
    app.register_blueprint(llm_bp, url_prefix="/api/llm")
except Exception as e:
    print(f"[warn] llm_semantic not loaded: {e}")

# DLCA Blueprint： dlca_service
import dlca_service
print("USING dlca_service:", getattr(dlca_service, "__file__", "<no __file__>"))

# 
try:
    import dlca_core
    print("USING dlca_core:", getattr(dlca_core, "__file__", "<no __file__>"))
except Exception as e:
    print("[warn] dlca_core not imported at app startup:", e)

from dlca_service import bp as dlca_bp
app.register_blueprint(dlca_bp, url_prefix="/api/dlca")


# Neo4j Blueprint
try:
    from neo4j_service import bp as neo4j_bp
    app.register_blueprint(neo4j_bp, url_prefix="/api/neo4j")
    print("USING neo4j_service")
except Exception as e:
    print(f"[warn] neo4j_service not loaded: {e}")

if __name__ == "__main__":
    print(f"ENV >> OLLAMA_HOST={os.getenv('OLLAMA_HOST')}  OLLAMA_MODEL={os.getenv('OLLAMA_MODEL')}")
    app.run(host="0.0.0.0", port=PORT, debug=True, use_reloader=False)