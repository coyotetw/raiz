# 🌱 Raíz Emprendedora — Dashboard

Dashboard de gestión y diagnóstico del programa **Raíz Emprendedora**.  
Dirección de Promoción de las Inversiones · Ministerio de Producción · Provincia del Chubut.

---

## Estructura del proyecto

```
raiz_dashboard/
├── app.py              ← App principal (Streamlit)
├── data_loader.py      ← Carga y procesamiento de datos
├── requirements.txt    ← Dependencias Python
├── .gitignore
├── .streamlit/
│   ├── config.toml     ← Tema y configuración
│   └── secrets.toml    ← ⚠️ NO subir (credenciales DB)
└── README.md
```

---

## Deploy en Streamlit Cloud (paso a paso)

### 1. Subir a GitHub

```bash
# Crear repositorio en github.com, luego:
git init
git add .
git commit -m "Dashboard Raíz Emprendedora"
git remote add origin https://github.com/TU_USUARIO/raiz-dashboard.git
git push -u origin main
```

### 2. Conectar en Streamlit Cloud

1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. **New app** → seleccionar tu repositorio
3. Main file: `app.py`
4. Ir a **Advanced settings → Secrets**
5. Pegar esto (con tu URL real de PostgreSQL):

```toml
DATABASE_URL = "postgresql://herramientas_chubut_db_user:PASSWORD@host/herramientas_chubut_db"
```

6. Hacer clic en **Deploy**

---

## Correr localmente

```bash
pip install -r requirements.txt

# Crear archivo de secrets local:
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Editar secrets.toml con la URL real de la base

streamlit run app.py
```

---

## Fuentes de datos

| Fuente | Qué aporta | Acceso |
|--------|-----------|--------|
| Google Sheets `00_Base_Normalizada_Filtrable` | Datos personales: nombre, CUIT, localidad, eventos | Público (export xlsx) |
| Google Drive `02base_raiz_emprendedora.xlsx` | Actividad ARCA + CuitOnline (formalidad) | Público (export xlsx) |
| PostgreSQL en Render (`historico_bcra`) | Deuda BCRA período 202604 | Credencial en Secrets |

---

## Funcionalidades

- **KPIs en tiempo real**: total, formales, deuda BCRA, irrecuperables
- **Filtros** por formalidad, situación BCRA, completitud y localidad
- **Tab Formalidad y BCRA**: distribución, régimen fiscal, cruce formalidad × deuda
- **Tab Eventos**: participación por evento con tabla descargable
- **Tab Territorial**: ranking de localidades, desglose de formalidad por localidad
- **Tab Explorador**: búsqueda por CUIT/nombre, descarga CSV

---

## Paleta institucional

| Color | Hex | Uso |
|-------|-----|-----|
| Azul petróleo | `#0E4D5F` | Principal, header, gráficos |
| Naranja | `#E85D36` | Alertas, informales, deuda |
| Dorado | `#F4B41A` | Riesgo bajo, acentos |
| Turquesa | `#1B7F91` | Normal/sin deuda, positivo |
