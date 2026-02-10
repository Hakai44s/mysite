"""
Daily zakat check for GitHub Actions.
Sends an email only when the app decides zakat is due ("Paye").
"""
from datetime import datetime, timezone
import os
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.crypto_data import is_mock_data_used, update_data
from backend.notifier import send_email_alert
from backend.utils import save_crypto_balance
from backend.zakat import calcul_zakat


def main():
    total, token_balance, token_price, token_mc, gold_price = update_data()

    if is_mock_data_used():
        print("Mock data in use. Skip alert to avoid false positives.")
        return 0

    current_time = save_crypto_balance(token_balance)
    gold_price, zakat_amount, msg, counter = calcul_zakat(total, gold_price)

    print(
        "Computed zakat status:",
        {
            "msg": msg,
            "days_passed": counter,
            "total_usd": round(float(total), 2),
            "zakat_usd": float(zakat_amount),
            "timestamp": current_time,
        },
    )

    if msg != "Paye":
        print("Zakat not due today. No email sent.")
        return 0

    subject = f"[Zakat Alert] Paiement recommande - {datetime.now(timezone.utc).date()}"
    body = (
        "Le moment de payer la zakat est arrive.\n\n"
        f"Date calcul: {current_time}\n"
        f"Total portefeuille (USD): {float(total):,.2f}\n"
        f"Montant zakat (USD): {float(zakat_amount):,.2f}\n"
        f"Jours ecoules depuis le seuil: {counter}\n"
        f"Prix de l'or (USD): {float(gold_price):,.2f}\n\n"
        "Ceci est une alerte automatique GitHub Actions."
    )

    sent, info = send_email_alert(subject, body)
    print(info)
    return 0 if sent else 1


if __name__ == "__main__":
    raise SystemExit(main())
