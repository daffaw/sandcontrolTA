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
    # Revenue per year

    if Qo>qz:
        revenue = (Qo-qz)* price * 365
    else:
        revenue=Qo*price*365

    
    # Net cash flow
    cashflow = revenue - opex
    
    if cashflow <= 0:
        return float('inf')  # ga balik modal
    
    # Payout period
    payout = capex / cashflow
    
    return payout