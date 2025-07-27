import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

# ----------- Load Items from Excel ------------
@st.cache_data
def load_all_items(excel_path):
    xl = pd.ExcelFile(excel_path)
    all_items = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        df = df.dropna()
        if df.shape[1] >= 3:
            for _, row in df.iterrows():
                desc = str(row.iloc[0]).strip()
                unit = str(row.iloc[1]).strip()
                try:
                    rate = float(row.iloc[2])
                except:
                    continue
                all_items.append({"desc": desc, "unit": unit, "rate": rate})
    return all_items

# ---------- Session State ----------
if "boq_data" not in st.session_state:
    st.session_state.boq_data = []

# ---------- Streamlit Page Settings ----------
st.set_page_config(layout="wide")
st.markdown("""
<style>
    .main > div {
        padding-left: 3% !important;
        padding-right: 3% !important;
        border-left: 2px solid #e0e0e0;
        border-right: 2px solid #e0e0e0;
    }

    .stTextInput > div > input {
        padding: 0.5rem 0.75rem;
    }

    /* Compact and wide uploader styling */
    div[data-testid="stFileUploader"] {
        width: 100% !important;
    }

    div[data-testid="stFileUploader"] > div {
        padding: 0px 4px !important;
        height: 32px !important;
        min-height: 32px !important;
        display: flex;
        align-items: center;
    }

    div[data-testid="stFileUploader"] input[type="file"] {
        height: 28px !important;
        font-size: 13px !important;
        padding: 2px !important;
    }

    label[for^="file_uploader"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Title and Upload (Same Row) ----------
title_col, upload_col = st.columns([8, 2])
with title_col:
    st.markdown("<h1 style='text-align: left;'>BOQ Estimator</h1>", unsafe_allow_html=True)
with upload_col:
    excel_file = st.file_uploader("📁", type=["xlsx", "xls"], label_visibility="collapsed")

# ---------- Main Logic ----------
if excel_file:
    items = load_all_items(excel_file)
    all_descriptions = [item["desc"] for item in items]

    if "search_term" not in st.session_state:
        st.session_state.search_term = ""

    st.markdown("### 🔍 Search Items")
    st.session_state.search_term = st.text_input("", value=st.session_state.search_term)

    search = st.session_state.search_term.lower()
    matched_items = [d for d in all_descriptions if search in d.lower()]

    if matched_items:
        st.markdown("### ➕ Add or Update Item")
        with st.form("add_item_form"):
            form_col1, form_col2, form_col3, form_col4 = st.columns([4, 2, 2, 2])
            with form_col1:
                selected = st.selectbox("Select Matching Item", matched_items)
            matched = next((i for i in items if i["desc"] == selected), None)
            unit = matched["unit"]
            rate = matched["rate"]
            with form_col2:
                quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
            with form_col3:
                st.markdown(f"**Unit:** `{unit}`  \n**Rate:** Rs. `{rate:.2f}`")
            with form_col4:
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("✅ Add / Update Item")

            if submitted:
                total = quantity * rate
                existing_index = next((i for i, item in enumerate(st.session_state.boq_data)
                                       if item["Item Name"] == selected), None)
                new_row = {
                    "Item Name": selected,
                    "Quantity": quantity,
                    "Unit": unit,
                    "Unit Price": rate,
                    "Total": total
                }
                if existing_index is not None:
                    st.session_state.boq_data[existing_index] = new_row
                    st.success(f"✅ '{selected}' updated.")
                else:
                    st.session_state.boq_data.append(new_row)
                    st.success(f"✅ '{selected}' added.")
                st.rerun()
    else:
        if search:
            st.warning("No matching item found.")
else:
    st.info("📁 Please upload an Excel file to begin.")

# ---------- Show Table & Total ----------
if st.session_state.boq_data:
    df = pd.DataFrame(st.session_state.boq_data)
    df.index += 1
    total_sum = df["Total"].sum()

    col_title, col_gt = st.columns([6, 1])
    with col_title:
        st.markdown("<h5 style='margin:0 0 8px 0; font-size:14px;'>📑 Current BOQ Table</h5>", unsafe_allow_html=True)
    with col_gt:
        st.markdown(f"""
            <div style='border:1px solid #4CAF50; border-radius:6px;
                        padding:4px; text-align:center; background-color:#f0fff0; margin-bottom:10px;'>
                <div style='font-size:13px; font-weight:600;'>Grand Total</div>
                <div style='font-size:13px; color:green;'>Rs. {total_sum:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.dataframe(
        df.style.format({
            "Quantity": "{:.2f}",
            "Unit Price": "{:.2f}",
            "Total": "{:.2f}"
        }),
        use_container_width=True,
        height=450
    )

    col_del1, col_del2 = st.columns([3, 1])
    with col_del1:
        delete_idx = st.number_input("Enter Sr# to delete", min_value=1, max_value=len(df), step=1)
    with col_del2:
        if st.button("❌ Delete Selected Item"):
            st.session_state.boq_data.pop(delete_idx - 1)
            st.rerun()

    st.markdown(f"### 🧮 Running Grand Total: Rs. {total_sum:,.2f}")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")

    if st.button("📥 Download Excel"):
        excel_path = Path.cwd() / f"BOQ_{now}.xlsx"
        df.to_excel(excel_path, index_label="Sr#")
        st.success(f"✅ Excel saved: {excel_path.name}")

    if st.button("🖨️ Print PDF"):
        pdf = FPDF()
        pdf.add_page()
        # pdf.set_font("Arial", size=12)
        pdf.set_font("Arial", style="B", size=18)  # Bold + larger size
        pdf.cell(200, 10, "Bill of Quantities", ln=True, align="C")
        pdf.ln(5)

        col_widths = [15, 55, 25, 20, 30, 30]
        headers = ["Sr#", "Item Name", "Quantity", "Unit", "Unit Price", "Total"]
        total_table_width = sum(col_widths)

        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(200, 220, 255)
        pdf.set_x((pdf.w - total_table_width) / 2)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        for idx, row in df.iterrows():
            pdf.set_x((pdf.w - total_table_width) / 2)
            pdf.cell(col_widths[0], 10, str(idx), border=1, align="C")
            pdf.cell(col_widths[1], 10, row["Item Name"][:25], border=1)
            pdf.cell(col_widths[2], 10, f"{row['Quantity']:.2f}", border=1, align="C")
            pdf.cell(col_widths[3], 10, row["Unit"], border=1, align="C")
            pdf.cell(col_widths[4], 10, f"{row['Unit Price']:.2f}", border=1, align="C")
            pdf.cell(col_widths[5], 10, f"{row['Total']:.2f}", border=1, align="C")
            pdf.ln()

        pdf.set_x((pdf.w - total_table_width) / 2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(sum(col_widths[:-1]), 10, "Grand Total", border=1, align="R")
        pdf.cell(col_widths[-1], 10, f"{total_sum:.2f}", border=1, align="C")

        pdf_path = Path.cwd() / f"BOQ_{now}.pdf"
        pdf.output(str(pdf_path))
        st.success(f"✅ PDF saved: {pdf_path.name}")
