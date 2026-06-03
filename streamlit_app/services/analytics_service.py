import pandas as pd

def calculate_financial_metrics(df: pd.DataFrame) -> dict:
    """
    Calculates total pemasukan, total pengeluaran, and total saldo.
    """
    if df.empty:
        return {"pemasukan": 0, "pengeluaran": 0, "saldo": 0}

    # Filter completed or active transactions if 'status' column exists, assuming all valid for now
    
    pemasukan = df[df['type'].str.lower() == 'pemasukan']['amount'].sum()
    pengeluaran = df[df['type'].str.lower() == 'pengeluaran']['amount'].sum()
    # Karena nilai pengeluaran di database sudah minus (negatif),
    # maka saldo adalah hasil penjumlahan keduanya, bukan pengurangan.
    saldo = pemasukan + pengeluaran

    return {
        "pemasukan": pemasukan,
        "pengeluaran": pengeluaran,
        "saldo": saldo
    }

def calculate_health_score(df: pd.DataFrame) -> dict:
    """
    Calculates a Health Score (0-100) based on financial metrics.
    """
    metrics = calculate_financial_metrics(df)
    pemasukan = metrics['pemasukan']
    pengeluaran = metrics['pengeluaran']
    saldo = metrics['saldo']
    
    score = 0
    
    # 1. Cashflow Positif (Max 40 pts)
    if saldo > 0:
        score += 40
    elif saldo == 0:
        score += 20
        
    # 2. Rasio Pengeluaran terhadap Pemasukan (Max 40 pts)
    if pemasukan > 0:
        ratio = abs(pengeluaran) / pemasukan
        if ratio < 0.5:
            score += 40 # Sangat sehat (pengeluaran < 50% pemasukan)
        elif ratio < 0.8:
            score += 30 # Sehat
        elif ratio <= 1.0:
            score += 10 # Pas-pasan
    else:
        if pengeluaran == 0:
            score += 20 # Tidak ada aktivitas
            
    # 3. Aktivitas Transaksi (Max 20 pts)
    if not df.empty and len(df) > 5:
        score += 20
    elif not df.empty:
        score += 10
        
    # Tentukan Status
    if score >= 80:
        status = "Sangat Sehat"
        color = "green"
    elif score >= 60:
        status = "Sehat"
        color = "blue"
    elif score >= 40:
        status = "Perlu Perhatian"
        color = "orange"
    else:
        status = "Kritis"
        color = "red"
        
    return {
        "score": score,
        "status": status,
        "color": color
    }
