"""
app.py — Dashboard Raíz Emprendedora
Streamlit Cloud · GitHub deploy
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from data_loader import cargar_base, EVENTOS, ORDEN_SITUACION

# ── Paleta institucional ──────────────────────────────────────────────────
PETRO   = "#0E4D5F"
NARANJA = "#E85D36"
DORADO  = "#F4B41A"
TURQ    = "#1B7F91"
GRIS    = "#6B7280"

COLOR_SIT = {
    "Normal":           TURQ,
    "Riesgo bajo":      DORADO,
    "Riesgo medio":     "#E8A020",
    "Riesgo alto":      "#E07030",
    "Irrecuperable":    NARANJA,
    "Sin registro BCRA":"#9CA3AF",
    "Sin deuda":        "#CBD5E1",
}

# ── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Raíz Emprendedora | Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: #F8FAFC; }}

  /* ── Header ── */
  .main-header {{
    background: linear-gradient(135deg, {PETRO} 0%, {TURQ} 100%);
    color: white;
    padding: 1.8rem 2.5rem 1.4rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
  }}
  .main-header h1 {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.3rem;
    font-weight: 700;
    margin: 0 0 0.2rem;
    letter-spacing: 0.5px;
  }}
  .main-header p {{ font-size: 0.88rem; opacity: 0.82; margin: 0; }}

  /* ── KPI cards ── */
  .kpi-card {{
    background: white;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 2px 8px rgba(14,77,95,0.08);
    border-left: 4px solid {PETRO};
    height: 100%;
  }}
  .kpi-card.naranja {{ border-left-color: {NARANJA}; }}
  .kpi-card.turq    {{ border-left-color: {TURQ};    }}
  .kpi-card.dorado  {{ border-left-color: {DORADO};  }}
  .kpi-value {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.1rem; font-weight: 700;
    color: {PETRO}; line-height: 1; margin-bottom: 0.15rem;
  }}
  .kpi-label {{
    font-size: 0.72rem; color: {GRIS};
    text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
  }}
  .kpi-sub {{ font-size: 0.82rem; color: {GRIS}; margin-top: 0.25rem; }}

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {{ background-color: {PETRO}; }}
  section[data-testid="stSidebar"] * {{ color: white !important; }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stMultiSelect label {{
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px;
  }}

  /* ── Sección títulos ── */
  .sec-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.2rem; font-weight: 700;
    color: {PETRO}; text-transform: uppercase; letter-spacing: 1px;
    border-bottom: 2px solid {NARANJA};
    padding-bottom: 0.25rem; margin: 1.8rem 0 1rem;
  }}

  /* ── Alertas ── */
  .alerta {{ background: #FFF3EE; border: 1px solid {NARANJA};
    border-radius: 8px; padding: 0.7rem 1rem;
    font-size: 0.86rem; color: #7A2A10; margin-bottom: 1rem; }}
  .info-box {{ background: #EEF7FA; border: 1px solid {TURQ};
    border-radius: 8px; padding: 0.7rem 1rem;
    font-size: 0.86rem; color: {PETRO}; margin-bottom: 1rem; }}

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
  .stTabs [data-baseweb="tab"] {{
    background: white; border-radius: 8px 8px 0 0;
    padding: 0.5rem 1.2rem; font-weight: 600;
    color: {PETRO} !important; border: 1px solid #E5E7EB;
  }}
  .stTabs [aria-selected="true"] {{
    background: {PETRO} !important; color: white !important;
  }}
</style>
""", unsafe_allow_html=True)


# ── Carga de datos ────────────────────────────────────────────────────────
df_raw = cargar_base()


# ── Sidebar — filtros ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌱 Raíz Emprendedora")
    st.markdown("**Ministerio de Producción · Chubut**")
    st.markdown("---")
    st.markdown("### Filtros")

    f_formal = st.selectbox(
        "Formalidad",
        ["Todas"] + sorted(df_raw["formalidad"].dropna().unique()),
    )
    f_sit = st.selectbox(
        "Situación BCRA",
        ["Todas"] + [s for s in ORDEN_SITUACION if s in df_raw["situacion_label"].values],
    )
    f_reg = st.selectbox(
        "Registro",
        ["Todos"] + sorted(df_raw["Registro_completo"].dropna().unique()),
    )
    localidades = sorted(df_raw["Localidad_norm"].dropna().unique()) if "Localidad_norm" in df_raw.columns else []
    f_loc = st.selectbox("Localidad", ["Todas"] + localidades)

    st.markdown("---")
    if st.button("🔄 Recargar datos"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Datos BCRA: período 202604  \nActualizado: junio 2026")


# ── Aplicar filtros ───────────────────────────────────────────────────────
df = df_raw.copy()
if f_formal != "Todas":
    df = df[df["formalidad"] == f_formal]
if f_sit != "Todas":
    df = df[df["situacion_label"] == f_sit]
if f_reg != "Todos":
    df = df[df["Registro_completo"] == f_reg]
if f_loc != "Todas" and "Localidad_norm" in df.columns:
    df = df[df["Localidad_norm"] == f_loc]

total      = len(df)
total_raw  = len(df_raw)
filtrado   = total < total_raw


# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <h1>🌱 RAÍZ EMPRENDEDORA — Dashboard de Gestión</h1>
  <p>Dirección de Promoción de las Inversiones · Ministerio de Producción · Provincia del Chubut</p>
</div>
""", unsafe_allow_html=True)

if filtrado:
    st.markdown(
        f'<div class="info-box">🔍 Mostrando <strong>{total:,} participantes</strong> '
        f'según filtros aplicados (universo total: {total_raw:,})</div>',
        unsafe_allow_html=True
    )


# ── KPIs ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Indicadores Clave</div>', unsafe_allow_html=True)

formales   = (df["formalidad"] == "Formal").sum()
informales = (df["formalidad"] == "Informal").sum()
con_deuda  = df["tiene_deuda"].sum()
irrecup    = (df["peor_situacion"] == 5).sum()
completos  = (df["Registro_completo"] == "Completo").sum() if "Registro_completo" in df.columns else 0
monto_med  = df[df["monto_total"] > 0]["monto_total"].median() if con_deuda > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    (c1, "", f"{total:,}", "Participantes", f"{completos:,} registros completos"),
    (c2, "naranja", f"{formales:,}", "Formales", f"{formales/total*100:.1f}% del total" if total else "—"),
    (c3, "", f"{informales:,}", "Informales", f"{informales/total*100:.1f}% del total" if total else "—"),
    (c4, "turq", f"{con_deuda:,}", "Con deuda BCRA", f"{con_deuda/total*100:.1f}% · mediana ${monto_med:,.0f}k" if total else "—"),
    (c5, "dorado", f"{irrecup:,}", "Irrecuperables (sit. 5)", f"{irrecup/total*100:.1f}% del total" if total else "—"),
]
for col, cls, val, label, sub in cards:
    with col:
        st.markdown(
            f'<div class="kpi-card {cls}">'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

if irrecup > 0:
    st.markdown(
        f'<div class="alerta">⚠️ <strong>{irrecup} participantes</strong> en situación '
        f'irrecuperable (BCRA 5) en la selección actual. Se recomienda atención diferenciada.</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Formalidad y BCRA",
    "📅 Participación por Evento",
    "📍 Distribución Territorial",
    "🔍 Explorador de Participantes",
])


# ── TAB 1: Formalidad y BCRA ─────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    # Formalidad
    with col1:
        st.markdown('<div class="sec-title">Formalidad</div>', unsafe_allow_html=True)
        vals_f = df["formalidad"].value_counts().reset_index()
        vals_f.columns = ["formalidad", "cantidad"]
        vals_f["pct"] = (vals_f["cantidad"] / total * 100).round(1)
        vals_f["texto"] = vals_f.apply(lambda r: f"{r['cantidad']:,}  ({r['pct']}%)", axis=1)
        fig = px.bar(
            vals_f, x="cantidad", y="formalidad", orientation="h",
            color="formalidad",
            color_discrete_map={"Formal": PETRO, "Informal": NARANJA, "Sin dato": GRIS},
            text="texto",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False, title=""),
            yaxis_title="", margin=dict(l=0, r=100, t=10, b=10), height=220,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Régimen fiscal
        if "regimen" in df.columns:
            st.markdown('<div class="sec-title">Régimen fiscal (formales)</div>', unsafe_allow_html=True)
            reg = df[df["formalidad"] == "Formal"]["regimen"].value_counts().reset_index()
            reg.columns = ["regimen", "cantidad"]
            fig_reg = px.pie(
                reg, values="cantidad", names="regimen",
                color_discrete_sequence=[PETRO, TURQ, DORADO, NARANJA],
                hole=0.4,
            )
            fig_reg.update_traces(textinfo="label+percent", textfont_size=11)
            fig_reg.update_layout(
                showlegend=False, paper_bgcolor="white",
                margin=dict(l=0, r=0, t=10, b=10), height=240,
            )
            st.plotly_chart(fig_reg, use_container_width=True)

    # Situación BCRA
    with col2:
        st.markdown('<div class="sec-title">Situación BCRA — Período 202604</div>', unsafe_allow_html=True)
        sit_vals = (
            df["situacion_label"]
            .value_counts()
            .reindex(ORDEN_SITUACION)
            .dropna()
            .reset_index()
        )
        sit_vals.columns = ["situacion", "cantidad"]
        sit_vals["pct"] = (sit_vals["cantidad"] / total * 100).round(1)
        fig2 = px.bar(
            sit_vals, x="situacion", y="cantidad",
            color="situacion", color_discrete_map=COLOR_SIT,
            text=sit_vals.apply(lambda r: f"{r['cantidad']:,}\n{r['pct']}%", axis=1),
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="", yaxis_title="Participantes",
            xaxis_tickangle=-25, margin=dict(l=0, r=20, t=10, b=60), height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="sec-title">Deuda BCRA según formalidad</div>', unsafe_allow_html=True)
        cruce = df.groupby("formalidad")["tiene_deuda"].agg(["sum", "count"]).reset_index()
        cruce.columns = ["formalidad", "con_deuda", "total_grupo"]
        cruce["sin_deuda"] = cruce["total_grupo"] - cruce["con_deuda"]
        cruce = cruce[cruce["total_grupo"] > 5]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="Con deuda", x=cruce["formalidad"], y=cruce["con_deuda"],
            marker_color=NARANJA, text=cruce["con_deuda"].apply(lambda v: f"{v:,}"),
            textposition="outside",
        ))
        fig3.add_trace(go.Bar(
            name="Sin deuda / Sin reg.", x=cruce["formalidad"], y=cruce["sin_deuda"],
            marker_color=TURQ, text=cruce["sin_deuda"].apply(lambda v: f"{v:,}"),
            textposition="outside",
        ))
        fig3.update_layout(
            barmode="group", plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            margin=dict(l=0, r=20, t=30, b=10), height=280,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Tabla resumen BCRA
    st.markdown('<div class="sec-title">Resumen por situación BCRA</div>', unsafe_allow_html=True)
    resumen_bcra = sit_vals.copy()
    resumen_bcra["% del total"] = resumen_bcra["pct"].apply(lambda x: f"{x}%")
    resumen_bcra["monto_prom"] = resumen_bcra["situacion"].apply(
        lambda s: df[df["situacion_label"] == s]["monto_total"].replace(0, np.nan).mean()
    )
    resumen_bcra["Monto promedio ($k)"] = resumen_bcra["monto_prom"].apply(
        lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "—"
    )
    st.dataframe(
        resumen_bcra[["situacion", "cantidad", "% del total", "Monto promedio ($k)"]].rename(
            columns={"situacion": "Situación BCRA", "cantidad": "N°"}
        ),
        use_container_width=True, hide_index=True,
    )


# ── TAB 2: Eventos ────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-title">Participación por evento</div>', unsafe_allow_html=True)
    ev_data = {
        label: int((df[col] == "X").sum())
        for col, label in EVENTOS.items()
        if col in df.columns
    }
    ev_df = (
        pd.DataFrame(list(ev_data.items()), columns=["Evento", "Participantes"])
        .sort_values("Participantes", ascending=True)
    )
    fig_ev = px.bar(
        ev_df, x="Participantes", y="Evento", orientation="h",
        color_discrete_sequence=[PETRO], text="Participantes",
    )
    fig_ev.update_traces(
        texttemplate="%{text:,}", textposition="outside",
        marker_line_color="white", marker_line_width=1,
    )
    fig_ev.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, showticklabels=False, title=""),
        yaxis_title="", margin=dict(l=0, r=80, t=20, b=10), height=480,
    )
    st.plotly_chart(fig_ev, use_container_width=True)

    # Tabla
    ev_tabla = ev_df.sort_values("Participantes", ascending=False).copy()
    ev_tabla["% del total"] = (ev_tabla["Participantes"] / total * 100).round(1).apply(lambda x: f"{x}%")
    st.dataframe(ev_tabla.reset_index(drop=True), use_container_width=True, hide_index=True)


# ── TAB 3: Distribución territorial ──────────────────────────────────────
with tab3:
    if "Localidad_norm" not in df.columns:
        st.info("No hay columna de localidad disponible.")
    else:
        st.markdown('<div class="sec-title">Participantes por localidad</div>', unsafe_allow_html=True)
        top_n = st.slider("Mostrar top N localidades", 5, 30, 15)
        loc_df = (
            df["Localidad_norm"].value_counts()
            .head(top_n)
            .reset_index()
        )
        loc_df.columns = ["Localidad", "Participantes"]
        loc_df = loc_df.sort_values("Participantes", ascending=True)

        fig_loc = px.bar(
            loc_df, x="Participantes", y="Localidad", orientation="h",
            color="Participantes", color_continuous_scale=[[0, TURQ], [1, PETRO]],
            text="Participantes",
        )
        fig_loc.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_loc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False, showticklabels=False, title=""),
            yaxis_title="", margin=dict(l=0, r=80, t=20, b=10), height=500,
        )
        st.plotly_chart(fig_loc, use_container_width=True)

        # Desglose formalidad por localidad
        st.markdown('<div class="sec-title">Formalidad por localidad (top 10)</div>', unsafe_allow_html=True)
        top10_locs = df["Localidad_norm"].value_counts().head(10).index.tolist()
        df_loc_f = df[df["Localidad_norm"].isin(top10_locs)]
        cruce_loc = (
            df_loc_f.groupby(["Localidad_norm", "formalidad"])
            .size().reset_index(name="cantidad")
        )
        fig_lf = px.bar(
            cruce_loc, x="Localidad_norm", y="cantidad", color="formalidad",
            barmode="stack",
            color_discrete_map={"Formal": PETRO, "Informal": NARANJA, "Sin dato": GRIS},
        )
        fig_lf.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="", yaxis_title="Participantes",
            xaxis_tickangle=-25, legend_title="",
            margin=dict(l=0, r=20, t=20, b=60), height=340,
        )
        st.plotly_chart(fig_lf, use_container_width=True)


# ── TAB 4: Explorador ────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-title">Explorador de participantes</div>', unsafe_allow_html=True)

    col_b, col_n = st.columns([3, 1])
    with col_b:
        busqueda = st.text_input("🔍 Buscar por CUIT, nombre o localidad", placeholder="Ej: 27123456789")
    with col_n:
        n_filas = st.selectbox("Mostrar", [25, 50, 100, 200], index=0)

    # Columnas para mostrar
    COLS_SHOW = [c for c in [
        "cuit_limpio", "Apellido", "Nombre",
        "Localidad_norm", "formalidad", "regimen",
        "situacion_label", "monto_total", "cantidad_entidades",
        "Registro_completo", "Total_participaciones",
    ] if c in df.columns]

    df_tabla = df[COLS_SHOW].copy()
    df_tabla = df_tabla.rename(columns={
        "cuit_limpio":       "CUIT",
        "Localidad_norm":    "Localidad",
        "situacion_label":   "Situación BCRA",
        "monto_total":       "Deuda ($k)",
        "cantidad_entidades":"N° entidades",
        "Registro_completo": "Completitud",
        "Total_participaciones": "Participaciones",
    })

    if busqueda:
        mask = df_tabla.apply(
            lambda col: col.astype(str).str.contains(busqueda, case=False, na=False)
        ).any(axis=1)
        df_tabla = df_tabla[mask]

    st.dataframe(
        df_tabla.head(n_filas).reset_index(drop=True),
        use_container_width=True,
        height=420,
    )
    st.caption(
        f"Mostrando {min(n_filas, len(df_tabla)):,} de {len(df_tabla):,} registros"
    )

    # Descarga
    csv = df_tabla.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar selección como CSV",
        data=csv,
        file_name="raiz_emprendedora_seleccion.csv",
        mime="text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Raíz Emprendedora · Dirección de Promoción de las Inversiones · "
    "Ministerio de Producción · Provincia del Chubut · "
    "Datos BCRA período 202604 · Junio 2026"
)
