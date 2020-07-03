from itsdangerous import TimestampSigner

signer = TimestampSigner("mysecret")


def csrf():
    pass
