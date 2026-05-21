def payout_period(capex, Qo, price, opex,qz):
    """
    Calculate payout period (years)
    
    Parameters:
    capex : float (USD)
    Qo    : float (bopd)
    price : float (USD/bbl)
    opex  : float (USD/year)
    
    Returns:
    float (years)
    """
    deltaq=max(Qo-qz,0)
    # Revenue per year
    revenue = deltaq * price * 365
    
    
    
    # Net cash flow
    cashflow = revenue - opex
    
    if cashflow <= 0:
        return float('inf')  # ga balik modal
    
    # Payout period
    payout = capex / cashflow
    
    return payout