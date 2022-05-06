from scripts.helpful_scripts import get_account
from scripts.helpful_scripts_aave import *
from brownie import interface, config, network


def main():
    lending_pool_address = get_lending_pool()
    account = get_account()
    print("Lending Pool address is : ", lending_pool_address)
    lending_pool = interface.ILendingPool(lending_pool_address)
    get_borrowable_data(lending_pool, account)
