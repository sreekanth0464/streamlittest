# Import the necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import warnings
from io import StringIO
import boto3
import datetime
import seaborn as sns 

# Disable all warnings, including deprecation warnings
warnings.filterwarnings('ignore') 

# Set the Streamlit page configuration for the Dashboard with a wide layout and a chart icon
st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")

# Custom CSS styling
st.markdown(
    """
    <style>
    body { background-color: #ffffff; }

    [data-testid=metric-container] { box-shadow: 0 0 4px #686664; padding: 10px; }
    .plot-container>div { box-shadow: 0 0 2px #070505; padding: 5px; border-color: #000000; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.2rem; color: rgb(0, 0, 0); border-color: #000000; }
    .sidebar-content { color: white; }
    
    [data-testid=stSidebar] { color: white; }
    
    [div[data-testid="metric-container"] {{
                background-color: #333333;
                border-left: 5px solid #444444;
                border: 1px solid #555555;
                box-shadow: 0 0 4px #000000;
                padding: 10px;
                border-radius: 5px;
                color: #FFFFFF;}}
    """,
    unsafe_allow_html=True
)

class Dashboard:
    def __init__(self,Revenue_df, customers_df, subscriptions_df, payment_df, financial_df):
        self.Revenue_df = Revenue_df
        self.customers_df = customers_df
        self.subscriptions_df = subscriptions_df
        self.payment_df = payment_df
        self.financial_df = financial_df
    
    def Summary(self,Revenue_df, customers_df, subscriptions_df, payment_df, financial_df):
        # Assuming `Revenue_df` is your DataFrame with a 'created' column
        Revenue_df['created'] = pd.to_datetime(Revenue_df['created'], errors='coerce')

        st.markdown("---")
        # New users     - current day and last 7 days
        today = Revenue_df['created'].dt.date.max()
        last7days = today - datetime.timedelta(days=7)
        last30days = today - datetime.timedelta(days=30)
        new_users_today = Revenue_df[Revenue_df['created'].dt.date == today]['customer_id'].nunique()
        new_users_last7days = Revenue_df[(Revenue_df['created'].dt.date >= last7days) & (Revenue_df['created'].dt.date < today)]['customer_id'].nunique()
        new_users_last30days = Revenue_df[(Revenue_df['created'].dt.date >= last30days) & (Revenue_df['created'].dt.date < today)]['customer_id'].nunique()

        # New subscriptions - current day and last 7 days
        last7days = today - datetime.timedelta(days=7)
        last30days = today - datetime.timedelta(days=30)
        new_sub_today = Revenue_df[Revenue_df['created'].dt.date == today]['subscription'].nunique()
        new_sub_last7days = Revenue_df[(Revenue_df['created'].dt.date >= last7days) & (Revenue_df['created'].dt.date < today)]['subscription'].nunique()
        new_sub_last30days = Revenue_df[(Revenue_df['created'].dt.date >= last30days) & (Revenue_df['created'].dt.date < today)]['subscription'].nunique()


        total1, total2 , total3 = st.columns(3, gap='small')
        with total1 :
            st.info('New Users')
            st.metric(label="New users today", value=f" {new_users_today}")
    
        with total2 :
            st.info('New Users in last 7 days')
            st.metric(label="New users in last 7 days", value=f"{new_users_last7days}")

        with total3 :
            st.info('New Users in last 30 days')
            st.metric(label="New users in last 30 days", value=f"{new_users_last30days}")
        
        total1, total2 , total3 = st.columns(3, gap='small')
        with total1 :
            st.info('New Subscriptions')
            st.metric(label="New Subscriptions today", value=f"{new_sub_today}")
        
        with total2 :
            st.info('New Subscriptions in last 7 days')
            st.metric(label="New Subscriptions in last 7 days", value=f" {new_sub_last7days}")

        with total3 :
            st.info('New Subscriptions in last 30 days')
            st.metric(label="New Subscriptions in last 30 days", value=f" {new_sub_last30days}")
        

    def Revenue(self,Revenue_df):
        # Use Streamlit's markdown function to add a style tag to hide the Streamlit element toolbar
        
        st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        # Sidebar
        st.sidebar.header("Select Date Range:")
        # Get the start date and end date from the sidebar
        Revenue_df['created'] = pd.to_datetime( Revenue_df['created'], errors='coerce')
        start_date = st.sidebar.date_input("Start date", Revenue_df["created"].min())
        end_date = st.sidebar.date_input("End date", Revenue_df["created"].max())

        # Convert the start date and end date to datetime format
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter the dataframe based on the start date and end date
        filtered_df = Revenue_df.query("created >= @start_date and created <= @end_date")

        # 1. Total Transaction Amount (sum of all invoice amounts)
        total_transaction_amount = filtered_df['total_invoice_amount'].sum()

        # 2. Total Subscription Amount (assuming 'subscription' keyword in description)
        subscription_df = filtered_df[filtered_df['description'].str.contains('subscription', case=False, na=False)]
        total_subscription_amount = subscription_df['total_invoice_amount'].sum()

        # 3. Total Products Amount (rows where 'description' does NOT contain 'subscription')
        product_df = filtered_df[~filtered_df['description'].str.contains('subscription', case=False, na=False)]
        total_product_amount = product_df['total_invoice_amount'].sum()

        # 4. Tax Amount (assuming 'tax_info_type' provides relevant details)
        tax_amount = filtered_df['tax'].sum()  # Adjust this to the actual tax column

        # Display metrics for all required amounts
        total1, total2  = st.columns(2, gap='small')
        with total1 :
            st.info('Total Amount',  icon="💰")
            st.metric(label="Total Transaction Amount", value=f"$ {total_transaction_amount:,.2f}")
        with total2:
            st.info('Total Subscription',icon="💰")
            st.metric(label="Total Subscription Amount", value=f"$ {total_subscription_amount:,.2f}")
        
        total1,total2 = st.columns(2, gap='small')
        with total1:
            st.info('Total Product', icon="💰")
            st.metric(label="Total Product Amount", value=f"$ {total_product_amount:,.2f}")
        with total2:
            st.info('Total Tax', icon="💰") 
            st.metric(label="Total Tax Amount", value=f"$ {tax_amount:,.2f}")

        with st.expander("VIEW DATA"):
            showData = st.multiselect('Filter: ', filtered_df.columns, default=[
                'created', 'customer_id', 'email', 'phone', 'name',  'subscription', 'invoice_number',
                'description', 'quantity', 'currency', 'line_item_amount',
                'total_invoice_amount', 'discount', 'fee', 'tax', 'net_amount'
            ])
            st.dataframe(filtered_df[showData])

        # GEAPH 1 
        filtered_df['year_month'] = filtered_df['created'].dt.to_period('M')
        monthly_net_amount = filtered_df.groupby('year_month')['net_amount'].sum().reset_index() # Group the filtered dataframe by year_month and sum the net_amount column
        monthly_net_amount['year_month'] = monthly_net_amount['year_month'].astype(str) # Convert the year_month column to string type
        fig_1 = px.bar(monthly_net_amount, x='year_month', y='net_amount', title="Total Net Amount by Month",
                    labels={'year_month': 'Month', 'net_amount': 'Total Net Amount ($)'})# Create a bar plot using the Plotly Express library
        
        # GEAPH 2  
        monthly_tax = filtered_df.groupby('year_month')['tax'].sum().reset_index() # Group the filtered dataframe by year_month and sum the tax values
        monthly_tax['year_month'] = monthly_tax['year_month'].astype(str) # Convert the year_month column to string type
        fig_2 = px.bar(monthly_tax, x='tax', y='year_month', title="Total Tax by Month",
            labels={'year_month': 'Month', 'tax': 'Total Tax ($)'}) # Create a pie chart using the monthly_tax dataframe, with the tax values as the values, the year_month as the names, and the title as "Total Tax by Month"


        total1, total2 = st.columns(2, gap='small')
        with total1:
            st.plotly_chart(fig_1)

        with total2:
            st.plotly_chart(fig_2)

        # Graph 3
        filtered_df['total_invoice_amount'] = filtered_df['total_invoice_amount'].astype(int)# Convert the 'total_invoice_amount' column to integer type
        top_customers = filtered_df.groupby('email')['total_invoice_amount'].sum().reset_index()# Group the data by 'customer_id' and sum the 'total_invoice_amount' for each customer
        top_customers = top_customers.sort_values(by='total_invoice_amount', ascending=False).head(5)# Sort the data by 'total_invoice_amount' in descending order and select the top 10 customers
        fig_3 = px.pie(top_customers, names='email', values='total_invoice_amount', title='Top 5 Customers by Revenue')# Create a pie chart using Plotly Express with 'customer_id' on the x-axis and 'total_invoice_amount' on the y-axis

        # Graph 4
        revenue_by_product = product_df.groupby('description')['total_invoice_amount'].sum().reset_index() # Group the data by 'description' and sum the 'total_invoice_amount' for each product
        top_revenue_by_product = revenue_by_product.sort_values(by='total_invoice_amount', ascending=False).head(5) # Sort the values and get the top 10
        fig_4 = px.pie(top_revenue_by_product, values='total_invoice_amount', names='description', title='Top 5 Products by Revenue') # Create the pie chart visualization

        total1 ,total2 = st.columns(2, gap='small')
        with total1:
            st.plotly_chart(fig_3)

            with st.expander("VIEW DATA"): # Create an expander to display the data
                st.dataframe(top_customers)  # Display the top customers dataframe

        with total2:
            st.plotly_chart(fig_4, use_container_width=True)

            with st.expander("VIEW DATA"):
                st.dataframe(top_revenue_by_product)
        
        # Graph 5
        filtered_df['month'] = filtered_df['created'].dt.strftime('%Y-%m') # Convert the 'created' column to a string in the format 'YYYY-MM'
        tax_fee = filtered_df.groupby('month').agg({'tax': 'sum', 'fee': 'sum'}).reset_index() # Group the data by month and sum the 'tax' and 'fee' columns
        fig_5 = px.bar(tax_fee, x='month', y=['tax', 'fee'], title='Tax and Fee Analysis Over Time', labels={'month': 'Month'}) # Create a bar chart with the 'month' on the x-axis and 'tax' and 'fee' on the y-axis
        fig_5.update_xaxes(type='category') # Ensure the x-axis is treated as categorical
        st.plotly_chart(fig_5)

        with st.expander("VIEW DATA"):
            st.dataframe(tax_fee)

        # Graph 6
        subscription_analysis = filtered_df['subscription'].value_counts().reset_index() # Create a dataframe with the count of each subscription type
        subscription_analysis.columns = ['Subscription', 'Count'] # Rename the columns of the dataframe
        fig_6 = px.bar(subscription_analysis, x='Subscription', y='Count', title='Revenue by Subscription') # Create a bar chart with the subscription type on the x-axis and the count on the y-axis
        st.plotly_chart(fig_6)

        with st.expander("VIEW DATA"):
            st.dataframe(subscription_analysis)

        Revenue_df['created'] = pd.to_datetime(Revenue_df['created'], errors='coerce')
        # Drop rows where 'created' is NaT (not a time)
        Revenue_df = Revenue_df.dropna(subset=['created'])
        # Extract year and month from the 'created' column for grouping
        Revenue_df['year'] = Revenue_df['created'].dt.year
        # Month names (January, February, etc.)
        Revenue_df['month'] = Revenue_df['created'].dt.strftime('%B')  

        total1,total2 = st.columns(2, gap='small')
        with total1:
            # Total Transaction Amount by Month
            monthly_transaction = Revenue_df.groupby(['year', 'month'])['total_invoice_amount'].sum().reset_index()
            # Calculate the percentage change
            monthly_transaction['percent_change'] = monthly_transaction['total_invoice_amount'].pct_change() * 100
            # Create a figure with bar and line charts
            fig = px.bar(
                monthly_transaction,
                x='month',
                y='total_invoice_amount',
                title="Total Transaction Amount by Month",
                labels={'total_invoice_amount': 'Total Transaction Amount ($)'}
            )
            # Add a trend line showing percentage change
            fig.add_scatter(
                x=monthly_transaction['month'],
                y=monthly_transaction['total_invoice_amount'],
                mode='lines+markers',
                name='Trend',
                hovertext=monthly_transaction['percent_change'].apply(lambda x: f'{x:.2f}%' if pd.notnull(x) else ''),
                hoverinfo='text'
            )
            fig.update_layout(
                xaxis_title='Month',
                yaxis_title='Total Transaction Amount ($)',
                xaxis={'categoryorder': 'category ascending'},
                template='plotly_white'
            )
            # Display the plot
            st.plotly_chart(fig)

        with total2:
            # Filter where 'description' contains 'subscription'
            subscription_df = Revenue_df[Revenue_df['description'].str.contains('subscription', case=False, na=False)]
            # Total Subscription Amount by Month
            monthly_subscription = subscription_df.groupby(['year', 'month'])['total_invoice_amount'].sum().reset_index()
            # Calculate the percentage change
            monthly_subscription['percent_change'] = monthly_subscription['total_invoice_amount'].pct_change() * 100
            # Create a figure with bar and line charts
            fig2 = px.bar(
                monthly_subscription,
                x='month',
                y='total_invoice_amount',
                title="Total Subscription Amount by Month",
                labels={'total_invoice_amount': 'Total Subscription Amount ($)'}
            )
            # Add a trend line showing percentage change
            fig2.add_scatter(
                x=monthly_subscription['month'],
                y=monthly_subscription['total_invoice_amount'],
                mode='lines+markers',
                name='Trend',
                hovertext=monthly_subscription['percent_change'].apply(lambda x: f'{x:.2f}%' if pd.notnull(x) else ''),
                hoverinfo='text'
            )
            fig2.update_layout(
                xaxis_title='Month',
                yaxis_title='Total Subscription Amount ($)',
                xaxis={'categoryorder': 'category ascending'},
                template='plotly_white'
            )
            # Display the plot
            st.plotly_chart(fig2)

        total1,total2 = st.columns(2, gap='small')

        with total1:
            # Filter where 'description' does not contain 'subscription'
            product_df = Revenue_df[~Revenue_df['description'].str.contains('subscription', case=False, na=False)]
            # Total Products Amount by Month
            monthly_product = product_df.groupby(['year', 'month'])['total_invoice_amount'].sum().reset_index()
            # Calculate the percentage change
            monthly_product['percent_change'] = monthly_product['total_invoice_amount'].pct_change() * 100
            # Create a figure with bar and line charts
            fig3 = px.bar(
                monthly_product,
                x='month',
                y='total_invoice_amount',
                title="Total Product Amount by Month",
                labels={'total_invoice_amount': 'Total Product Amount ($)'}
            )
            # Add a trend line showing percentage change
            fig3.add_scatter(
                x=monthly_product['month'],
                y=monthly_product['total_invoice_amount'],
                mode='lines+markers',
                name='Trend',
                hovertext=monthly_product['percent_change'].apply(lambda x: f'{x:.2f}%' if pd.notnull(x) else ''),
                hoverinfo='text'
            )
            fig3.update_layout(
                xaxis_title='Month',
                yaxis_title='Total Product Amount ($)',
                xaxis={'categoryorder': 'category ascending'},
                template='plotly_white'
            )
            # Display the plot
            st.plotly_chart(fig3)

        with total2:
            # Total Tax Amount by Month
            monthly_tax = Revenue_df.groupby(['year', 'month'])['tax'].sum().reset_index()
            # Calculate the percentage change
            monthly_tax['percent_change'] = monthly_tax['tax'].pct_change() * 100
            # Create a figure with bar and line charts
            fig4 = px.bar(
                monthly_tax,
                x='month',
                y='tax',
                title="Total Tax Amount by Month",
                labels={'tax': 'Tax Amount ($)'}
            )
            # Add a trend line showing percentage change
            fig4.add_scatter(
                x=monthly_tax['month'],
                y=monthly_tax['tax'],
                mode='lines+markers',
                name='Trend',
                hovertext=monthly_tax['percent_change'].apply(lambda x: f'{x:.2f}%' if pd.notnull(x) else ''),
                hoverinfo='text'
            )
            fig4.update_layout(
                xaxis_title='Month',
                yaxis_title='Tax Amount ($)',
                xaxis={'categoryorder': 'category ascending'},
                template='plotly_white'
            )
            # Display the plot
            st.plotly_chart(fig4)

    def Customers(self,customers_df,subscriptions_df):
        # Use Streamlit's markdown function to add a style tag to hide the Streamlit element toolbar
        st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        # Convert 'trial_end' and 'created' to datetime
        subscriptions_df['trial_end'] = pd.to_datetime(subscriptions_df['trial_end'])
        subscriptions_df['created'] = pd.to_datetime(subscriptions_df['created'])

        # Sidebar filter for date range
        st.sidebar.header("Select Date Range:")
        #start_date = st.sidebar.date_input("Start date", datetime.date.today() - datetime.timedelta(days=30))
        #end_date = st.sidebar.date_input("End date", datetime.date.today())
        start_date = st.sidebar.date_input("Start date", subscriptions_df['created'].min().date())
        end_date = st.sidebar.date_input("End date", subscriptions_df['created'].max().date())
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter the subscription data
        filtered_sub_df = subscriptions_df[(subscriptions_df["trial_end"] >= start_date) & (subscriptions_df["trial_end"] <= end_date)]
        filtered_cust_sub_df = filtered_sub_df.merge(customers_df, left_on="customer_id", right_on="id", how="inner")
        # Filter data
        customers_df['created'] = pd.to_datetime(customers_df['created'], errors='coerce')
        filtered_df = customers_df[(customers_df['created'] >= pd.to_datetime(start_date)) & (customers_df['created'] <= pd.to_datetime(end_date))]


        # Calculate the total number of active, inactive, trialing, past due, paused, and incomplete expired subscriptions
        total_active = filtered_cust_sub_df[filtered_cust_sub_df["status"] == "active"].shape[0] # Calculate the total number of active customers
        total_inactive = filtered_cust_sub_df[filtered_cust_sub_df["status"] != "active"].shape[0] # Calculate the total number of inactive customers
        total_trialing = filtered_cust_sub_df[filtered_cust_sub_df["status"] == "trialing"].shape[0] # Calculate the total number of trialing customers

        total_customers = total_active + total_inactive + total_trialing
        total1 , total2  = st.columns(2)
        with total1:
            # Display churn rate in metrics
            st.info('Total Customers')
            st.metric(label="Total Customers", value=f" {total_customers:,.0f}")
        with total2:
            st.info('Active Customers')
            st.metric(label="Active Customers", value=f" {total_active:,.0f}")
        
        total1,total2 = st.columns(2)
        with total1:
            st.info('Inactive Customers')
            st.metric(label="Inactive Customers", value=f" {total_inactive:,.0f}")
        with total2:
            st.info('Trialing Customers')
            st.metric(label="Trialing Customers", value=f" {total_trialing:,.0f}")

        #Graph 1
        filtered_df['created'] = pd.to_datetime(filtered_df['created']) # Convert 'created' to datetime if it's not already
        current_date = pd.to_datetime("today") # Filter data for the last 6 months
        start_date = current_date - pd.DateOffset(months=6)
        filtered_customers = filtered_df[filtered_df['created'] >= start_date]
        filtered_customers.set_index('created', inplace=True) # Group by month and count new customers
        monthly_new_customers = filtered_customers.resample('M').size().reset_index(name='new_customers_count')
        monthly_new_customers['year_month'] = monthly_new_customers['created'].dt.strftime('%Y-%m') # Correctly align data with the months
        monthly_new_customers = monthly_new_customers.sort_values(by='created', ascending=True) # Sort by 'year_month' in ascending order
        st.subheader('New Customer Sign-Up Trend')
        # Plot the data
        fig = px.bar(
            monthly_new_customers,
            x='year_month',
            y='new_customers_count',
            title="New Customer Sign-Ups by Month",
            width=1200,
            height=400,
            color_discrete_sequence=['#636EFA']
        )

        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='New Customers Count',
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )

        st.plotly_chart(fig)
        
        #Graph 2
        # Filter data for the last 6 months
        df_sign_up = filtered_df[["id", "created"]]
        df_sign_up["created"] = pd.to_datetime(df_sign_up["created"])
        df_sign_up["Month_year"] = df_sign_up["created"].dt.strftime('%Y-%m')
        df_sign_up = df_sign_up[["id", "Month_year"]]
        df_sign_up["Cust_count_month"] = df_sign_up.groupby("Month_year")["id"].transform('count')
        df_sign_up_data = df_sign_up[["Month_year", "Cust_count_month"]]
        df_sign_up_data = df_sign_up_data.drop_duplicates()
        df_sign_up_data = df_sign_up_data.sort_values(by=['Month_year'], ascending=False)
        df_sign_up_data.reset_index(drop=True, inplace=True)
        with st.expander("VIEW DATA"):
            st.dataframe(df_sign_up_data) #, use_container_width=True
                
        #Graph 2
        # Filter data for the last 6 months
        df_sign_up = filtered_df[["id", "created"]]
        df_sign_up["created"] = pd.to_datetime(df_sign_up["created"])
        df_sign_up["Month_year"] = df_sign_up["created"].dt.strftime('%Y-%m')
        df_sign_up = df_sign_up[["id", "Month_year"]]
        df_sign_up["Cust_count_month"] = df_sign_up.groupby("Month_year")["id"].transform('count')
        df_sign_up_data = df_sign_up[["Month_year", "Cust_count_month"]]
        df_sign_up_data = df_sign_up_data.drop_duplicates()
        df_sign_up_data = df_sign_up_data.sort_values(by=['Month_year'], ascending=False)
        df_sign_up_data.reset_index(drop=True, inplace=True)
        with st.expander("VIEW DATA"):
            st.dataframe(df_sign_up_data) #, use_container_width=True
                
    
        geo_data = filtered_df[['shipping_address_city', 'shipping_address_country']].dropna()
        city_counts = geo_data['shipping_address_city'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']

        fig = px.bar(city_counts.head(10), x='City', y='Count', title='Top 10 Cities by Customer Count')
        st.plotly_chart(fig)

        #Graph 3
        # Display an interactive table
        city_counts = filtered_df['shipping_address_city'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        with st.expander("VIEW DATA"):
            st.dataframe(city_counts)

        # Prepare data for the donut chart
        country_counts = filtered_df['shipping_address_country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']

        fig = px.pie(country_counts.head(5), values='Count', names='Country', title='Top 5 Countries by Customer Count', hole=0.4)

        fig.update_traces(textinfo='percent+label')
        fig.update_layout(annotations=[dict(text='Countries', x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(fig)

    def Subscriptions(self,subscriptions_df,customers_df,revenue_df):
        st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        # Convert 'trial_end' and 'created' to datetime
        subscriptions_df['trial_end'] = pd.to_datetime(subscriptions_df['trial_end'])
        subscriptions_df['created'] = pd.to_datetime(subscriptions_df['created'])
        revenue_df['created'] = pd.to_datetime(revenue_df['created'])

        # Sidebar filter for date range
        st.sidebar.header("Select Date Range:")
        start_date = st.sidebar.date_input("Start date", datetime.date.today() - datetime.timedelta(days=30))
        end_date = st.sidebar.date_input("End date", datetime.date.today())
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter the subscription data
        filtered_sub_df = subscriptions_df[(subscriptions_df["trial_end"] >= start_date) & (subscriptions_df["trial_end"] <= end_date)]
        filtered_cust_sub_df = filtered_sub_df.merge(customers_df, left_on="customer_id", right_on="id", how="inner")

        # Calculate the total number of active, inactive, trialing, past due, paused, and incomplete expired subscriptions
        total_active = filtered_sub_df[filtered_sub_df["status"] == "active"].shape[0] # Calculate the total number of active customers
        total_inactive = filtered_sub_df[filtered_sub_df["status"] != "active"].shape[0] # Calculate the total number of inactive customers
        total_trialing = filtered_sub_df[filtered_sub_df["status"] == "trialing"].shape[0] # Calculate the total number of trialing customers
        total_past_due = filtered_sub_df[filtered_sub_df["status"] == "past_due"].shape[0] # Calculate the total number of past due customers
        total_paused = filtered_sub_df[filtered_sub_df["status"] == "paused"].shape[0] # Calculate the total number of paused customers
        total_incomplete_expired = subscriptions_df[subscriptions_df["status"] == "incomplete_expired"].shape[0] # Calculate the total number of incomplete expired subscriptions
        

        # Create columns in Streamlit
        total1, total2, total3 = st.columns(3, gap='small')

        # Display total active and inactive subscriptions in the columns
        with total1:
            st.info('Active Subscriptions')
            st.metric(label="Total Active Subscriptions", value=str(total_active))

        with total2:
            st.info('Inactive Subscriptions')
            st.metric(label="Total Inactive Subscriptions", value=str(total_inactive))
        
        with total3:
            st.info('Trialing Subscriptions')
            st.metric(label="Total trialing Subscriptions", value=str(total_trialing))
        
        # Create columns in Streamlit
        total1, total2, total3 = st.columns(3, gap='small')

        # Display total active and inactive subscriptions in the columns
        with total1:
            st.info('Past Due Subscriptions')
            st.metric(label="Past Due Subscriptions", value=str(total_past_due))

        with total2:
            st.info('Paused Subscriptions')
            st.metric(label="Total Paused Subscriptions", value=str(total_paused))
        
        with total3:
            st.info('Incomplete Expired Subscriptions')
            st.metric(label="Total Incomplete Expired Subscriptions", value=str(total_incomplete_expired))

        # Display upcoming subscription end customers
        st.subheader("Upcoming Subscription End Customers")
        with st.expander("VIEW DATA"):
            filtered_cust_sub_df['trial_start'] = pd.to_datetime(filtered_cust_sub_df['trial_start']).dt.date
            filtered_cust_sub_df['trial_end'] = pd.to_datetime(filtered_cust_sub_df['trial_end']).dt.date
            showData = st.multiselect('Filter: ', filtered_cust_sub_df.columns, default=[
                "name", "phone", "email", "trial_start","trial_end"])
            st.dataframe(filtered_cust_sub_df[showData], use_container_width=True) 


        # Graph 2
        # Monthly Active Subscriptions
        filtered_sub_df["month"] = filtered_sub_df["created"].dt.to_period('M').astype(str)
        monthly_active_subs = filtered_sub_df.groupby("month")["customer_id"].count().reset_index()
        fig_monthly_2 = px.bar(monthly_active_subs, x="month", y="customer_id", title="Monthly Active Subscriptions")
        st.plotly_chart(fig_monthly_2)

        # Graph 3
        # Daily Active Subscriptions
        filtered_sub_df = filtered_sub_df[filtered_sub_df["status"] == "active"] # Filter the dataframe to only include rows where the subscription status is active
        filtered_sub_df["day"] = filtered_sub_df["created"].dt.strftime('%Y-%m-%d') # Create a new column in the dataframe that contains the date of the subscription creation
        daily_active_subs = filtered_sub_df.groupby("day")["customer_id"].count().reset_index() # Group the dataframe by the date of subscription creation and count the number of unique customer IDs for each date
        fig_daily_3 = px.bar(daily_active_subs, x="day", y="customer_id", title="Daily Active Subscriptions") # Create a bar chart using Plotly Express to display the number of active subscriptions for each date
        fig_daily_3.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Active Subscriptions',
            xaxis_tickformat='%Y-%m-%d'
        ) # Update the layout of the bar chart to include titles for the x and y axes and format the x-axis tick labels
        st.plotly_chart(fig_daily_3)

        # Filter the data for the specific customer_id
        filtered_sub_df['trial_start'] = pd.to_datetime(filtered_sub_df['trial_start']).dt.date
        filtered_sub_df['trial_end'] = pd.to_datetime(filtered_sub_df['trial_end']).dt.date
        filtered_sub_df[filtered_sub_df["customer_id"]=="cus_OzTLZG52Io2Izb"][["customer_id","trial_start","trial_end","status"]].sort_values(by=["trial_start"])
        with st.expander("VIEW DATA"):
            st.dataframe(filtered_sub_df[filtered_sub_df["customer_id"]=="cus_OzTLZG52Io2Izb"][["customer_id","trial_start","trial_end","status"]].sort_values(by=["trial_start"]), use_container_width=True)

        # Graph 4   
        # Count the number of times each customer has used the trial
        df_trial_counts = filtered_cust_sub_df["customer_id"].value_counts().reset_index()
        df_trial_counts.columns = ['customer_id', 'trial_count']
        df_multiple_trials = df_trial_counts[df_trial_counts['trial_count'] > 1] # Filter customers who have used the trial multiple times (e.g., more than once)
        st.subheader("Customers Who Used Trial Multiple Times") # Display the title in the Streamlit app
        if not df_multiple_trials.empty: # Check if there are any customers with multiple trials
            st.bar_chart(df_multiple_trials.set_index('customer_id')['trial_count'])
            with st.expander("VIEW DATA"):
                st.dataframe(df_multiple_trials)
        else:
            st.write("No customers have used the trial multiple times.")
        
        # Graph 5
        # Convert start_date to datetime
        subscriptions_df['start'] = pd.to_datetime(subscriptions_df['start'])
        # Extract month and year
        subscriptions_df['month_year'] = subscriptions_df['start'].dt.to_period('M')
        # Group by month_year and status
        trend_data = subscriptions_df.groupby(['month_year', 'status']).size().reset_index(name='count')
        # Convert month_year to string for plotting
        trend_data['month_year'] = trend_data['month_year'].astype(str)
        # Plot the trend line
        fig = px.line(trend_data, x='month_year', y='count', color='status', title='Subscription Staus Trend Line Over Time')
        fig.update_layout(
            xaxis_title='Month-Year',
            yaxis_title='Count',
            template='plotly_white'
        )
        fig.update_traces(mode='lines+markers')
        # Display the plot
        st.plotly_chart(fig)

        # Extract month and year
        revenue_df['month_year'] = revenue_df['created'].dt.to_period('M')
        # Group by month_year and subscription status
        trend_data = revenue_df.groupby(['month_year', 'subscription']).size().reset_index(name='count')
        # Convert month_year to string for plotting
        trend_data['month_year'] = trend_data['month_year'].dt.strftime('%b %Y')
        # Plot the trend line
        fig = px.line(trend_data, x='month_year', y='count', color='subscription', title='Subscription Count over time')
        fig.update_layout(
            xaxis_title='Month-Year',
            yaxis_title='Count',
            template='plotly_white'
        )
        fig.update_traces(mode='lines+markers')
        # Display the plot
        st.plotly_chart(fig)



    def Payment(self,payment_df):
        # Hide the Streamlit toolbar
        st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        
        st.sidebar.header("Select Date Range:")
        payment_df['created_date'] = pd.to_datetime(payment_df['created_date'], errors='coerce')

        start_date = st.sidebar.date_input("Start date", payment_df["created_date"].min().date())
        end_date = st.sidebar.date_input("End date", payment_df["created_date"].max().date())

        # Filter data
        filtered_df  = payment_df[(payment_df['created_date'] >= pd.to_datetime(start_date)) & (payment_df['created_date'] <= pd.to_datetime(end_date))]
        
        # Display data
        with st.expander("VIEW DATA"):
            filtered_df['created_date'] = pd.to_datetime(filtered_df['created_date']).dt.date
            showData = st.multiselect('Filter: ', filtered_df.columns, default=[
                'id', 'amount', 'amount_refunded', 'balance_transaction_id',
                'calculated_statement_descriptor',  'created_date', 'currency', 'customer_id',
                'description', 'status'])
            st.dataframe(filtered_df[showData], use_container_width=True)

        total_transactions = filtered_df.shape[0] # Calculate the total number of transactions
        successful_transactions = filtered_df[filtered_df["status"] == "succeeded"].shape[0] # Calculate the number of successful transactions
        failed_transactions = filtered_df[filtered_df["status"] == "failed"].shape[0] # Calculate the number of failed transactions

        total1, total2, total3 = st.columns(3, gap='small')
        with total1:
            st.info('Total Transactions')
            st.metric(label="Total Transactions", value=f" {total_transactions:,.0f}")

        with total2:
            st.info('Number of successful transactions')
            st.metric(label="Number of successful transactions:", value=f"{successful_transactions:,.0f}")

        with total3:
            st.info('Number of failed transactions')
            st.metric(label="Number of failed transactions:", value=f"{failed_transactions:,.0f}")

        st.markdown("---")
        
        # Graph 1
        # Pie chart
        total1, total2 = st.columns(2, gap='small')
        with total1:
            refunded_line_items = filtered_df[filtered_df["refunded"] == True]["description"].value_counts() # Filter the dataframe to only include rows where the "refunded" column is True
            top_2 = refunded_line_items.head(2)
            other = refunded_line_items[2:].sum() if len(refunded_line_items) > 2 else 0
            top_2_with_other = pd.concat([top_2, pd.Series({'Other': other})])

            fig_1 = px.pie(values=top_2_with_other, names=top_2_with_other.index, title="Top 2 Refunded Line Items and Others",
                        labels={'index': 'Refunded Items', 'values': 'Count'}, hole=0.3)
            st.plotly_chart(fig_1)
        
        # Graph 2
        with total2:
            status_counts = filtered_df['status'].value_counts() # Count the number of times each status appears in the filtered dataframe
            if not status_counts.empty and 'succeeded' in status_counts and 'failed' in status_counts: # Check if the dataframe is not empty and if 'succeeded' and 'failed' statuses exist
                succeeded_count = status_counts['succeeded'] # Get the count of 'succeeded' and 'failed' statuses
                failed_count = status_counts['failed']
                labels = ['Succeeded', 'Failed']  # Prepare the data for the pie chart
                values = [succeeded_count, failed_count]
                fig_2 = px.pie(values=values, names=labels, title="Payment Status Distribution",
                            labels={'index': 'Payment Status', 'values': 'Count'}, hole=0.3)  # Create a Plotly pie chart for payment statuses
                st.plotly_chart(fig_2)
            else:
                st.write("No data available for succeeded or failed payments.") # If the dataframe is empty or 'succeeded' and 'failed' statuses do not exist, display a message

        # Graph 3
        failure_reasons = (filtered_df["failure_code"].value_counts(normalize=True).head() * 100).round(2) # Calculate the percentage of each failure reason in the filtered dataframe
        failure_reasons_df = failure_reasons.reset_index() # Reset the index of the failure_reasons dataframe
        failure_reasons_df.columns = ['Failure Reason', 'Percentage'] # Rename the columns of the failure_reasons dataframe
        fig_3 = px.bar(
            failure_reasons_df, 
            x='Failure Reason', 
            y='Percentage',
            title="Top 5 Failure Reasons",
            labels={'Failure Reason': 'Failure Reason', 'Percentage': 'Percentage (%)'},
            text='Percentage',
            width=800,  # Adjusted width
            height=600
        ) # Create a bar chart using Plotly Express
        fig_3.update_traces(texttemplate='%{text:.2f}%', textposition='outside') # Update the text of the bar chart to display the percentage
        fig_3.update_layout(
            xaxis_title='Failure Reason', 
            yaxis_title='Percentage (%)', 
            xaxis_tickangle=320,
            margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins if needed
        ) # Update the layout of the bar chart
        st.plotly_chart(fig_3) # Plot the bar chart using Streamlit

        # Graph 4
        refunded_amounts = filtered_df[filtered_df["amount_refunded"] > 0]["amount_refunded"].value_counts().head() # Get the value counts of the refunded amounts in the filtered dataframe
        st.subheader("Most Frequent Refunded Amounts") # Create a subheader for the most frequent refunded amounts
        st.bar_chart(refunded_amounts,x_label="Amount Refunded", y_label="Count") # Create a bar chart of the most frequent refunded amounts

    def financial(self,financial_df):
        st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        # Sidebar options
        st.sidebar.header("Select Date Range:")
        financial_df['month'] = pd.to_datetime(financial_df['month'], errors='coerce')

        start_date = st.sidebar.date_input("Start date", financial_df["month"].min().date())
        end_date = st.sidebar.date_input("End date", financial_df["month"].max().date())

        # Filter data
        filtered_df = financial_df[(financial_df['month'] >= pd.to_datetime(start_date)) & (financial_df['month'] <= pd.to_datetime(end_date))]

        # Create an expander to view the data
        with st.expander("VIEW DATA"):
            showData = st.multiselect('Filter: ',  filtered_df.columns, default=[
                'month','currency','total_sales','total_refunds','total_payouts','net_profit_loss'])
            st.dataframe( filtered_df[showData], use_container_width=True)


        total_sales = filtered_df['total_sales'].sum() # Calculate the total sales from the filtered dataframe
        total_refunds = filtered_df['total_refunds'].sum() # Calculate the total refunds from the filtered dataframe
        total_payouts = filtered_df['total_payouts'].sum() # Calculate the total payouts from the filtered dataframe
        net_profit_loss = filtered_df['net_profit_loss'].sum() # Calculate the net profit or loss from the filtered dataframe


        total1, total2 = st.columns(2, gap='small')

        with total1:
            st.info('Total Sales',icon="💸")
            st.metric(label="Total Sales", value=f"$ {total_sales:,.0f}")

        with total2:
            st.info('Total Refunds',icon="💸")
            st.metric(label="Total Refunds:", value=f"$ {total_refunds:,.0f}")

        total3, total4 = st.columns(2, gap='small')

        with total3:
            st.info('Total Payouts',icon="💸")
            st.metric(label="Total Payouts:", value=f"$ {total_payouts:,.0f}")

        with total4:
            st.info('Net Pofit & Loss',icon="📊")
            st.metric(label="Net Pofit & Loss:", value=f"$ {net_profit_loss:,.0f}")

        

        # Plotting the data
        st.title("Financial Overview")
        total1, total2 = st.columns(2, gap='small')

        with total1:
            fig_sales = px.bar(filtered_df, x='month', y='total_sales', title='Total Sales Over Time')
            st.plotly_chart(fig_sales)


        with total2:
            fig_refunds = px.bar(filtered_df, x='month', y='total_refunds', title='Total Refunds Over Time')
            st.plotly_chart(fig_refunds)

        total3, total4 = st.columns(2, gap='medium')

        with total3:
            fig_payouts = px.bar(filtered_df, x='month', y='total_payouts', title='Total Payouts Over Time')
            st.plotly_chart(fig_payouts)

        with total4:
            fig_net_profit_loss = px.bar(filtered_df, x='month', y='net_profit_loss', title='Net Profit/Loss Over Time')
            st.plotly_chart(fig_net_profit_loss)


def main():
    s3_client = boto3.client('s3')
    bucket_name = 'braintaprawdata'
    # Fetch the object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key='KPI_Revenue_total_counts.csv')
    content = response['Body'].read().decode('utf-8')# Read the content
    Revenue_df = pd.read_csv(StringIO(content))

    response2 = s3_client.get_object(Bucket=bucket_name, Key='customers_6months.csv')
    content2 = response2['Body'].read().decode('utf-8')
    customers_df= pd.read_csv(StringIO(content2))

    response1 = s3_client.get_object(Bucket=bucket_name, Key='subscriptions_6months.csv')
    content1 = response1['Body'].read().decode('utf-8')
    subscriptions_df = pd.read_csv(StringIO(content1))

    response = s3_client.get_object(Bucket=bucket_name, Key='payments_outcome_data.csv')
    content = response['Body'].read().decode('utf-8')
    payment_df = pd.read_csv(StringIO(content))

    response = s3_client.get_object(Bucket=bucket_name, Key='financial.csv')
    content = response['Body'].read().decode('utf-8')
    financial_df = pd.read_csv(StringIO(content))

    dashboard = Dashboard(Revenue_df, customers_df, subscriptions_df, payment_df, financial_df)

    with st.sidebar:
        selected = option_menu(
            menu_title="Select a Page",
            options=["Summary","Subscriptions","Customers","Payment","Revenue", "Financial"],
            icons=["","cash", "people", "bar-chart", "credit-card", "file-text"],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Summary":
        st.title(f"{selected}")
        dashboard.Summary(Revenue_df, customers_df, subscriptions_df, payment_df, financial_df)
    elif selected == "Revenue":
        st.title(f"{selected}")
        dashboard.Revenue(Revenue_df)
    elif selected == "Customers":
        st.header(f"{selected}")
        dashboard.Customers(customers_df,subscriptions_df)
    elif selected == "Subscriptions":
        st.header(f"{selected}")
        dashboard.Subscriptions(subscriptions_df,customers_df,Revenue_df)
    elif selected == "Payment":
        st.header(f"{selected}")
        dashboard.Payment(payment_df)
    elif selected == "Financial":
        st.header(f"{selected}")
        dashboard.financial(financial_df)


if __name__ == "__main__":
    main()
