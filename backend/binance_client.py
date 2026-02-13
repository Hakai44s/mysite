"""
Binance Spot API client + portfolio KPI helpers.
"""
import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests


class BinanceClient:
    def __init__(self, api_key, api_secret, base_url="https://api.binance.com", timeout=15):
        self.api_key = (api_key or "").strip()
        self.api_secret = (api_secret or "").strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _signed_params(self, params):
        params = dict(params or {})
        params["timestamp"] = int(time.time() * 1000)
        params.setdefault("recvWindow", 10000)
        query = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method, path, params=None, signed=False):
        url = f"{self.base_url}{path}"
        headers = {}
        request_params = dict(params or {})

        if signed:
            if not self.api_key or not self.api_secret:
                raise RuntimeError("BINANCE_API_KEY/BINANCE_API_SECRET manquants.")
            headers["X-MBX-APIKEY"] = self.api_key
            request_params = self._signed_params(request_params)

        response = requests.request(
            method=method.upper(),
            url=url,
            params=request_params,
            headers=headers,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Binance HTTP {response.status_code}: {response.text}")
        try:
            data = response.json()
        except Exception as exc:
            raise RuntimeError(f"Reponse Binance invalide: {response.text}") from exc
        if isinstance(data, dict) and "code" in data and "msg" in data and int(data["code"]) < 0:
            raise RuntimeError(f"Binance error {data['code']}: {data['msg']}")
        return data

    def ping(self):
        return self._request("GET", "/api/v3/ping")

    def get_account(self):
        return self._request("GET", "/api/v3/account", signed=True)

    def get_symbol_price(self, symbol):
        data = self._request("GET", "/api/v3/ticker/price", params={"symbol": symbol.upper()})
        return float(data["price"])

    def get_my_trades(self, symbol, limit=1000):
        return self._request(
            "GET",
            "/api/v3/myTrades",
            params={"symbol": symbol.upper(), "limit": int(limit)},
            signed=True,
        )

    def create_order(
        self,
        symbol,
        side,
        order_type,
        quantity=None,
        quote_order_qty=None,
        price=None,
        time_in_force="GTC",
        test_order=True,
    ):
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
        }
        if quantity is not None:
            params["quantity"] = quantity
        if quote_order_qty is not None:
            params["quoteOrderQty"] = quote_order_qty
        if params["type"] == "LIMIT":
            if price is None:
                raise RuntimeError("Le prix est obligatoire pour un ordre LIMIT.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        endpoint = "/api/v3/order/test" if test_order else "/api/v3/order"
        return self._request("POST", endpoint, params=params, signed=True)


def _compute_trade_kpis(trades, current_qty, current_price):
    """
    Approximation du prix moyen d'achat + PnL a partir de l'historique trades.
    """
    if not trades:
        return {
            "avg_buy_price": None,
            "cost_basis": 0.0,
            "unrealized_pnl": 0.0,
            "unrealized_pnl_pct": None,
            "realized_pnl": 0.0,
        }

    trades_sorted = sorted(trades, key=lambda t: int(t.get("time", 0)))
    position_qty = 0.0
    position_cost = 0.0
    realized_pnl = 0.0

    for t in trades_sorted:
        qty = float(t.get("qty", 0.0))
        price = float(t.get("price", 0.0))
        is_buyer = bool(t.get("isBuyer", False))
        if qty <= 0 or price <= 0:
            continue
        if is_buyer:
            position_qty += qty
            position_cost += qty * price
            continue

        if position_qty <= 0:
            continue
        sold_qty = min(qty, position_qty)
        avg_cost = position_cost / position_qty if position_qty > 0 else 0.0
        realized_pnl += sold_qty * (price - avg_cost)
        position_qty -= sold_qty
        position_cost -= sold_qty * avg_cost
        if position_qty <= 1e-12:
            position_qty = 0.0
            position_cost = 0.0

    avg_buy_price = (position_cost / position_qty) if position_qty > 0 else None
    if avg_buy_price is None:
        return {
            "avg_buy_price": None,
            "cost_basis": 0.0,
            "unrealized_pnl": 0.0,
            "unrealized_pnl_pct": None,
            "realized_pnl": realized_pnl,
        }

    cost_basis = current_qty * avg_buy_price
    unrealized_pnl = (current_price - avg_buy_price) * current_qty
    unrealized_pnl_pct = ((current_price / avg_buy_price) - 1.0) * 100 if avg_buy_price > 0 else None
    return {
        "avg_buy_price": avg_buy_price,
        "cost_basis": cost_basis,
        "unrealized_pnl": unrealized_pnl,
        "unrealized_pnl_pct": unrealized_pnl_pct,
        "realized_pnl": realized_pnl,
    }


def build_portfolio_kpis(client, quote_asset="USDT"):
    account = client.get_account()
    balances = account.get("balances", [])
    rows = []
    quote_asset = quote_asset.upper()

    for balance in balances:
        asset = balance.get("asset", "").upper()
        free = float(balance.get("free", 0.0))
        locked = float(balance.get("locked", 0.0))
        total_qty = free + locked
        if total_qty <= 0:
            continue

        symbol = f"{asset}{quote_asset}"
        if asset == quote_asset:
            current_price = 1.0
            symbol = quote_asset
            trades = []
        else:
            try:
                current_price = client.get_symbol_price(symbol)
            except Exception:
                current_price = None
            trades = []
            if current_price is not None:
                try:
                    trades = client.get_my_trades(symbol=symbol, limit=1000)
                except Exception:
                    trades = []

        current_value = total_qty * current_price if current_price is not None else 0.0
        trade_kpis = _compute_trade_kpis(
            trades=trades,
            current_qty=total_qty,
            current_price=current_price or 0.0,
        )

        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "free": free,
                "locked": locked,
                "total_qty": total_qty,
                "current_price": current_price,
                "current_value": current_value,
                "avg_buy_price": trade_kpis["avg_buy_price"],
                "cost_basis": trade_kpis["cost_basis"],
                "unrealized_pnl": trade_kpis["unrealized_pnl"],
                "unrealized_pnl_pct": trade_kpis["unrealized_pnl_pct"],
                "realized_pnl": trade_kpis["realized_pnl"],
            }
        )

    total_value = sum(r["current_value"] for r in rows)
    total_cost = sum(r["cost_basis"] for r in rows)
    total_unrealized = sum(r["unrealized_pnl"] for r in rows)
    total_realized = sum(r["realized_pnl"] for r in rows)
    total_unrealized_pct = ((total_value / total_cost) - 1.0) * 100 if total_cost > 0 else None

    summary = {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_unrealized": total_unrealized,
        "total_realized": total_realized,
        "total_unrealized_pct": total_unrealized_pct,
        "assets_count": len(rows),
        "quote_asset": quote_asset,
    }
    rows.sort(key=lambda r: r["current_value"], reverse=True)
    return summary, rows
