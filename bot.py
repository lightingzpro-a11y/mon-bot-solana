import os
import threading
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Config depuis variables d'environnement (à set dans Railway)
SHEETDB_API_URL = os.getenv("SHEETDB_API_URL")  # tu peux garder pour debug
SOLANA_RPC = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
SECRET_KEY_BASE58 = os.getenv("SECRET_KEY_BASE58")  # NE PAS COMMITER la clé en dur
TP_PERCENT = float(os.getenv("TP_PERCENT", "20"))  # take profit %
SL_PERCENT = float(os.getenv("SL_PERCENT", "20"))  # stop loss % (valeur positive)

# Etat en mémoire (évite de traiter 2x le même token)
active_trades = set()
lock = threading.Lock()

def log(*args, **kwargs):
    print("[BOT]", *args, **kwargs)

# ---------- Placeholders d'intégration trading ----------
def buy_token(token_mint):
    log(f"(SIMUL) Achat du token {token_mint}")
    fake_buy_price = 1.0  # remplacer par prix réel
    return fake_buy_price

def get_token_price(token_mint):
    # TODO: appeler une API réelle
    return 1.0  # simulation

def sell_token(token_mint):
    log(f"(SIMUL) Vente du token {token_mint}")

# ---------- Monitoring d'une position ----------
def monitor_trade(token_mint, buy_price):
    log(f"Lancement monitoring pour {token_mint} (buy_price={buy_price})")
    try:
        while True:
            time.sleep(15)
            current = get_token_price(token_mint)
            if current is None:
                log("Impossible d'obtenir le prix, on réessaie...")
                continue
            change_pct = (current - buy_price) / buy_price * 100.0
            log(f"{token_mint} price={current} change={change_pct:.2f}%")

            if change_pct >= TP_PERCENT:
                log(f"TP atteint ({change_pct:.2f}%), vente {token_mint}")
                sell_token(token_mint)
                break
            if change_pct <= -SL_PERCENT:
                log(f"SL atteint ({change_pct:.2f}%), vente {token_mint}")
                sell_token(token_mint)
                break
    except Exception as e:
        log("Erreur dans monitoring:", e)
    finally:
        with lock:
            active_trades.discard(token_mint)
        log(f"Monitoring terminé pour {token_mint}")

# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json(silent=True)
        if not payload:
            log("Aucun JSON reçu dans la requête")
            return jsonify({"error": "No JSON payload"}), 400
        
        log("Webhook reçu:", payload)
        # SheetDB envoie {"data":[{"token":"..."}], ...}
        items = payload.get("data") or []
        for item in items:
            token = item.get("token") or item.get("Token") or item.get("address")
            if not token:
                continue
            token = token.strip()
            with lock:
                if token in active_trades:
                    log(f"{token} déjà en cours, skip.")
                    continue
                active_trades.add(token)

            buy_price = buy_token(token)
            if buy_price is None:
                log(f"Achat échoué pour {token}")
                with lock:
                    active_trades.discard(token)
                continue

            t = threading.Thread(target=monitor_trade, args=(token, buy_price), daemon=True)
            t.start()
            log(f"Trade lancé pour {token}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        log("Erreur webhook:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    log("Démarrage app sur port", port)
    app.run(host="0.0.0.0", port=port)
