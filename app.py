import pandas as pd
import streamlit as st

SPREADSHEET_ID = "1p4oZCjqQuAW8fv0kLZ1lU2NtMQaMi6K7Z0gzZUPt1Iw"
GID = "0"

SELECTED_TSP_IDS = [
    "164934","165507","164051","164810","166033","164502","164501","166277",
    "168418","167152","164356","163418","164798","164503","168360","167732",
    "164581","165991","168422","168415","168346","168313","168413","167709",
    "165993","164580","167961","168108","168416","168053","168417","167930",
    "168414","166481","168420","168386","168419","164417","168421","164582",
    "164768","168385","168999"
]

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

st.set_page_config(
    page_title="4MR Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL, dtype=str)
    df.columns = df.columns.str.strip()

    required_cols = ["Door TSP", "Address", "Sub-Agent Name", "Current 4MR%"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()

    df["Door TSP"] = df["Door TSP"].astype(str).str.strip()

    filtered = df[df["Door TSP"].isin(SELECTED_TSP_IDS)].copy()

    filtered = filtered[["Door TSP", "Address", "Sub-Agent Name", "Current 4MR%"]]

    filtered["Current 4MR%"] = filtered["Current 4MR%"].fillna("").astype(str)

    return filtered

st.title("📊 4MR Dashboard")
st.caption("Selected TSP IDs only — Address, Sub-Agent Name, and Current 4MR%")

df = load_data()

search = st.text_input(
    "Search",
    placeholder="Search TSP ID, address, or sub-agent name..."
)

if search:
    s = search.lower()
    df_view = df[
        df.apply(lambda row: row.astype(str).str.lower().str.contains(s).any(), axis=1)
    ]
else:
    df_view = df

col1, col2 = st.columns(2)
col1.metric("Stores Showing", len(df_view))
col2.metric("Selected TSP IDs", len(SELECTED_TSP_IDS))

def highlight_4mr(val):
    try:
        num = float(str(val).replace("%", "").strip())
        if num >= 70:
            return "color: green; font-weight: bold;"
        return "color: red; font-weight: bold;"
    except:
        return ""

st.dataframe(
    df_view.style.map(highlight_4mr, subset=["Current 4MR%"]),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="Download Current View as CSV",
    data=df_view.to_csv(index=False).encode("utf-8"),
    file_name="selected_tsp_4mr_dashboard.csv",
    mime="text/csv"
)
