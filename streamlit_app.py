import os
import pandas as pd
import streamlit as st
from src import Data

# Set Streamlit page configuration
st.set_page_config(page_title="Machine Data Overview", layout="wide")

# Create a range of data for the plot
end = pd.Timestamp.now().normalize()
start = pd.Timestamp("06-06-2024").normalize()

# Initialize the DataFrames
df_usage = pd.DataFrame(index=pd.date_range(start=start, end=end))
df_storage = pd.DataFrame(index=pd.date_range(start=start, end=end))

# Load data using the Data API
api = Data(api_key=os.getenv("API_KEY"), api_token=os.getenv("API_TOKEN"))
df_tot_storage, df_tot_usage = api.get_summary(start=start, end=end)

# Process the data for each machine
machines = df_tot_storage["hostnode_id"].value_counts()
for machine in machines.index:
    _df_storage = df_tot_storage[df_tot_storage["hostnode_id"] == machine]
    _df_storage = _df_storage.groupby(_df_storage.index).sum()

    _df_usage = df_tot_usage[df_tot_usage["hostnode_id"] == machine]
    _df_usage = _df_usage.groupby(_df_usage.index).sum()

    df_storage[machine] = _df_storage["total_amount"]
    df_usage[machine] = _df_usage["total_amount"]

df_usage.fillna(0, inplace=True)
df_storage.fillna(0, inplace=True)
df_total = df_usage + df_storage


TOTAL_MACHINE = len(machines)
_df_total = pd.DataFrame({
    "usage": df_usage.sum(axis=1),
    "storage": df_storage.sum(axis=1),
    "total": df_total.sum(axis=1)
}, index=df_total.index)


# Plot the total cumulative sum across all machines
st.subheader("Total Cumulative Sum Across All Machines")


_df_total_cumsum = _df_total.cumsum()
st.line_chart(_df_total_cumsum)
