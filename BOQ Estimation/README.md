# BOQ Estimation

This folder contains a Python-based automation tool designed to help estimate Bills of Quantities (BOQ) for construction-related projects. It was originally developed to support cost estimation across civil, electrical, and plumbing domains.

## Contents

- `app_v1.1.py`: The initial version of the application containing the basic estimation logic.
- `app_v1.2.py`: An improved version with enhanced UI, dynamic search, Excel/PDF report generation, and session-based item tracking.
- `item_schedule.xlsx`: The source data file that includes item descriptions, units, and rates for different categories (civil, electrical, plumbing).

## Features in app_v1.2

- Upload an Excel file containing structured BOQ data across multiple sheets.
- Search for items by name and add/update them dynamically.
- Automatically calculate total cost based on quantity and rate.
- Generate detailed BOQ tables viewable within the interface.
- Export final reports in Excel or PDF format.
- Supports item deletion and live grand total updates.
- Responsive and clean Streamlit interface with minimal styling for ease of use.

## Technology Stack

- **Python**
- **Streamlit** (for the user interface)
- **Pandas** (for data handling)
- **FPDF** (for PDF export)

## Note

This version is a close reproduction of an internal project developed four years ago for practical construction automation. The data used here is for demonstration only and does not represent actual commercial use.

