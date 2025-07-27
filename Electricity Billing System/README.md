# Electricity Billing System

This folder contains a departmental electricity billing automation tool built using Python and Streamlit. The tool is designed to calculate electricity bills for multiple departments based on uploaded monthly meter readings, following IESCO tariff structures. The system can generate both detailed CSV summaries and printable PDF reports.

## Contents

- `Electricity_Billing_System.py`: Main Streamlit application script that computes the bill based on user-defined tariff rates and uploaded readings.
- `Department_Meter_Readings_Jul24_Jun25.xlsx`: Sample dataset containing departmental meter readings from July 2024 to June 2025.

## Key Features

- Upload an Excel sheet containing departmental T1 and T2 readings for each month.
- Input tariff rates for T1, T2, FC surcharge, QTR tariff, and FPA via an intuitive sidebar.
- Handles optional inclusion of:
  - GST on base bill
  - FPA charges and FPA GST
- Dynamically calculates:
  - Units consumed per tariff category
  - Base bill and surcharges
  - FPA components
  - GST (on base and FPA)
  - Final total payable per department
- Includes checks for missing previous month readings, with optional fallback logic.
- Generates:
  - CSV summary of department-wise billing
  - Professionally formatted PDF reports for each department

## Technologies Used

- **Python**
- **Streamlit** for interactive web UI
- **Pandas** for data processing
- **FPDF** for PDF report generation

## Notes

- This application is a working copy inspired by an internal billing solution developed around 3 years ago.
- All data used here is sample and for demonstration purposes only.
