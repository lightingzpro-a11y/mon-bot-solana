import os
import threading
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Config depuis variables d'environnement (à configurer dans Railway)
SHEETDB_API_URL = os.getenv("SHEETDB_API_URL")  # Pour debug, pas forcément utilisé ici
SOLANA_RPC = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
SECRET_KEY_BASE58 = os.getenv("SECRET_KEY_BASE58")  # TA CLÉ PRIVÉE doit être ici, NE PAS COMMITER EN DUR

TP_PERCENT = 20.0  # Take profit en %
SL_PERCENT = 20.0  # Stop loss en %
BUY_AMOUNT = 0.1   # Montant fixe à acheter (en SOL ou token, selon implémentation)

active_trades = set()
lock = threading.Lock()

def log(*args, **kwargs):
    print("[BOT]", *args, **kwargs)

# --- Fonctions simulées d'interaction avec la blockchain Solana ---
def buy_token(token_mint):
    """
    Simulation achat d'un token pour 0.1 unité.
    Remplacer cette fonction par appel réel à ton wallet/DEX.
    """
    log(f"Achat simulé de {BUY_AMOUNT} sur token {token_mint} avec clé privée {SECRET_KEY_BASE58[:6]}... (cachée)")
    fake_buy_price = get_token_price(token_mint)
    if fake_buy_price is None:
        log("Erreur: Impossible de récupérer le prix pour achat")
        return None
    return fake_buy_price

def get_token_price(token_mint):
    """
    Simulation récupération du prix token.
    À remplacer par appel API réelle (ex: CoinGecko, Serum, etc.).
    """
    # Ici on simule un prix fixe pour l'exemple
    return 1.0

def sell_token(token_mint):
    """
    Simulation vente du token.
    Remplacer par call réel à la blockchain.
    """
    log(f"Vente simulée du token {token_mint}")

# --- Monitoring d'une position ---
def monitor_trade(token_mint, buy_price):
    log(f"Démarrage du suivi pour {token_mint} à prix d'achat {buy_price}")
    try:
        while True:
            time.sleep(1)  # Vérifie toutes les secondes
            current_price = get_token_price(token_mint)
            if current_price is None:
                log(f"Impossible d'obtenir le prix actuel de {token_mint}, tentative suivante...")
                continue

            change_pct = (current_price - buy_price) / buy_price * 100
            log(f"Prix {token_mint}: {current_price} (changement {change_pct:.2f}%)")

            if change_pct >= TP_PERCENT:
                log(f"Take Profit atteint (+{change_pct:.2f}%), vente de {token_mint}")
                sell_token(token_mint)
                break

            if change_pct <= -SL_PERCENT:
                log(f"Stop Loss atteint ({change_pct:.2f}%), vente de {token_mint}")
                sell_token(token_mint)
                break
    except Exception as e:
        log(f"Erreur dans le suivi de {token_mint}: {e}")
    finally:
        with lock:
            active_trades.discard(token_mint)
        log(f"Suivi terminé pour {token_mint}")

# --- Endpoint webhook pour recevoir tokens ---
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json(silent=True)
        if not payload:
            log("Pas de payload JSON reçu")
            return jsonify({"error": "No JSON payload"}), 400

        log("Webhook reçu:", payload)
        items = payload.get("data") or []

        for item in items:
            token = item.get("token") or item.get("Token") or item.get("address")
            if not token:
                continue
            token = token.strip()

            with lock:
                if token in active_trades:
                    log(f"{token} est déjà en cours de trade, on skip.")
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
        log(f"Erreur dans webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    log(f"Démarrage du serveur sur le port {port}")
    app.run(host="0.0.0.0", port=port)
