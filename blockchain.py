import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

private_key = os.getenv('PRIVATE_KEY')

default_provider = 'https://goerli.infura.io/v3/YOUR-API-KEY'

w3 = Web3(Web3.HTTPProvider(default_provider))

def get_nonce():
    nonce = web3.eth.getTransactionCount(from_account)

def check_gas(tx):
    pass
