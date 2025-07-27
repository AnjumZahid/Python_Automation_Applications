import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from pathlib import Path

# ---------- BOQ ITEM SETUP ----------
item_units = {
    "Bricks": "pieces",
    "Cement": "bags",
    "Steel Rod": "kg",
    "Sand": "cft",
    "Crush": "cft"
}

st.title("BOQ Generator")
now = datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD

# ---------- SESSION STATE ----------
if "boq_data" not in st.session_state:
    st.session_state.boq_data = []

# ---------- FORM ----------
with st.form("boq_form"):
    description = st.selectbox("Select Item", list(item_units.keys()))
    quantity = st.number_input("Enter Quantity", min_value=0.0, format="%.2f")
    unit_price = st.number_input("Enter Unit Price", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add/Update Item")

    if submitted:
        unit = item_units[description]
        total = quantity * unit_price

        # Check if item already exists to update
        updated = False
        for item in st.session_state.boq_data:
            if item["Item Name"] == description:
                item["Quantity"] = quantity
                item["Unit Price"] = unit_price
                item["Total"] = total
                updated = True
                break

        if not updated:
            st.session_state.boq_data.append({
                "Item Name": description,
                "Quantity": quantity,
                "Unit": unit,
                "Unit Price": unit_price,
                "Total": total
            })

        st.success(f"Item '{description}' added/updated successfully!")

# ---------- DISPLAY BOQ ----------
if st.session_state.boq_data:
    df = pd.DataFrame(st.session_state.boq_data)
    df.index = df.index + 1
    df.index.name = "Sr#"

    total_sum = df["Total"].sum()

    st.dataframe(df.style.format({
        "Quantity": "{:.2f}",
        "Unit Price": "{:.2f}",
        "Total": "{:.2f}"
    }), use_container_width=True)

    st.markdown(f"### 🧮 Grand Total: Rs. {total_sum:,.2f}")

    # ---------- SAVE EXCEL ----------
    if st.button("📥 Download Excel"):
        download_path = Path.cwd() / f"BOQ_{now}.xlsx"
        df_reset = df.reset_index()
        df_reset.to_excel(download_path, index=False)
        st.success(f"Excel saved to current directory as {download_path.name}")

    # ---------- GENERATE PDF ----------
    if st.button("🖨️ Print PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Bill of Quantities", ln=True, align="C")
        pdf.ln(5)

        # Define column widths (based on number of columns)
        col_widths = [15, 40, 25, 20, 30, 30]
        total_table_width = sum(col_widths)

        # Table headers
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(200, 220, 255)
        pdf.set_x((pdf.w - total_table_width) / 2)
        headers = ["Sr#", "Item Name", "Quantity", "Unit", "Unit Price", "Total"]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
        pdf.ln()

        # Table rows
        pdf.set_font("Arial", "", 10)
        for idx, row in df.reset_index().iterrows():
            pdf.set_x((pdf.w - total_table_width) / 2)
            pdf.cell(col_widths[0], 10, str(int(row["Sr#"])), border=1, align="C")
            pdf.cell(col_widths[1], 10, row["Item Name"], border=1)
            pdf.cell(col_widths[2], 10, f"{row['Quantity']:.2f}", border=1, align="C")
            pdf.cell(col_widths[3], 10, row["Unit"], border=1, align="C")
            pdf.cell(col_widths[4], 10, f"{row['Unit Price']:.2f}", border=1, align="C")
            pdf.cell(col_widths[5], 10, f"{row['Total']:.2f}", border=1, align="C")
            pdf.ln()

        # Final Grand Total row
        pdf.set_x((pdf.w - total_table_width) / 2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(sum(col_widths[:-1]), 10, "Grand Total", border=1, align="R")
        pdf.cell(col_widths[-1], 10, f"{total_sum:.2f}", border=1, align="C")

        # Save PDF
        pdf_path = Path.cwd() / f"BOQ_{now}.pdf"
        pdf.output(str(pdf_path))
        st.success(f"PDF saved to current directory as {pdf_path.name}")

else:
    st.info("Please add items to generate BOQ.")
