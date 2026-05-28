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
    page_title="DLAR MR Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_data():
    raw = pd.read_csv(CSV_URL, header=None, dtype=str)

    average_row = raw.iloc[3].copy()
    headers = raw.iloc[4].astype(str).str.strip()

    df = raw.iloc[5:].copy()
    df.columns = headers
    df = df.loc[:, df.columns.notna()]
    df.columns = df.columns.str.strip()

    avg_df = pd.DataFrame([average_row.values], columns=headers)
    avg_df.columns = avg_df.columns.str.strip()

    if "Door TSP" not in df.columns:
        st.error("Door TSP column not found. Please check DLAR header row.")
        return pd.DataFrame(), avg_df

    df["Door TSP"] = df["Door TSP"].astype(str).str.strip()

    filtered = df[df["Door TSP"].isin(SELECTED_TSP_IDS)].copy()

    columns_to_show = [
        "Door TSP",
        "Address",
        "Sub-Agent Name",

        "Current 2MR Acts",
        "Current 2MR Payments",
        "Current 2MR%",

        "Prior 2MR Acts",
        "Prior 2MR Payments",
        "Prior 2MR%",

        "Current 3MR Acts",
        "Current 3MR Payments",
        "Current 3MR%",

        "Prior 3MR Acts",
        "Prior 3MR Payments",
        "Prior 3MR%",

        "Current 4MR Acts",
        "Current 4MR Payments",
        "Current 4MR%",

        "Prior 4MR Acts",
        "Prior 4MR Payments",
        "Prior 4MR%",

        "Prior 5MR Acts",
        "Prior 5MR Payments",
        "Prior 5MR%",

        "Prior 6MR Acts",
        "Prior 6MR Payments",
        "Prior 6MR%",

        "Prior 7MR Acts",
        "Prior 7MR Payments",
        "Prior 7MR%"
    ]

    existing_columns = [col for col in columns_to_show if col in filtered.columns]

    filtered = filtered[existing_columns]

    return filtered, avg_df


def color_percent(val):
    try:
        num = float(str(val).replace("%", "").strip())

        if num >= 70:
            return "color: green; font-weight: bold;"
        elif num == 0:
            return "color: gray;"
        else:
            return "color: red; font-weight: bold;"
    except:
        return ""


def clean_percent(val):
    try:
        val = str(val).replace("%", "").strip()
        if val == "" or val.lower() == "nan":
            return ""
        return f"{float(val):.2f}%"
    except:
        return val


st.title("📊 DLAR MR Dashboard")
st.caption("Selected TSP IDs only")

df, avg_df = load_data()

if df.empty:
    st.stop()

search = st.text_input(
    "Search",
    placeholder="Search TSP ID, address, or sub-agent..."
)

if search:
    s = search.lower()
    df_view = df[
        df.apply(
            lambda row: row.astype(str).str.lower().str.contains(s).any(),
            axis=1
        )
    ]
else:
    df_view = df

col1, col2, col3 = st.columns(3)

col1.metric("Stores Showing", len(df_view))
col2.metric("Selected TSP IDs", len(SELECTED_TSP_IDS))

if "Current 4MR%" in avg_df.columns:
    avg_4mr = clean_percent(avg_df["Current 4MR%"].iloc[0])
    col3.metric("Company Avg Current 4MR%", avg_4mr)
else:
    col3.metric("Company Avg Current 4MR%", "N/A")

percent_columns = [col for col in df_view.columns if "%" in col]

styled_df = df_view.style

for col in percent_columns:
    styled_df = styled_df.map(color_percent, subset=[col])

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)

csv = df_view.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="dlar_mr_dashboard.csv",
    mime="text/csv"
)
