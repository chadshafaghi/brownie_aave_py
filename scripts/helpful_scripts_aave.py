from web3 import Web3
from brownie import interface, network, config
from scripts.helpful_scripts import get_contract


def get_token_price(price_feed_dai_eth):
    price_feed_dai_eth = get_contract("eth_dai_price_feed")
    price_dai_eth = price_feed_dai_eth.latestRoundData()[1]
    return float(Web3.fromWei(price_dai_eth, "ether"))


def get_borrowable_data(lending_pool, account):
    # Get borrowable data for the Account on this lending pool
    # this will provide ability to udnetrand at runtime capacity/limit for the account to borrow
    # without being liquiditate
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrows_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account)

    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_borrows_eth = Web3.fromWei(available_borrows_eth, "ether")
    ltv = ltv / 100
    current_liquidation_threshold = current_liquidation_threshold / 100
    print(f"You have {total_collateral_eth} worth of ETH collateral deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You can borrow {available_borrows_eth} worth of ETH")
    print(f"Loan to value is currently {ltv} %")
    print(f"Liquidation treshold is currently set to {current_liquidation_threshold} %")
    print(f"Health factor is {health_factor/(10**18)}")

    return (float(total_debt_eth), float(available_borrows_eth))


def get_lending_pool():
    # ABI : abi of the contract which will provide us the lending pool address
    # Address of the contract which will provide us the lending pool address

    pool_provider_address = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["pool_provider_adr"]
    )
    return pool_provider_address.getLendingPool()


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token......")
    erc20 = interface.IERC20(erc20_address)
    tx_approve = erc20.approve(spender, amount, {"from": account})
    tx_approve.wait(1)
    print(
        f"{erc20.symbol()} token has been approved for amount: {amount / (10 ** 18)} for the spender {spender}"
    )
    return tx_approve


def repay_all(amount, lending_pool, account):
    approve_erc20(
        amount,
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )

    tx_repay = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    tx_repay.wait(1)
    print(f"Repayment has been completed successfully")
