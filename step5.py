import json
import time
import base64
import os
from dotenv import load_dotenv
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction
from algosdk import encoding
from algosdk import account

load_dotenv()

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
def group_transactions():

    # recover a account    
    passphrase1 = os.getenv("MNEMONIC1")
    pk_account_a = mnemonic.to_private_key(passphrase1)
    account_a = account.address_from_private_key(pk_account_a)

    # recover b account
    account_b = "4O6BRAPVLX5ID23AZWV33TICD35TI6JWOHXVLPGO4VRJATO6MZZQRKC7RI"

    # connect to node
    acl = connect_to_network()

    # get suggested parameters
    params = acl.suggested_params()
    gen = params["genesisID"]
    gh = params["genesishashb64"]
    last_round = params["lastRound"]
    fee = params["fee"]
    asset_index = 14035004

    # create transaction1
    txn1 = transaction.PaymentTxn(account_a, fee, last_round, last_round+100, gh, account_b, 42000000)

    # create transaction2
    txn2 = transaction.AssetTransferTxn(account_b, fee, last_round, last_round+100, gh, account_a, 1, asset_index)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transaction1
    stxn1 = txn1.sign(pk_account_a)

    # sign transaction2
    with open("buildweb3/step5.lsig", "rb") as f:
      lsig = encoding.future_msgpack_decode(base64.b64encode(f.read()))
    stxn2 = transaction.LogicSigTransaction(txn2, lsig)

    signedGroup = []
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