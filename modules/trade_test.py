import sys
sys.path.append('./modules')

from modules.solana_executor import execute_sol_trade, wallet
# Test swap: 0.01 SOL ➝ USDC
mint = "Es9vMFrzaCERDAyMtbZ8DYAGQjP7QJjBifRsUJ5ZjFqa"
amount = 0.01

execute_sol_trade(mint, amount, wallet)