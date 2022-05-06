from scripts.helpful_scripts import get_account
from brownie import interface, network, config
from web3 import Web3


def main():
    get_weth()


def get_weth(deposit_eth):
    """
    Mints WETH by depositing ETH
    """
    # ABI :
    # Address :

    account = get_account()
    weth = interface.WethInterface(
        config["networks"][network.show_active()]["weth_token"]
    )
    tx = weth.deposit({"from": account, "value": (deposit_eth * 1.1)})
    tx.wait(1)
    print(
        "Account: ",
        account,
        " has deposit ",
        deposit_eth,
        "ETH and has received ",
        weth.balanceOf(account) / (10 ** 18),
        "wETH",
    )
    return tx
