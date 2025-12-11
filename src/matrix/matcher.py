try:
    print("DEBUG df type:", type(df))
    print("DEBUG index type:", type(df.index[0]))
    print("DEBUG col type:", type(df.columns[0]))
    print("DEBUG rounded_w:", rounded_w, type(rounded_w))
    print("DEBUG rounded_h:", rounded_h, type(rounded_h))

    price = df.loc[rounded_h, rounded_w]
except Exception:
    plooi_prices[plooi] = "N/A"
    continue
