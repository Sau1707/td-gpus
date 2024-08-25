import streamlit as st
import threading
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Function to simulate data generation
def simulate_data_generation():
    while True:
        # Generate some random data
        new_data = {
            'timestamp': [datetime.now()],
            'value': [np.random.randint(1, 100)]
        }

        # Convert to DataFrame
        new_df = pd.DataFrame(new_data)

        # Append to the global data cache
        global data_cache
        if data_cache is None:
            data_cache = new_df
        else:
            data_cache = pd.concat([data_cache, new_df], ignore_index=True)

        # Wait for 5 minutes (300 seconds) before the next data generation
        time.sleep(60)

# Initialize an empty cache
data_cache = None

# Start the background thread
threading.Thread(target=simulate_data_generation, daemon=True).start()

# Streamlit UI
st.title('Simulated Real-time Data Viewer')

# Display the data in the app
if data_cache is not None:
    st.dataframe(data_cache)
else:
    st.write('Data is loading... Please wait.')

