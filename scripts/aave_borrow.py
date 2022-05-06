from web3 import Web3
from scripts.get_weth import get_weth
from scripts.helpful_scripts import get_account, is_local_env, get_contract
from scripts.helpful_scripts_aave import (
    get_borrowable_data,
    approve_erc20,
    get_lending_pool,
    repay_all,
    get_token_price,
)
from brownie import network, config, interface


def main():

    # Borrow context
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    amount_deposit = Web3.toWei(0.02, "ether")
    symbol_deposit = interface.IERC20(erc20_address).symbol()

    account = get_account()

    if network.show_active() in ["mainnet-fork", "kovan"]:
        get_weth(amount_deposit)
        print(f"Account has been credited with WETH token")

    # 0 Deposit some collateral in aave
    print(f"Let's first deposit some WETH as a collateral in aave lending pool")

    # ABI and Address to deposit our wETh into aave lending pool

    lending_pool_address = get_lending_pool()
    print("Lending Pool address is : ", lending_pool_address)
    lending_pool = interface.ILendingPool(lending_pool_address)

    # 1 approve sending token
    print(f"Approving WETH deposit transaction....")

    tx_approve = approve_erc20(
        amount_deposit, lending_pool.address, erc20_address, account
    )
    tx_approve.wait(1)
    print(f"WETH deposit transaction has been approved")

    # 2 deposit weth into the landing pool
    tx_deposit = lending_pool.deposit(
        erc20_address, amount_deposit, account.address, 0, {"from": account}
    )
    tx_deposit.wait(1)
    print(
        "Deposit of ",
        amount_deposit / (10 ** 18),
        " ",
        symbol_deposit,
        " to aave pool ",
        lending_pool_address,
        " is completed",
    )

    # Get borrowable data for the Account
    (total_debt_eth, available_borrows_eth) = get_borrowable_data(lending_pool, account)

    # 3 Borrow DAI
    print(f"Now, let's borrow some DAI ....")

    # 3.1 To Borrow DAI we need to first evaluate the market conversion rate between ETH > DAI
    # We will use chainlink V3Aggregator to get this conversion rate.

    # price_feed_dai_eth = get_contract("eth_dai_price_feed")

    converted_price_dai_eth = get_token_price("eth_dai_price_feed")

    print(f"The current DAI/ETH price is {converted_price_dai_eth}")

    # calculating the amount we want to borrow without being liquidated
    amount_dai_to_borrow = (1 / converted_price_dai_eth) * (
        available_borrows_eth * 0.90
    )
    print(f"Amount of DAI to borrow : {amount_dai_to_borrow}")

    tx_borrow = lending_pool.borrow(
        config["networks"][network.show_active()]["dai_token"],
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    tx_borrow.wait(1)
    print(
        f"Address {account.address} has successfully borrowed {amount_dai_to_borrow} DAI from pool {lending_pool.address} "
    )
    (total_debt_eth, available_borrows_eth) = get_borrowable_data(lending_pool, account)

    # 4 We want now to repay what we borrowed.
    print(f"We are no repaying all DAI borrowed, worth of {total_debt_eth} ETH")
    amount_dai_to_repay = (1 / converted_price_dai_eth) * (total_debt_eth) * 0.90
    # We can only repay 90% has we won't have enough DAI to cover the interest :)
    # Ideally this should be change in a way that we can always rebuy dynamically new DAI to cover the interest portion

    repay_all(Web3.toWei(amount_dai_to_repay, "ether"), lending_pool, account)

    (total_debt_eth, available_borrows_eth) = get_borrowable_data(lending_pool, account)
    print(f"Total Debt is now {total_debt_eth} ETH")
    print(
        f"Well done CanaryDigital you have deposit a collateral, borrowed DAI and repayed your debt using Brownie, Aave and Chainlink !"
    )
