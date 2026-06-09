import pandas as pd
import streamlit as st


SPREADSHEET_ID = "1p4oZCjqQuAW8fv0kLZ1lU2NtMQaMi6K7Z0gzZUPt1Iw"
GID = "0"

SELECTED_TSP_IDS = [
    "164934", "165507", "164051", "164810", "166033", "164502", "164501", "166277",
    "168418", "167152", "164356", "163418", "164798", "164503", "168360", "167732",
    "164581", "165991", "168422", "168415", "168346", "168313", "168413", "167709",
    "165993", "164580", "167961", "168108", "168416", "168053", "168417", "167930",
    "168414", "166481", "168420", "168386", "168419", "164417", "168421", "164582",
    "164768", "168385", "168999"
]

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"


st.set_page_config(
    page_title="DLAR MR Dashboard",
    page_icon="📊",
    layout="wide"
)


def normalize_tsp(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()
    value = value.replace(".0", "")
    value = value.replace(",", "")
    return value


def clean_percent(val):
    try:
        val = str(val).replace("%", "").strip()

        if val == "" or val.lower() in ["nan", "none"]:
            return ""

        return f"{float(val):.2f}%"
    except:
        return val


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


def highlight_percent_columns(row):
    styles = []

    for col, val in row.items():
        if "%" in col:
            styles.append(color_percent(val))
        else:
            styles.append("")

    return styles


@st.cache_data(ttl=300)
def load_data():
    raw = pd.read_csv(CSV_URL, header=None, dtype=str)

    if raw.shape[1] == 1:
        raw = raw[0].str.split("\t", expand=True)

    average_row = raw.iloc[3].copy()
    headers = raw.iloc[4].astype(str).str.strip()

    df = raw.iloc[5:].copy()
    df.columns = headers

    df = df.loc[:, ~df.columns.astype(str).str.lower().isin(["nan", "none", ""])]
    df.columns = df.columns.astype(str).str.strip()

    avg_df = pd.DataFrame([average_row.values[:len(headers)]], columns=headers)
    avg_df = avg_df.loc[:, ~avg_df.columns.astype(str).str.lower().isin(["nan", "none", ""])]
    avg_df.columns = avg_df.columns.astype(str).str.strip()

    if "Door TSP" not in df.columns:
        st.error("Door TSP column not found. Please check DLAR header row.")
        st.write("Available columns:", list(df.columns))
        return pd.DataFrame(), avg_df

    df["Door TSP"] = df["Door TSP"].apply(normalize_tsp)

    selected_ids_clean = [normalize_tsp(x) for x in SELECTED_TSP_IDS]

    filtered = df[df["Door TSP"].isin(selected_ids_clean)].copy()

    columns_to_show = [
        "Door TSP",
        "Address",
        "Sub-Agent Name",
        "City",
        "State",

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

    for col in filtered.columns:
        if "%" in col:
            filtered[col] = filtered[col].apply(clean_percent)

    return filtered, avg_df


st.title("📊 DLAR MR Dashboard")
st.caption("Selected TSP IDs only")

df, avg_df = load_data()

if df.empty:
    st.warning("No matching selected TSP IDs found.")
    st.stop()


search = st.text_input(
    "Search",
    placeholder="Search TSP ID, address, city, state, or sub-agent..."
)

df_view = df.copy()

if search:
    s = search.lower()
    df_view = df_view[
        df_view.apply(
            lambda row: row.astype(str).str.lower().str.contains(s, na=False).any(),
            axis=1
        )
    ]


col1, col2, col3 = st.columns(3)

col1.metric("Stores Showing", len(df_view))
col2.metric("Selected TSP IDs", len(SELECTED_TSP_IDS))

if "Current 4MR%" in avg_df.columns:
    avg_4mr = clean_percent(avg_df["Current 4MR%"].iloc[0])
    col3.metric("Company Avg Current 4MR%", avg_4mr)
else:
    col3.metric("Company Avg Current 4MR%", "N/A")


styled_df = df_view.style.apply(
    highlight_percent_columns,
    axis=1
)

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)


csv = df_view.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="dlar_mr_dashboard_selected_tsp.csv",
    mime="text/csv"
)
