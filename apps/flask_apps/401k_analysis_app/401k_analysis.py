from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
from io import StringIO
import datetime
from datetime import timedelta

app = Flask(__name__)

# Defining numerical abbreviation function
def abbreviate_number(num):
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif abs(num) >= 1_000:
        return f"{num/1_000:.2f}K"
    return f"{num:.2f}"

# Processing and cleaning data
def process_data(csv_content):
    try:
        df = pd.read_csv(StringIO(csv_content), thousands=',')
        
        # Try to parse dates - handle different date formats
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Drop rows with missing essential data
        required_columns = ['Date', 'Investment', 'Transaction Type', 'Amount ($)']
        existing_columns = [col for col in required_columns if col in df.columns]
        df = df.dropna(subset=existing_columns)
        
        # Converting numerical columns
        if 'Amount ($)' in df.columns:
            df['Amount ($)'] = pd.to_numeric(df['Amount ($)'], errors='coerce')
        if 'Shares/Unit' in df.columns:
            df['Shares/Unit'] = pd.to_numeric(df['Shares/Unit'], errors='coerce')
        
        # Filtering data for the last year (only if Date column exists and has valid dates)
        if 'Date' in df.columns and not df['Date'].isna().all():
            end_date = pd.to_datetime('2025-07-17')
            start_date = end_date - timedelta(days=365)
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        return df
    except Exception as e:
        print(f"Error processing data: {e}")
        return pd.DataFrame()

# Generating summary metrics
def generate_summary(df):
    if df.empty:
        return {"investments": [], "net_change": "0.00"}
    
    try:
        summary = df.groupby(['Investment', 'Transaction Type'])['Amount ($)'].sum().unstack().fillna(0)
        total_net = df['Amount ($)'].sum()
        
        summary_data = []
        for investment in summary.index:
            investment_data = {"investment": investment, "transactions": []}
            for trans_type in summary.columns:
                amount = summary.loc[investment, trans_type]
                if amount != 0:
                    investment_data["transactions"].append({
                        "type": trans_type,
                        "amount": abbreviate_number(amount)
                    })
            total = summary.loc[investment].sum()
            investment_data["total"] = abbreviate_number(total)
            summary_data.append(investment_data)
        
        return {
            "investments": summary_data,
            "net_change": abbreviate_number(total_net)
        }
    except Exception as e:
        print(f"Error generating summary: {e}")
        return {"investments": [], "net_change": "0.00"}

# Creating bar chart for transaction types
def create_bar_chart(df):
    if df.empty:
        return None
    
    try:
        summary = df.groupby(['Investment', 'Transaction Type'])['Amount ($)'].sum().reset_index()
        fig = px.bar(
            summary,
            x='Investment',
            y='Amount ($)',
            color='Transaction Type',
            title='Transaction Amounts by Investment and Type',
            labels={'Amount ($)': 'Amount ($)'},
            text_auto='.2s'
        )
        fig.update_layout(font_size=12, showlegend=True)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creating bar chart: {e}")
        return None

# Creating line chart for cumulative value
def create_line_chart(df):
    if df.empty:
        return None
    
    try:
        df_sorted = df.sort_values('Date')
        df_sorted['Cumulative Value'] = df_sorted['Amount ($)'].cumsum()
        fig = px.line(
            df_sorted,
            x='Date',
            y='Cumulative Value',
            title='Cumulative Account Value Over Time',
            labels={'Cumulative Value': 'Cumulative Value ($)'}
        )
        fig.update_layout(font_size=12)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creating line chart: {e}")
        return None

# Creating pie chart for investment allocation
def create_pie_chart(df):
    if df.empty:
        return None
    
    try:
        total_by_investment = df.groupby('Investment')['Amount ($)'].sum().reset_index()
        total_by_investment = total_by_investment[total_by_investment['Amount ($)'] > 0]
        if total_by_investment.empty:
            return None
        fig = px.pie(
            total_by_investment,
            names='Investment',
            values='Amount ($)',
            title='Investment Allocation',
            labels={'Amount ($)': 'Total Amount ($)'}
        )
        fig.update_traces(textinfo='percent+label', textfont_size=12)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creating pie chart: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            try:
                # Try UTF-8 first
                csv_content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, try with latin-1 encoding
                file.seek(0)  # Reset file pointer
                try:
                    csv_content = file.read().decode('latin-1')
                except UnicodeDecodeError:
                    # If both fail, try with errors='replace'
                    file.seek(0)
                    csv_content = file.read().decode('utf-8', errors='replace')
            
            df = process_data(csv_content)
            
            if df.empty:
                return jsonify({'error': 'No valid data found in the uploaded file'}), 400
            
            summary = generate_summary(df)
            bar_chart = create_bar_chart(df)
            line_chart = create_line_chart(df)
            pie_chart = create_pie_chart(df)
            
            # Convert DataFrame to dict for JSON response
            table_data = df.to_dict('records')
            # Convert dates to strings for JSON serialization
            for record in table_data:
                if 'Date' in record and pd.notna(record['Date']):
                    record['Date'] = record['Date'].strftime('%Y-%m-%d')
            
            return jsonify({
                'success': True,
                'summary': summary,
                'bar_chart': bar_chart,
                'line_chart': line_chart,
                'pie_chart': pie_chart,
                'table_data': table_data
            })
        else:
            return jsonify({'error': 'Please upload a CSV file'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
