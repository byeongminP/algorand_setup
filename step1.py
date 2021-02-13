import algosdk

private_1, account_1 = algosdk.account.generate_account()
private_2, account_2 = algosdk.account.generate_account()

mnemonic_1 = algosdk.mnemonic.from_private_key(private_1)
mnemonic_2 = algosdk.mnemonic.from_private_key(private_2)

print("Private 1: ", mnemonic_1)
print("Account 1: ", account_1)

print("Private 2: ", mnemonic_2)
print("Account 2: ", account_2)
