"""
Page Trading Binance: KPI portefeuille + execution d'ordres manuels.
"""
import os
import sys
import pandas as pd
import streamlit as st

# Ajout du chemin parent pour l'importation des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.binance_client import BinanceClient, build_portfolio_kpis
from backend.config import get_secret
from frontend.auth import require_password
from frontend.ui import apply_custom_style


def _as_bool(value, default=False):
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _money(amount, quote_asset):
    return f"{amount:,.2f} {quote_asset}"


def _trading_config():
    api_key = get_secret("BINANCE_API_KEY", "")
    api_secret = get_secret("BINANCE_API_SECRET", "")
    testnet = _as_bool(get_secret("BINANCE_TESTNET", "false"), default=False)
    enable_live_trading = _as_bool(get_secret("BINANCE_ENABLE_LIVE_TRADING", "false"), default=False)
    quote_asset = (get_secret("BINANCE_QUOTE_ASSET", "USDT") or "USDT").upper()
    default_base_url = "https://testnet.binance.vision" if testnet else "https://api.binance.com"
    base_url = get_secret("BINANCE_BASE_URL", default_base_url) or default_base_url

    return {
        "api_key": api_key,
        "api_secret": api_secret,
        "testnet": testnet,
        "enable_live_trading": enable_live_trading,
        "quote_asset": quote_asset,
        "base_url": base_url,
    }


@st.cache_data(ttl=120)
def _load_trading_kpis(api_key, api_secret, base_url, quote_asset):
    client = BinanceClient(api_key=api_key, api_secret=api_secret, base_url=base_url, timeout=20)
    client.ping()
    return build_portfolio_kpis(client=client, quote_asset=quote_asset)


def _render_order_panel(config):
    st.markdown("### Execution d'ordres")
    if config["enable_live_trading"]:
        st.warning("Mode live actif: les ordres non-test seront reels.")
    else:
        st.info("Mode securise: les ordres reels sont bloques (BINANCE_ENABLE_LIVE_TRADING=false).")

    with st.form("order_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            symbol = st.text_input("Symbol", value=f"BTC{config['quote_asset']}").upper().strip()
            side = st.selectbox("Side", options=["BUY", "SELL"])
        with col2:
            order_type = st.selectbox("Type", options=["MARKET", "LIMIT"])
            quantity = st.number_input("Quantite (base asset)", min_value=0.0, value=0.001, step=0.001, format="%.8f")
        with col3:
            use_quote_order_qty = st.checkbox("BUY MARKET via montant quote", value=False)
            quote_order_qty = st.number_input(
                f"Montant ({config['quote_asset']})",
                min_value=0.0,
                value=50.0,
                step=10.0,
                format="%.2f",
                disabled=not (side == "BUY" and order_type == "MARKET" and use_quote_order_qty),
            )

        price = None
        if order_type == "LIMIT":
            price = st.number_input("Prix limite", min_value=0.0, value=0.0, step=0.01, format="%.8f")

        test_order = st.checkbox("Ordre test Binance (/order/test)", value=True)
        confirm = st.checkbox("Je confirme l'envoi de cet ordre", value=False)
        submit_order = st.form_submit_button("Envoyer ordre")

    if not submit_order:
        return
    if not confirm:
        st.error("Confirme l'ordre avant envoi.")
        return

    actual_test_order = test_order or (not config["enable_live_trading"])
    if (not test_order) and (not config["enable_live_trading"]):
        st.warning("Ordre reel bloque: passage automatique en mode test.")

    try:
        client = BinanceClient(
            api_key=config["api_key"],
            api_secret=config["api_secret"],
            base_url=config["base_url"],
            timeout=20,
        )
        if order_type == "MARKET" and side == "BUY" and use_quote_order_qty:
            response = client.create_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=None,
                quote_order_qty=quote_order_qty,
                test_order=actual_test_order,
            )
        else:
            response = client.create_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price if order_type == "LIMIT" else None,
                test_order=actual_test_order,
            )

        if actual_test_order:
            st.success("Ordre test envoye avec succes.")
        else:
            st.success("Ordre reel envoye avec succes.")
        st.json(response if response else {"status": "ok"})
        st.cache_data.clear()
    except Exception as exc:
        st.error(f"Erreur ordre Binance: {exc}")


def main():
    apply_custom_style()
    require_password()

    st.title("Trading")

    config = _trading_config()

    with st.sidebar:
        st.subheader("Trading")
        st.caption("Configuration runtime")
        st.write(f"Base URL: `{config['base_url']}`")
        st.write(f"Testnet: `{config['testnet']}`")
        st.write(f"Live trading: `{config['enable_live_trading']}`")
        if st.button("Rafraichir KPIs"):
            st.cache_data.clear()
            st.rerun()

    if not config["api_key"] or not config["api_secret"]:
        st.error("BINANCE_API_KEY / BINANCE_API_SECRET manquants dans Secrets/.env")
        st.stop()

    try:
        summary, rows = _load_trading_kpis(
            api_key=config["api_key"],
            api_secret=config["api_secret"],
            base_url=config["base_url"],
            quote_asset=config["quote_asset"],
        )
    except Exception as exc:
        st.error(f"Impossible de recuperer les KPIs Binance: {exc}")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valeur portefeuille", _money(summary["total_value"], summary["quote_asset"]))
    col2.metric("PnL latent", _money(summary["total_unrealized"], summary["quote_asset"]))
    col3.metric("PnL realise", _money(summary["total_realized"], summary["quote_asset"]))
    pct = summary["total_unrealized_pct"]
    col4.metric("Perf latente", f"{pct:.2f}%" if pct is not None else "N/A")

    st.markdown("### Positions")
    df = pd.DataFrame(rows)
    if not df.empty:
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "asset": st.column_config.TextColumn("Asset"),
                "symbol": st.column_config.TextColumn("Pair"),
                "free": st.column_config.NumberColumn("Free", format="%.8f"),
                "locked": st.column_config.NumberColumn("Locked", format="%.8f"),
                "total_qty": st.column_config.NumberColumn("Total", format="%.8f"),
                "current_price": st.column_config.NumberColumn("Prix", format="%.8f"),
                "current_value": st.column_config.NumberColumn("Valeur", format="%.2f"),
                "avg_buy_price": st.column_config.NumberColumn("Prix achat moyen", format="%.8f"),
                "cost_basis": st.column_config.NumberColumn("Cost basis", format="%.2f"),
                "unrealized_pnl": st.column_config.NumberColumn("PnL latent", format="%.2f"),
                "unrealized_pnl_pct": st.column_config.NumberColumn("PnL latent %", format="%.2f%%"),
                "realized_pnl": st.column_config.NumberColumn("PnL realise", format="%.2f"),
            },
        )
    else:
        st.info("Aucune position detectee sur le compte Binance.")

    _render_order_panel(config)

    st.markdown("### Roadmap")
    st.info(
        "LLM conseil: a integrer ensuite via OpenAI API (watchlist + scoring + explications).\n\n"
        "Bot auto-trade: a venir avec garde-fous (risk limits, max drawdown, paper mode, journal d'ordres)."
    )


if __name__ == "__main__":
    main()
