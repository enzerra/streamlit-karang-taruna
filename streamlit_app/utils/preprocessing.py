import pandas as pd

def aggregate_daily_transactions(df):
    """
    Groups transactions by date and calculates daily net flow (Pemasukan - Pengeluaran)
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "amount"])
        
    df = df.copy()
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate amount considering 'type' (e.g. 'Pemasukan' is positive, 'Pengeluaran' is negative)
    df['net_amount'] = df.apply(lambda row: row['amount'] if str(row['type']).lower() == 'pemasukan' else -row['amount'], axis=1)
    
    # Group by date
    daily_df = df.groupby(df['date'].dt.date)['net_amount'].sum().reset_index()
    daily_df.rename(columns={'date': 'ds', 'net_amount': 'y'}, inplace=True)
    
    # Sort by date
    daily_df = daily_df.sort_values('ds')
    
    return daily_df
