# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/167F77QfvKWvB29a7ksmGcTnmtcdxQfvT
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from prophet import Prophet

# Set primary color
primary_color = '#CDCDCD'  # Replace with your desired color in hexadecimal format

# Set background color
background_color = '#CDCDCD'  # Replace with your desired color in hexadecimal format

# Set the overall theme
st.set_page_config(
    page_title="Stock Analysis App",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="auto",
)

# Apply the custom theme
css = f"""
    body {{
        color: {primary_color};
        background-color: {background_color};
    }}

    .css-1l02zno {{
        color: {primary_color};
    }}
"""
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# Set the page title
st.title("Stock Price Analysis App 📈")
st.write("Welcome to the *Stock Price Analysis App!* (to get the methodology explore the final section)")

st.write("1) In the first section of the app, you can input the ticker symbol of a company to access its time series data, decomposition analysis, and forecast.")# Get user input for stock symbol
stock_symbol = st.text_input("Enter stock symbol (e.g., MDLZ)")

# Check if the stock symbol is provided
if stock_symbol:
    # Suppress the FutureWarning messages from the yahooquery package
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # Define the start and end dates
    start_date = "2018-01-01"
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Get the historical stock data from Yahoo Finance
    stock_data = yf.download(stock_symbol, start=start_date, end=today_date)

    # Resample the data by year-month
    stock_data = stock_data.resample("M").last()

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(stock_data["Close"], color='slateblue')

    # Set the axis labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Average Close')
    ax.set_title(f'{stock_symbol} price dynamic')

    # Rotate the x-axis labels by 45 degrees
    plt.xticks(rotation=45)

    # Display the plot in Streamlit
    st.pyplot(fig)

        # Generate monthly dates for forecasting
    def generate_monthly_dates(year):
        current_date = datetime.now().date()
        start_date = pd.to_datetime(f'{year}-01-01')
        end_date = pd.to_datetime(current_date)
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        df = pd.DataFrame({'Date': dates})
        return df

    # Load the data and preprocess
    df_fcast = stock_data[['Close']]

    # Prepare the data for Prophet
    df_prophet = df_fcast[['Close']].rename(columns={'Close': 'y'}).reset_index()
    df_prophet.rename(columns={'Date': 'ds'}, inplace=True)

    # Initialize and fit the Prophet model
    model = Prophet()
    model.fit(df_prophet)

    # Generate future dates for forecasting
    future = model.make_future_dataframe(freq='M', periods=12)  # Forecasting for the next 12 months

    # Make predictions
    forecast = model.predict(future)

    # Set the title for the second part
    st.subheader('Decomposition of time series and forecast with Prophet package')

    # Visualize the forecast components
    fig_comp = model.plot_components(forecast)
    st.pyplot(fig_comp)

    # Visualize the forecast
    fig_forecast = model.plot(forecast)
    st.pyplot(fig_forecast)

    # Show the forecasted values
    forecast_df = forecast[['ds', 'yhat']].rename(columns={'yhat': f'{stock_symbol}_forecast', 'ds': 'Date'})[-12:]
    st.write(forecast_df)

st.write("2) In the second section, you can input a list of ticker symbols to test the consistency of your portfolio.")
# Get user input for portfolio symbols
portfolio_symbols = st.text_input("Enter portfolio symbols (comma-separated, e.g., AAPL,BAC,CVX,KO,AXP,KHC,MCO)")

# Check if the portfolio symbols are provided
if portfolio_symbols:
    # Split the input string into a list of symbols
    symbols = [symbol.strip() for symbol in portfolio_symbols.split(',')]

    # Suppress the FutureWarning messages from the yahooquery package
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # Define the year filter
    year_filter = 2019

    # Create an empty DataFrame to store the monthly data for all symbols
    monthly_data_all = pd.DataFrame()

    # Loop through each symbol and retrieve the historical stock price data
    for symbol in symbols:
        # Get historical stock price data for the current symbol
        stock_data = yf.Ticker(symbol).history(period='max')

        # Aggregate the data at a monthly level and calculate the average and last closing prices
        monthly_data = stock_data.resample('M').agg({'Close': ['mean', 'last']}).reset_index()

        # Extract the symbol name from the symbol string and add it as a column to the DataFrame
        monthly_data['Symbol'] = symbol

        # Append the monthly data for the current symbol to the monthly_data_all DataFrame
        monthly_data_all = monthly_data_all.append(monthly_data)

    # Rename the columns for readability
    monthly_data_all.columns = ['Date', 'Average Close', 'Last Close', 'Symbol']

    # Extract the year, month, and day from the 'Date' column
    monthly_data_all['Year'] = monthly_data_all['Date'].dt.year
    monthly_data_all['Month'] = monthly_data_all['Date'].dt.month
    monthly_data_all['Day'] = monthly_data_all['Date'].dt.day

    # Filter the data to include only years 2000 and later
    monthly_data_all = monthly_data_all[monthly_data_all['Year'] >= year_filter]

    # Set the figure size
    plt.figure(figsize=(10, 6))

    # Plot the data
    for symbol in symbols:
        # Filter the data for the current symbol and for years 2000 and later
        data = monthly_data_all[(monthly_data_all['Symbol'] == symbol) & (monthly_data_all['Year'] >= year_filter)]

        # Plot the data for the current symbol
        plt.plot(data['Date'], data['Average Close'], label=symbol)

    # Set the axis labels and legend
    plt.xlabel('Date')
    plt.ylabel('Average Close')
    plt.legend()
    plt.title(f'Stock price since {year_filter}')

    # Rotate the x-axis labels by 45 degrees
    plt.xticks(rotation=45)

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Standarized and differenced dataset to further correlation
    df = pd.pivot_table(monthly_data_all, values='Average Close', index=['Year', 'Month'],
                        columns=['Symbol']).reset_index().drop(columns=['Year', 'Month'])
    # Diff
    df = df.diff().drop(index=0)

    # Create a StandardScaler object
    scaler = StandardScaler()

    # Fit and transform the DataFrame
    df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    # Compute the correlation matrix
    corr_matrix = df.corr()

    # Plot the correlation matrix with the custom color map
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True)
    plt.title('Portfolio Correlation')

    # Display the plot in Streamlit
    st.pyplot(plt)

st.write("Bonus: To get easly a ticker look at this table.")

def display_company_table():
    # Define the company data
    company_data = {
        'Company Name': ['Apple Inc.', 'Microsoft Corporation', 'Amazon.com Inc.', 'Alphabet Inc.', 'Meta Platforms',
                         'Berkshire Hathaway Inc.', 'Tesla Inc.', 'JPMorgan Chase & Co.', 'Johnson & Johnson', 'Visa Inc.'],
        'Ticker': ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'BRK.A', 'TSLA', 'JPM', 'JNJ', 'V']
    }

    # Create a DataFrame from the company data
    df = pd.DataFrame(company_data)

    # Display the DataFrame as a table in Streamlit
    st.table(df)

# Run the function to display the company table
display_company_table()

st.markdown("---")
st.write("The methodology summarized:")
st.write("- The app was developed using python and streamlit.")
st.write("- The historical stock data is retrieved from Yahoo Finance, resampled on a monthly basis.")
st.write("- The data is preprocessed and prepared for the Prophet package, which is a time series library.")
st.write("- The Prophet model is initialized, fitted with the historical data,and used to make predictions.")
st.write("- For the second part, the dataset is standardized and differenced to further analyze with correlation matrix.")
st.markdown("---")
st.markdown("Created by Oscar Gomez - oscar.gomezr0414@gmail.com")
