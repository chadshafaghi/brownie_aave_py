from web3 import Web3
from brownie import (
    Contract,
    accounts,
    config,
    network,
    MockV3Aggregator,
)

LOCAL_ENV = ["development", "ganache-local", "mainnet-fork"]
DECIMAL = 8
STARTING_PRICE = 341446200000000

contract_to_mock = {"eth_dai_price_feed": MockV3Aggregator}


def is_local_env():
    if network.show_active() in LOCAL_ENV:
        return True
    return False


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if is_local_env():
        return accounts[0]
    return accounts.add(config["networks"][network.show_active()]["wallet_private_key"])


def deploy_mocks(decimals=DECIMAL, starting_price=STARTING_PRICE):

    MockV3Aggregator.deploy(decimals, starting_price, {"from": get_account()})

    print(
        "A new mock instance for V3Aggregator Contract has been created at address:",
        MockV3Aggregator[-1].address,
    )


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if define, otherwisem it will deploy a new version of that contract , and
    return that mock contract

    Args :
        contract_name (string)

    Returns:
        brownie.network.contract.ProjectContract: the most recently deployed
        version of this contract.
    """
    print("****** Getting contract ", contract_name, " ***********")
    contract_type = contract_to_mock[contract_name]

    if is_local_env():
        print(
            "Environment is local .... a mock contract is required for",
            contract_name,
        )
        if len(contract_type) <= 0:
            print("Creating a new mock instance for ", contract_name, " contract...")
            deploy_mocks()
        else:
            print(
                "An existing mock instance for ",
                contract_name,
                " contract has been identified at address:",
                contract_type[-1].address,
            )
        contract = contract_type[-1]
    else:
        print(
            "Environment is not Local .... getting network ",
            contract_name,
            " contract instance",
        )
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract
