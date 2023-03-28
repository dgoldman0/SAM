import os
from dotenv import load_dotenv
from web3 import Web3
import ledgereth

# Will need to add ledger support.

load_dotenv()

private_key = os.getenv('PRIVATE_KEY')
api_key = os.getenv('INFURA_API_KEY')

default_provider = 'https://goerli.infura.io/v3/' + api_key

w3 = Web3(Web3.HTTPProvider(default_provider))

def get_nonce():
    nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount)
    return nonce

def check_gas(tx):
    global web3
    gas = web3.eth.estimateGas(tx)
    return "Estimated gas fee for tx: " + gas

def send_transaction(tx):
    signed_tx = w3.eth.account.signTransaction(tx, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return "Transaction hash: " + tx_hash.hex()

def get_balance(address):
    balance = w3.eth.getBalance(address)
    return "Balance for address " + address + ": " + balance

def get_transaction(tx_hash):
    tx = w3.eth.getTransaction(tx_hash)
    return tx

def get_transaction_receipt(tx_hash):
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return "Transaction receipt for tx " + tx_hash + ": " + tx_receipt

def get_contract(address):
    contract = w3.eth.contract(address=address)
    return contract

def get_contract_abi(address):
    contract = w3.eth.contract(address=address)
    abi = contract.abi
    return "ABI for contract at address " + address + ": " + abi

def get_contract_bytecode(address):
    contract = w3.eth.contract(address=address)
    bytecode = contract.bytecode
    return bytecode

def get_contract_events(address):
    contract = w3.eth.contract(address=address)
    events = contract.events
    return events

def get_contract_functions(address):
    contract = w3.eth.contract(address=address)
    functions = contract.functions
    return functions

def get_contract_call(address, function, *args):
    contract = w3.eth.contract(address=address)
    call = contract.functions.function(*args).call()
    return call
