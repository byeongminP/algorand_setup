import json
import time
import base64
import os
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction
from algosdk import encoding
from algosdk import account

# utility to connect to node
def connect_to_network():
    algod_address = "https://api.testnet.algoexplorer.io"
    algod_token = ""
    algod_client = algod.AlgodClient(algod_token, algod_address, headers = {
      "User-Agent": "DoYouLoveMe?"
    })
    return algod_client

# utility for waiting on a transaction confirmation
def wait_for_confirmation(algod_client, txid ):
    while True:
        txinfo = algod_client.pending_transaction_info(txid)
        if txinfo.get('round') and txinfo.get('round') > 0:
            print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('round')))
            break
        else:
            print("Waiting for confirmation...")
            algod_client.status_after_block(algod_client.status().get('lastRound') +1)

# group transactions           
def group_transactions() :

    # recover a account    
    passphrase1 = os.getenv("MNEMONIC1")
    pk_account_a = mnemonic.to_private_key(passphrase1)
    account_a = account.address_from_private_key(pk_account_a)

    # recover b account
    passphrase2 = os.getenv("MNEMONIC2")
    pk_account_b = mnemonic.to_private_key(passphrase2)
    account_b = account.address_from_private_key(pk_account_b)

    # connect to node
    acl = connect_to_network()

    # get suggested parameters
    params = acl.suggested_params()
    gen = params["genesisID"]
    gh = params["genesishashb64"]
    last_round = params["lastRound"]
    fee = params["fee"]
    asset_index = 14065375

    # create transaction1
    txn1 = transaction.PaymentTxn(account_b, fee, last_round, last_round+100, gh, account_a, 12000000)

    # create transaction2
    txn2 = transaction.AssetTransferTxn(account_a, fee, last_round, last_round+100, gh, account_b, 1, asset_index)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transaction1
    stxn1 = txn1.sign(pk_account_b)

    # sign transaction2
    stxn2 = txn2.sign(pk_account_a)

    signedGroup =  []
    signedGroup.append(stxn1)
    signedGroup.append(stxn2)

    # send them over network
    sent = acl.send_transactions(signedGroup)
    # print txid
    print(sent)

    # wait for confirmation
    wait_for_confirmation(acl, sent) 

# Test Runs     
group_transactions()