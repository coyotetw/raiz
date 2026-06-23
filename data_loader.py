"""
data_loader.py — Carga y procesamiento de datos para Raíz Emprendedora
Lee los archivos Excel directamente del repositorio (carpeta data/)
"""

import pandas as pd
import numpy as np
import re
import os
import psycopg2
import streamlit as st

# ── Rutas locales (archivos dentro del repo) ──────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PATH_MADRE    = os.path.join(BASE_DIR, "data", "base_madre.xlsx")
PATH_RAIZ     = os.path.join(BASE_DIR, "data", "base_raiz.xlsx")

# ── Columnas de eventos con etiquetas legibles ────────────────────────────
EVENTOS = {
    "CR_jul25":           "CR jul-25",
    "TW_ago25":           "TW ago-25",
    "PM_nov25":           "PM nov-25",
    "Feria_RW_dic25":     "RW dic-25",
    "Feria_Hoyo_ene26":   "El Hoyo ene-26",
    "Feria_EQ_feb26":     "Feria EQ feb-26",
    "EQ_mar26":           "EQ mar-26",
    "Feria_Tecka_mar26":  "Tecka mar-26",
    "Feria_Gaiman_mar26": "Gaiman mar-26",
    "Feria_TW_abr26":     "TW abr-26",
    "CICECH_abr26":       "CICECH abr-26",
    "CR_may26":           "CR may-26",
    "PM_jun26":           "PM jun-26",
    "CerroCentinela_26":  "Cerro Centinela",
}

ORDEN_SITUACION = [
    "Normal", "Riesgo bajo", "Riesgo medio",
    "Riesgo alto", "Irrecuperable", "Sin registro BCRA", "Sin deuda"
]


def limpiar_cuit(v):
    if pd.isna(v):
        return None
    c = re.sub(r"\D", "", str(v).strip())
    return c if len(c) == 11 else None


def clasificar_formalidad(row):
    ok  = str(row.get("ok_cuitonline", "")).strip().upper()
    act = str(row.get("actividades", "")).strip()
    invalidas = ("", "nan", "Sin datos", "No se encontró denominación")
    return "Formal" if ok == "TRUE" and act not in invalidas else "Informal"


def clasificar_regimen(act):
    a = str(act).upper()
    if "MONOTRIBUTO"           in a: return "Monotributo"
    if "AUTÓNOMO" in a or "AUTONOMO" in a: return "Autónomo"
    if "RESPONSABLE INSCRIPTO" in a: return "Resp. Inscripto"
    return "Sin dato"


@st.cache_data(ttl=3600, show_spinner="Cargando datos del programa...")
def cargar_base():

    # ── Fuente 1: Base madre ──────────────────────────────────────────────
    bm = pd.read_excel(PATH_MADRE, dtype=str)
    bm["cuit_limpio"] = bm["CUIT"].apply(limpiar_cuit)

    # ── Fuente 2: Base raiz ───────────────────────────────────────────────
    br = pd.read_excel(PATH_RAIZ, dtype=str)
    br["cuit_limpio"] = br["cuit"].apply(limpiar_cuit)
    br["formalidad"]  = br.apply(clasificar_formalidad, axis=1)
    br["regimen"]     = br["actividades"].apply(clasificar_regimen)

    # ── Merge personas + actividad ────────────────────────────────────────
    COLS_BM = [c for c in [
        "cuit_limpio", "Apellido", "Nombre", "Email_norm",
        "Localidad_norm", "Es_VIRCh", "Edad_norm",
        "Registro_completo", "Total_participaciones",
        *EVENTOS.keys()
    ] if c in bm.columns]

    COLS_BR = ["cuit_limpio", "formalidad", "regimen",
               "nombre_arca", "actividades", "ok_arca", "estado_arca"]

    df_pers = bm[COLS_BM].dropna(subset=["cuit_limpio"]).drop_duplicates("cuit_limpio")
    df_act  = br[[c for c in COLS_BR if c in br.columns]].drop_duplicates("cuit_limpio")
    base    = df_pers.merge(df_act, on="cuit_limpio", how="left")
    base["formalidad"] = base["formalidad"].fillna("Sin dato")
    base["regimen"]    = base["regimen"].fillna("Sin dato")

    # ── Fuente 3: BCRA desde PostgreSQL ──────────────────────────────────
    DATABASE_URL = st.secrets.get("DATABASE_URL", "")
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=15)
            sql = """
                SELECT
                    cuit,
                    MAX(situacion)                                      AS peor_situacion,
                    SUM(CASE WHEN monto > 0 THEN monto ELSE 0 END)     AS monto_total,
                    COUNT(DISTINCT entidad)                             AS cantidad_entidades,
                    STRING_AGG(DISTINCT entidad, ', ' ORDER BY entidad) AS entidades
                FROM historico_bcra
                WHERE periodo = '202604'
                GROUP BY cuit
            """
            df_bcra = pd.read_sql_query(sql, conn)
            conn.close()
            df_bcra = df_bcra.rename(columns={"cuit": "cuit_limpio"})
            MAP_SIT = {
                0: "Sin deuda",    1: "Normal",      2: "Riesgo bajo",
                3: "Riesgo medio", 4: "Riesgo alto", 5: "Irrecuperable",
                6: "Irrecuperable técnico"
            }
            df_bcra["situacion_label"] = df_bcra["peor_situacion"].map(MAP_SIT).fillna("Sin dato")
            df_bcra["tiene_deuda"]     = df_bcra["monto_total"] > 0
            base = base.merge(df_bcra, on="cuit_limpio", how="left")
        except Exception as e:
            st.warning(f"⚠️ Sin conexión BCRA: {e}")
            _bcra_vacios(base)
    else:
        st.info("ℹ️ DATABASE_URL no configurada en secrets — datos BCRA no disponibles.")
        _bcra_vacios(base)

    # ── Tipado final ──────────────────────────────────────────────────────
    base["peor_situacion"]     = pd.to_numeric(base.get("peor_situacion"),     errors="coerce").fillna(-1).astype(int)
    base["monto_total"]        = pd.to_numeric(base.get("monto_total"),        errors="coerce").fillna(0)
    base["cantidad_entidades"] = pd.to_numeric(base.get("cantidad_entidades"), errors="coerce").fillna(0).astype(int)
    base["tiene_deuda"]        = base.get("tiene_deuda", pd.Series(False, index=base.index)).fillna(False).astype(str).str.upper() == "TRUE"
    base["situacion_label"]    = base.get("situacion_label", pd.Series("Sin registro BCRA", index=base.index)).fillna("Sin registro BCRA")
    base["Edad_norm"]          = pd.to_numeric(base.get("Edad_norm"), errors="coerce")
    base["Total_participaciones"] = pd.to_numeric(base.get("Total_participaciones"), errors="coerce").fillna(1).astype(int)

    return base


def _bcra_vacios(df):
    df["peor_situacion"]     = -1
    df["monto_total"]        = 0.0
    df["tiene_deuda"]        = False
    df["situacion_label"]    = "Sin registro BCRA"
    df["cantidad_entidades"] = 0
    df["entidades"]          = ""
