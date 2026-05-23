# DLAR 4MR Streamlit Dashboard

This Streamlit app shows only selected TSP IDs from the DLAR Google Sheet.

## Columns shown

- Door TSP
- Address
- Sub-Agent Name
- Current 4MR%

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud setup

1. Create a GitHub repository.
2. Upload these files:
   - app.py
   - requirements.txt
3. Go to Streamlit Community Cloud.
4. Click "New app".
5. Select the GitHub repository.
6. Main file path: app.py
7. Deploy.

## Important

Your Google Sheet must be shared as:

Anyone with the link → Viewer

Otherwise Streamlit cannot read the CSV export.
