from itsdangerous import TimestampSigner

csrf_signer = TimestampSigner("mysecret")
