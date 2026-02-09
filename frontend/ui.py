"""
Module pour les composants d'interface utilisateur Streamlit
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from .config import THEME


def setup_page_config(config):
    """
    Configure la page Streamlit

    Args:
        config (dict): Configuration de la page
    """
    st.set_page_config(
        page_title=config["page_title"],
        page_icon=config["page_icon"],
        layout=config["layout"],
        initial_sidebar_state=config["initial_sidebar_state"]
    )


def apply_custom_style():
    """Applique un style moderne a l'application Streamlit."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Manrope:wght@400;500;700&display=swap');

        :root {
            --bg-1: #0b1324;
            --bg-2: #16233f;
            --card: rgba(14, 24, 45, 0.74);
            --card-strong: rgba(20, 34, 62, 0.92);
            --line: rgba(164, 180, 214, 0.28);
            --text: #eaf1ff;
            --muted: #9fb0d6;
            --good: #2fd089;
            --bad: #ff6f7d;
            --accent: #58c2ff;
            --accent-2: #ffb648;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(88,194,255,0.18) 0%, rgba(88,194,255,0) 38%),
                radial-gradient(circle at 90% 82%, rgba(255,182,72,0.15) 0%, rgba(255,182,72,0) 42%),
                linear-gradient(145deg, var(--bg-1) 0%, var(--bg-2) 100%);
            color: var(--text);
            font-family: 'Manrope', sans-serif;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 1.2rem;
            padding-bottom: 2.5rem;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text);
            letter-spacing: 0.2px;
        }

        .hero {
            border: 1px solid var(--line);
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(25, 40, 70, 0.85), rgba(14, 23, 43, 0.9));
            padding: 1rem 1.1rem 1.15rem;
            box-shadow: 0 18px 36px rgba(3, 10, 26, 0.35);
            margin-bottom: 0.9rem;
        }

        .hero-kicker {
            color: var(--accent);
            font-size: 0.76rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            margin: 0;
            font-size: clamp(1.4rem, 3.4vw, 2.1rem);
            font-weight: 700;
            line-height: 1.1;
        }

        .hero-sub {
            margin-top: 0.35rem;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .hero-total {
            margin-top: 0.72rem;
            font-size: clamp(1.2rem, 3.6vw, 2rem);
            font-weight: 700;
            color: #ffffff;
        }

        .metric-card {
            border: 1px solid var(--line);
            border-radius: 14px;
            background: var(--card);
            backdrop-filter: blur(3px);
            padding: 0.85rem 0.9rem;
            min-height: 122px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            color: var(--text);
            font-weight: 700;
            font-size: 1.2rem;
            font-family: 'Space Grotesk', sans-serif;
        }

        .metric-note {
            color: var(--muted);
            font-size: 0.84rem;
            margin-top: 0.3rem;
        }

        .section-title {
            margin-top: 1.1rem;
            margin-bottom: 0.55rem;
            font-size: 1.16rem;
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text);
        }

        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(16, 28, 49, 0.95), rgba(11, 19, 36, 0.96));
            border-right: 1px solid var(--line);
        }

        div[data-testid="stSidebar"] h1,
        div[data-testid="stSidebar"] h2,
        div[data-testid="stSidebar"] h3,
        div[data-testid="stSidebar"] p,
        div[data-testid="stSidebar"] span,
        div[data-testid="stSidebar"] label {
            color: var(--text);
        }

        [data-testid="stMetricValue"] {
            color: var(--text);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 14px;
            overflow: hidden;
            background: var(--card-strong);
        }

        [data-testid="stTabs"] button[role="tab"] {
            color: var(--muted);
            border-radius: 8px;
            padding: 0.35rem 0.8rem;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--text);
            background: rgba(88,194,255,0.12);
            border: 1px solid rgba(88,194,255,0.35);
        }

        .positive {
            color: var(--good);
            font-weight: 700;
        }

        .negative {
            color: var(--bad);
            font-weight: 700;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 0.85rem;
            }
            .hero {
                padding: 0.85rem 0.85rem 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_percentage(value):
    """
    Formate un pourcentage avec couleur

    Args:
        value (float): Valeur du pourcentage

    Returns:
        str: HTML formate pour le pourcentage
    """
    if value is None:
        return "N/A"

    if value >= 0:
        return f"<span class='positive'>+{value:.2f}%</span>"
    return f"<span class='negative'>{value:.2f}%</span>"


def display_portfolio_summary(data):
    """Affiche le resume principal du portefeuille."""
    total = float(data.get("total", 0) or 0)
    gold_price = float(data.get("goldPrice", 0) or 0)
    zakat = float(data.get("zakat", 0) or 0)
    counter = data.get("counter", 0)
    current_time = data.get("current_time", "N/A")

    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-kicker">Dashboard Live</div>
            <h1 class="hero-title">Mon Portefeuille Crypto</h1>
            <div class="hero-sub">Vision instantanee de ton allocation, de la zakat et de l'evolution.</div>
            <div class="hero-total">${total:,.2f}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Prix de l'or</div>
                <div class="metric-value">${gold_price:,.2f}</div>
                <div class="metric-note">Valeur utilisee pour le seuil de nisab.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Zakat estimee</div>
                <div class="metric-value">${zakat:,.2f}</div>
                <div class="metric-note">{data.get('msg', 'N/A')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Jours ecoules</div>
                <div class="metric-value">{counter} jours</div>
                <div class="metric-note">Derniere mise a jour: {current_time}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_crypto_table(data):
    """Affiche un tableau moderne des cryptomonnaies."""
    st.markdown("<div class='section-title'>Detail des cryptomonnaies</div>", unsafe_allow_html=True)

    rows = []
    for token, details in data.get("token_balance", {}).items():
        balance = float(details.get("balance", 0) or 0)
        price = float(data.get("token_price", {}).get(token, 0) or 0)
        market_cap = data.get("token_mc", {}).get(token, "N/A")
        evolution = details.get("evolution", None)

        rows.append(
            {
                "Token": token,
                "Valeur ($)": balance,
                "Prix ($)": price,
                "Market Cap": market_cap,
                "Evolution 24h (%)": evolution,
            }
        )

    if not rows:
        st.warning("Aucune donnee disponible.")
        return

    df = pd.DataFrame(rows).sort_values(by="Valeur ($)", ascending=False)

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Token": st.column_config.TextColumn("Token"),
            "Valeur ($)": st.column_config.NumberColumn("Valeur ($)", format="$%.2f"),
            "Prix ($)": st.column_config.NumberColumn("Prix ($)", format="$%.6f"),
            "Market Cap": st.column_config.TextColumn("Market Cap"),
            "Evolution 24h (%)": st.column_config.NumberColumn("Evolution 24h (%)", format="%.2f%%"),
        },
    )


def create_evolution_chart(csv_path, view_mode="Normalized"):
    """
    Cree un graphique d'evolution des cryptomonnaies avec Plotly

    Args:
        csv_path (str): Chemin vers le fichier CSV des donnees

    Returns:
        plotly.graph_objects.Figure: Figure Plotly ou None en cas d'erreur
    """
    try:
        df = pd.read_csv(csv_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df_pivot = df.pivot_table(index="Date", columns="Crypto", values="Valeur").sort_index()
        df_chart = df_pivot.copy()
        yaxis_title = "Valeur ($)"
        hover_suffix = " $"

        if view_mode == "Normalized":
            # Base 100 par token pour comparer les tendances sans ecrasement.
            def _normalize(series):
                valid = series.dropna()
                if valid.empty or valid.iloc[0] == 0:
                    return series
                return (series / valid.iloc[0]) * 100

            df_chart = df_pivot.apply(_normalize, axis=0)
            yaxis_title = "Indice (base 100)"
            hover_suffix = ""
        elif view_mode == "Log":
            # Echelle log utile quand une crypto domine largement (ex: XRP).
            df_chart = df_pivot.where(df_pivot > 0)

        colors = ["#58c2ff", "#2fd089", "#ffb648", "#ff6f7d", "#b58cff", "#73e7ff", "#ffd86f"]
        fig = go.Figure()

        for idx, column in enumerate(df_chart.columns):
            fig.add_trace(
                go.Scatter(
                    x=df_chart.index,
                    y=df_chart[column],
                    mode="lines",
                    name=column,
                    line={"width": 2.4, "color": colors[idx % len(colors)]},
                    hovertemplate="%{x|%d/%m %H:%M}<br>%{y:,.2f}"
                    + hover_suffix
                    + "<extra>"
                    + str(column)
                    + "</extra>",
                )
            )

        fig.update_layout(
            title="Evolution des valeurs",
            xaxis_title="Date",
            yaxis_title=yaxis_title,
            height=540,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#eaf1ff"},
            xaxis={"gridcolor": "rgba(255,255,255,0.09)"},
            yaxis={"gridcolor": "rgba(255,255,255,0.09)"},
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
            margin={"l": 20, "r": 20, "t": 52, "b": 12},
            hovermode="x unified",
        )
        if view_mode == "Log":
            fig.update_yaxes(type="log")

        return fig
    except Exception as e:
        st.error(f"Erreur lors de la creation du graphique: {e}")
        return None


def display_charts(data_file, plot_file):
    """
    Affiche les graphiques d'evolution

    Args:
        data_file (str): Chemin vers le fichier CSV des donnees
        plot_file (str): Chemin vers l'image du graphique statique
    """
    st.markdown("<div class='section-title'>Evolution des valeurs</div>", unsafe_allow_html=True)

    try:
        tab1, tab2 = st.tabs(["Interactif", "Statique"])

        with tab1:
            view_mode = st.radio(
                "Mode de vue",
                options=["Normalized", "Real", "Log"],
                index=0,
                horizontal=True,
            )
            fig = create_evolution_chart(data_file, view_mode=view_mode)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.image(plot_file, use_column_width=True)
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du graphique: {e}")
        st.warning("Utilisation du graphique statique uniquement")
        try:
            st.image(plot_file, use_column_width=True)
        except Exception as e2:
            st.error(f"Impossible d'afficher le graphique statique: {e2}")


def display_error_message():
    """Affiche un message d'erreur en cas de probleme de connexion au backend."""
    st.error("Impossible de recuperer les donnees du portefeuille. Verifie que le serveur backend est en cours d'execution.")
