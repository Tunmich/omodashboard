res = resilient_request("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
if res:
    sol_price = res.json()["solana"]["usd"]
