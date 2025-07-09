import streamlit as st
import pandas as pd
import re

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Farver
ACCENT_COLOR = "#8CC63F"
DARK_COLOR   = "#333333"

st.set_page_config(
    page_title="Ads vs Organic Analyzer",
    layout="wide",
)

# --- Styling ---
st.markdown(f"""
    <style>
        body {{ font-family:"Helvetica Neue",sans-serif; color:{DARK_COLOR}; }}
        .big-title {{ font-size:36px; font-weight:700; color:{ACCENT_COLOR}; text-align:center; }}
        .section-divider {{ border-top:2px solid {ACCENT_COLOR}; margin:20px 0; }}
        .upload-box {{ border:2px dashed #CCC; padding:20px; border-radius:10px; background:#F9F9F9; }}
        .stButton>button {{
            background-color:{ACCENT_COLOR}; color:white; border:none; border-radius:4px;
            padding:0.5em 1em;
        }}
        .stButton>button:hover {{ background-color:#78B72D; }}
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="big-title">🔎 Ads vs Organic Search Term Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
✅ Upload:
- Google Ads CSV (2 metadata-linjer, header på linje 3)
- GSC CSV (med header: **query,page,clicks,impressions,ctr,position**)
""")
st.info("🔒 Ingen data gemmes – alt slettes ved reload eller luk af browser.")

# --- Upload bokse ---
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
ads_file = st.file_uploader("📂 Upload Google Ads CSV", type='csv')
gsc_file = st.file_uploader("📂 Upload Search Console CSV", type='csv')
if st.button("♻️ Nulstil alt"):
    st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- Hjælpefunktioner ---
def clean_term(txt):
    if pd.isnull(txt): return ''
    s = str(txt).lower().strip()
    s = re.sub(r"[^a-z0-9æøå\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def clean_numeric(val):
    if pd.isnull(val): return 0
    s = str(val).replace('.', '').replace(',', '')
    return pd.to_numeric(s, errors='coerce')

def parse_gsc_impressions(val):
    if pd.isnull(val): return 0
    s = str(val).strip()
    s = re.sub(r'([.,]0)$', '', s)
    s = s.replace('.', '')
    try:
        return int(s)
    except:
        return 0

# --- Hovedlogik ---
if ads_file and gsc_file:

    # --- Google Ads ---
    ads = pd.read_csv(ads_file, sep=',', encoding='utf-8', skiprows=2)
    ads.columns = ads.columns.str.strip().str.lower()
    ads['søgeterm'] = ads['søgeterm'].str.replace(r'^\d+\s+', '', regex=True).apply(clean_term)
    ads = ads[ads['søgeterm'] != '']

    # Fjern rækker med summer og "i alt" linjer
    forbudte_mønstre = [
        'i alt konto',
        'i alt performance max',
        'i alt søgetermer',
        'i alt andre søgetermer',
        'i alt søg',
        'i alt shopping'
    ]
    ads = ads[~ads['søgeterm'].isin(forbudte_mønstre)]

    expo_col = next((c for c in ads.columns if 'eksp' in c), None)
    if not expo_col:
        st.error("❌ Kunne ikke finde Ads-eksponeringer-kolonnen!")
        st.stop()

    ads[expo_col] = ads[expo_col].apply(clean_numeric)
    if 'interaktioner' in ads.columns:
        ads['interaktioner'] = ads['interaktioner'].apply(clean_numeric)

    if 'kampagne' in ads.columns:
        ads['kampagne'] = ads['kampagne'].str.strip().str.lower()
    else:
        ads['kampagne'] = ''

    ads_grouped = ads.groupby(['søgeterm', 'kampagne'], as_index=False).agg({
        expo_col: 'sum',
        'interaktioner': 'sum'
    })

    # --- GSC ---
    gsc_lines = gsc_file.getvalue().decode('utf-8').splitlines()
    header_idx = None
    for i, line in enumerate(gsc_lines):
        if line.lower().startswith('query,') and 'impressions' in line.lower():
            header_idx = i
            break
    if header_idx is None:
        st.error("❌ Kunne ikke finde headerlinje i GSC-fil!")
        st.stop()

    gsc = pd.read_csv(gsc_file, sep=',', encoding='utf-8', header=header_idx)
    gsc.columns = gsc.columns.str.strip().str.lower()
    if 'query' not in gsc.columns or 'impressions' not in gsc.columns:
        st.error(f"❌ GSC header mangler 'query' eller 'impressions'. Fundet: {gsc.columns.tolist()}")
        st.stop()

    gsc['søgeterm_renset'] = gsc['query'].apply(clean_term)
    gsc['impressions'] = gsc['impressions'].apply(parse_gsc_impressions)
    gsc['clicks'] = gsc['clicks'].apply(parse_gsc_impressions)

    gsc_grouped = gsc.groupby('søgeterm_renset', as_index=False).agg({
        'impressions': 'sum'
    })

    merged = pd.merge(
        ads_grouped,
        gsc_grouped,
        left_on='søgeterm',
        right_on='søgeterm_renset',
        how='left'
    )
    merged['impressions'] = merged['impressions'].fillna(0)
    merged['Organic_missing'] = merged['impressions'] == 0

    merged = merged.rename(columns={
        expo_col: 'Ads Eksponeringer',
        'interaktioner': 'Ads Interaktioner',
        'impressions': 'GSC Eksponeringer',
        'søgeterm': 'Google Ads søgning',
        'kampagne': 'Google Ads Kampagne'
    })
    merged['Synlig organisk'] = merged['Organic_missing'].map(lambda x: '✅' if not x else '🔴')
    merged.drop(columns=['Organic_missing', 'søgeterm_renset'], inplace=True)

    # --- Filtrering
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.expander("⚙️ Filtrer"):
        min_ads    = st.slider("Min Ads Eksponeringer", 0, 5000, 0)
        min_clicks = st.slider("Min Ads Klik", 0, 500, 0)
        max_gsc    = st.slider("Max GSC Eksponeringer", 0, 5000, 5000)

        kampagner = merged['Google Ads Kampagne'].dropna().unique().tolist()
        valgt_kampagner = st.multiselect("Vælg Google Ads Kampagne", kampagner, default=kampagner)

    df = merged.copy()
    df = df[df['Ads Eksponeringer'] >= min_ads]
    df = df[df['Ads Interaktioner'] >= min_clicks]
    df = df[df['GSC Eksponeringer'] <= max_gsc]
    df = df[df['Google Ads Kampagne'].isin(valgt_kampagner)]

    if df.empty:
        st.info("❗️ Ingen resultater opfylder de valgte filtre endnu.")
    else:
        df = df.sort_values(by='GSC Eksponeringer', ascending=False)

        st.subheader(f"✅ Resultat ({df.shape[0]} rækker)")

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(
            flex=1,
            minWidth=120,
            resizable=True,
            filter=True
        )
        gb.configure_grid_options(
            domLayout='normal',
            rowHeight=28,
            animateRows=True
        )
        gb.configure_side_bar()
        gb.configure_pagination(
            paginationAutoPageSize=False,
            paginationPageSize=20
        )

        grid_options = gb.build()

        AgGrid(
            df,
            gridOptions=grid_options,
            height=600,
            theme="alpine",
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True
        )

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download CSV", csv, "ads_vs_organic_result.csv", "text/csv")

else:
    st.warning("⬆️ Upload begge filer for at komme i gang!")
