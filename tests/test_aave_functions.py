import pytest
from scripts.helpful_scripts import get_account
from scripts.helpful_scripts_aave import (
    approve_erc20,
    get_lending_pool,
    get_token_price,
)
from brownie import network, config


def test_get_token_price():
    # Arrange / Act
    asset_price = get_token_price("eth_dai_price_feed")

    # Assert
    assert asset_price > 0


def test_get_lending_pool():
    # Arrange / Act
    lending_pool = get_lending_pool()
    # Assert
    assert lending_pool


def test_approve_erc20():
    # Arrange
    account = get_account()
    lending_pool = get_lending_pool()
    amount = 1000000000000000000  # 1
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # Act
    approved = approve_erc20(amount, lending_pool, erc20_address, account)
    # Assert
    assert approved != None
