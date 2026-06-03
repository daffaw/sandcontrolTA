def payout_period(capex, Qo, price, opex, qz):
    """
    Calculate payout period based on avoided production loss.

    Parameters:
    capex : float (USD)
    Qo    : float (bopd)
    price : float (USD/bbl)
    opex  : float (USD/year)
    qz    : float (bopd)

    Returns:
    float (years)
    """

    # Annual avoided revenue
    revenue = Qo * price * 365

    # Net cash flow
    cashflow = revenue - opex

    if cashflow <= 0:
        return float('inf')  # not economically paid out

    # Payout period
    payout = (capex+opex) / cashflow

    return payout