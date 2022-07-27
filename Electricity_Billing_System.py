import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="Billing System", layout="wide")
st.title("Departmental Electricity Billing System (IESCO Tariff-Based)")

# Sidebar inputs
st.sidebar.header("Enter Tariff Rates")
t1_tariff = st.sidebar.number_input("T1 Tariff Rate (Rs/unit)", min_value=0.0, step=0.1)
t2_tariff = st.sidebar.number_input("T2 Tariff Rate (Rs/unit)", min_value=0.0, step=0.1)
fc_surcharge_rate = st.sidebar.number_input("FC Surcharge Rate (Rs/unit)", min_value=0.0, step=0.1)
qtr_tariff_rate = st.sidebar.number_input("Qtr Tariff Rate (Rs/unit)", min_value=0.0, step=0.1)
fpa_rate = st.sidebar.number_input("FPA Rate (Rs/unit)", min_value=0.0, step=0.1)

apply_gst = st.sidebar.checkbox("Apply 18% GST on Base Bill", value=True)
apply_fpa = st.sidebar.checkbox("Apply FPA Charges", value=True)
apply_fpa_gst = st.sidebar.checkbox("Apply 18% GST on FPA", value=True if apply_fpa else False, disabled=not apply_fpa)

# Handling missing previous month logic
st.sidebar.markdown("### Handling Missing Data")
allow_missing_prev_bill = st.sidebar.checkbox("Allow bill calc even if previous month missing (use current reading)", value=False)
allow_missing_prev_fpa = st.sidebar.checkbox("Allow FPA calc even if previous FPA month missing (use current reading)", value=False)

# Upload file
uploaded_file = st.file_uploader("Upload Excel file with meter readings", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        # Detect available months
        month_columns = [col for col in df.columns if "T1" in col or "T2" in col]
        raw_months = list(set(col.split()[0] for col in month_columns))
        month_map = {m: pd.to_datetime("01-" + m, format="%d-%b-%y", errors="coerce") for m in raw_months}
        detected_months = sorted([m for m in raw_months if month_map[m] is not pd.NaT], key=lambda x: month_map[x])

                # --- Month-Year Selectors ---
        months_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        years_list = list(range(2020, 2031))

        st.sidebar.markdown("### Select Billing Month")
        bill_month = st.sidebar.selectbox("Month", months_list, index=6)  # Default to Jul
        bill_year = st.sidebar.selectbox("Year", years_list, index=years_list.index(2024))  # Default to 2024
        selected_bill_month = f"{bill_month}-{str(bill_year)[-2:]}"  # e.g., Jul-24

        st.sidebar.markdown("### Select FPA Month")
        fpa_month = st.sidebar.selectbox("FPA Month", months_list, index=6, key="fpa_month")
        fpa_year = st.sidebar.selectbox("FPA Year", years_list, index=years_list.index(2024), key="fpa_year")
        selected_fpa_month = f"{fpa_month}-{str(fpa_year)[-2:]}"  # e.g., Jul-24


        def get_previous_month(selected, all_months):
            idx = all_months.index(selected)
            return all_months[idx - 1] if idx > 0 else None

        selected_prev_month = get_previous_month(selected_bill_month, detected_months)
        fpa_prev_month = get_previous_month(selected_fpa_month, detected_months)

        if st.button("🔢 Calculate Bill"):
            if t1_tariff > 0 and t2_tariff > 0:
                t1_curr = f"{selected_bill_month} T1"
                t2_curr = f"{selected_bill_month} T2"
                t1_prev = f"{selected_prev_month} T1" if selected_prev_month else None
                t2_prev = f"{selected_prev_month} T2" if selected_prev_month else None

                if not allow_missing_prev_bill:
                    if not t1_prev or t1_prev not in df.columns or t2_prev not in df.columns:
                        raise ValueError(f"❌ Missing previous month reading for billing: {selected_prev_month}")

                df["T1 Units"] = (
                    df[t1_curr] - df[t1_prev] if t1_prev and t1_prev in df.columns
                    else df[t1_curr] if allow_missing_prev_bill
                    else 0
                ).fillna(0)

                df["T2 Units"] = (
                    df[t2_curr] - df[t2_prev] if t2_prev and t2_prev in df.columns
                    else df[t2_curr] if allow_missing_prev_bill
                    else 0
                ).fillna(0)

                df["Total Units"] = df["T1 Units"] + df["T2 Units"]
                df["T1 Bill"] = df["T1 Units"] * t1_tariff
                df["T2 Bill"] = df["T2 Units"] * t2_tariff
                df["FC Surcharge"] = df["Total Units"] * fc_surcharge_rate
                df["Qtr Tariff"] = df["Total Units"] * qtr_tariff_rate
                df["Base Bill"] = df["T1 Bill"] + df["T2 Bill"] + df["FC Surcharge"] + df["Qtr Tariff"]

                df["GST (18%)"] = df["Base Bill"] * 0.18 if apply_gst else 0.0
                df["Pre Total"] = df["Base Bill"] + df["GST (18%)"]

                fpa_t1_curr = f"{selected_fpa_month} T1"
                fpa_t2_curr = f"{selected_fpa_month} T2"
                fpa_t1_prev = f"{fpa_prev_month} T1" if fpa_prev_month else None
                fpa_t2_prev = f"{fpa_prev_month} T2" if fpa_prev_month else None

                if not allow_missing_prev_fpa:
                    if not fpa_t1_prev or fpa_t1_prev not in df.columns or fpa_t2_prev not in df.columns:
                        raise ValueError(f"❌ Missing previous month reading for FPA: {fpa_prev_month}")

                fpa_t1_units = (
                    df[fpa_t1_curr] - df[fpa_t1_prev] if fpa_t1_prev and fpa_t1_prev in df.columns
                    else df[fpa_t1_curr] if allow_missing_prev_fpa
                    else 0
                ).fillna(0)

                fpa_t2_units = (
                    df[fpa_t2_curr] - df[fpa_t2_prev] if fpa_t2_prev and fpa_t2_prev in df.columns
                    else df[fpa_t2_curr] if allow_missing_prev_fpa
                    else 0
                ).fillna(0)

                df["FPA Units"] = fpa_t1_units + fpa_t2_units
                df["FPA Charges"] = df["FPA Units"] * fpa_rate if apply_fpa else 0.0
                df["FPA GST (18%)"] = df["FPA Charges"] * 0.18 if (apply_fpa and apply_fpa_gst) else 0.0
                df["Total FPA (with GST)"] = df["FPA Charges"] + df["FPA GST (18%)"]
                df["Total Bill"] = df["Pre Total"] + df["Total FPA (with GST)"]

                df_display = df[[
                    "Department", "T1 Units", "T2 Units", "Total Units",
                    "T1 Bill", "T2 Bill", "FC Surcharge", "Qtr Tariff",
                    "Base Bill", "GST (18%)", "Pre Total",
                    "FPA Charges", "FPA GST (18%)", "Total FPA (with GST)",
                    "Total Bill"
                ]].round(2)

                st.subheader("📊 Calculated Units and Bills")
                st.dataframe(df_display, use_container_width=True)

                # 🔢 Summary (Inserted just after the table)
                st.subheader("🔢 Summary")
                st.markdown(f"**Total Units Consumed:** {df['Total Units'].sum():.2f} units")
                st.markdown(f"**Total FC Surcharge:** Rs. {df['FC Surcharge'].sum():,.2f}")
                st.markdown(f"**Total Qtr Tariff:** Rs. {df['Qtr Tariff'].sum():,.2f}")
                st.markdown(f"**Total FPA Charges (from {selected_fpa_month}):** Rs. {df['FPA Charges'].sum():,.2f}")
                if apply_gst:
                    st.markdown(f"**Total GST (18%) on Base:** Rs. {df['GST (18%)'].sum():,.2f}")
                if apply_fpa and apply_fpa_gst:
                    st.markdown(f"**Total FPA GST (18%):** Rs. {df['FPA GST (18%)'].sum():,.2f}")
                st.markdown(f"**✅ Final Total Bill (All Departments):** Rs. {df['Total Bill'].sum():,.2f}")

                st.subheader("📄 Download Options")

                csv_data = df_display.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", data=csv_data, file_name="iesco_bill_summary.csv", mime="text/csv")

                # --- Professional PDF Format ---
                class BillPDF(FPDF):
                    def header(self):
                        self.set_font("Arial", "B", 20)
                        self.cell(0, 10, "Electricity Bill", ln=True, align="C")
                        self.ln(3)
                        self.set_line_width(0.4)
                        self.line(10, self.get_y(), 200, self.get_y())
                        self.ln(5)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font("Arial", "I", 8)
                        self.cell(0, 10, f"Page {self.page_no()}", align="C")

                    def add_section(self, title, fields):
                        self.set_font("Arial", "B", 12)
                        self.set_fill_color(220, 220, 220)
                        self.cell(0, 6, title, ln=True, fill=True)
                        self.set_font("Arial", "", 11)
                        for label, val in fields.items():
                            self.cell(110, 8, label, border=1)
                            self.cell(80, 8, val, border=1, ln=True, align="C")
                        self.ln(4)

                pdf = BillPDF()
                pdf.set_auto_page_break(auto=True, margin=15)

                for _, row in df_display.iterrows():
                    pdf.add_page()
                    
                    # Title Section: Department and Bill Month
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, f"Department: {row['Department']}", ln=True)
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(0, 8, f"Bill Month: {selected_bill_month}", ln=True)  # ✅ Bill Month added
                    pdf.ln(2)

                    # T1 and T2 Units
                    pdf.add_section("T1 & T2 Units", {
                        "T1 Units": f"{row['T1 Units']:.2f}",
                        "T2 Units": f"{row['T2 Units']:.2f}",
                        "Total Units": f"{row['Total Units']:.2f}",
                    })

                    # Tariff Charges
                    pdf.add_section("Tariff Charges", {
                        "T1 Bill": f"Rs {row['T1 Bill']:,.2f}",
                        "T2 Bill": f"Rs {row['T2 Bill']:,.2f}",
                    })

                    # Surcharges
                    pdf.add_section("Surcharges", {
                        "FC Surcharge": f"Rs {row['FC Surcharge']:,.2f}",
                        "Qtr Tariff": f"Rs {row['Qtr Tariff']:,.2f}",
                    })

                    # Base Bill
                    pdf.add_section("Base Bill Summary", {
                        "Base Bill": f"Rs {row['Base Bill']:,.2f}",
                        "GST (18%)": f"Rs {row['GST (18%)']:,.2f}",
                        "Pre Total": f"Rs {row['Pre Total']:,.2f}",
                    })

                    # ✅ FPA Charges with selected FPA month in section title
                    pdf.add_section(f"FPA Charges ({selected_fpa_month})", {
                        "FPA Charges": f"Rs {row['FPA Charges']:,.2f}",
                        "FPA GST (18%)": f"Rs {row['FPA GST (18%)']:,.2f}",
                        "Total FPA (with GST)": f"Rs {row['Total FPA (with GST)']:,.2f}",
                    })

                    # Total Bill
                    pdf.add_section("Total Payable", {
                        "Total Bill": f"Rs {row['Total Bill']:,.2f}",
                    })


                pdf_buffer = io.BytesIO()
                pdf_buffer.write(pdf.output(dest='S').encode('latin-1'))
                pdf_buffer.seek(0)

                st.download_button("📥 Download PDF (All Departments)", data=pdf_buffer, file_name="iesco_department_bills.pdf", mime="application/pdf")
            else:
                st.warning("⚠️ Please enter both T1 and T2 tariff rates to proceed.")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
