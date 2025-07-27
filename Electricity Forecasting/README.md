# Electricity Forecasting

This folder contains two predictive modeling notebooks focused on electricity consumption forecasting using different feature sets. The models are built using Python and standard data science libraries such as Pandas, scikit-learn, and Matplotlib. These tools are intended to estimate future electricity consumption based on historical consumption patterns and environmental or usage factors.

## Contents

- `Energy_Forecasting_temp_vs_units.ipynb`: Predicts electricity units consumed based on ambient temperature using a linear regression model.
- `Energy_Forecasting_tech_non_tech.ipynb`: Uses separate technical and non-technical consumption figures to estimate total units consumed, and includes predictions across multiple feeders.
- `dataset_temp_vs_units/`: Contains Excel data for temperature and electricity usage by feeder.
- `dataset_tech_non_tech/`: Contains Excel data with technical and non-technical consumption breakdowns and corresponding units consumed.

## Notebook Descriptions

### 1. Energy_Forecasting_temp_vs_units.ipynb

- **Data Input**: `temperature_vs_units_feeders.xlsx`
- **Features Used**: Temperature, Squared Temperature
- **Model**: Linear Regression
- **Workflow**:
  - Reads and processes temperature-based dataset
  - Engineers a non-linear temperature term (`Temperature²`)
  - Trains and evaluates a regression model
  - Performs a prediction using a single temperature input
- **Output**: Predicted units consumed based on temperature

### 2. Energy_Forecasting_tech_non_tech.ipynb

- **Data Input**: `dataset tech_non_tech.xlsx`
- **Features Used**: Technical Consumption, Non-Technical Consumption
- **Model**: Linear Regression with feature scaling
- **Workflow**:
  - Reads departmental consumption data
  - Scales features and trains a regression model
  - Evaluates model performance using R² and MSE
  - Provides visual comparison between actual and predicted values
  - Simulates multiple feeder predictions with optional adjustment for temperature-based influence
- **Output**: Department-wise and cumulative unit predictions

## Technologies Used

- Python 3.x
- pandas, numpy
- scikit-learn
- matplotlib
- Jupyter Notebook

## Notes

- These notebooks were created as exploratory copies of earlier energy estimation models developed internally.
- The datasets used are anonymized and for demonstration purposes only.
