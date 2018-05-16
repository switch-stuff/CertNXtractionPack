import binascii, sys, random, asn1
from fractions import gcd

def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m

def get_primes(D, N, E = 0x10001):
    '''Computes P, Q given E,D where pow(pow(X, D, N), E, N) == X'''
    assert(pow(pow(0xCAFEBABE, D, N), E, N) == 0xCAFEBABE) # Check privk validity
    # code taken from https://stackoverflow.com/a/28299742
    k = E*D - 1
    if k & 1:
        raise ValueError('Could not compute factors. Is private exponent incorrect?')
    t = 0
    while not k & 1:
        k >>= 1;
        t += 1
    r = k
    while True:
        g = random.randint(0, N)
        y = pow(g, r, N)
        if y == 1 or y == N - 1:
            continue
        for j in range(1, t):
            x = pow(y, 2, N)
            if x == 1 or x == N - 1:
                break
            y = x
        if x == 1:
            break
        elif x == N - 1:
            continue
        x = pow(y, 2, N)
        if x == 1:
            break
    p = gcd(y - 1, N)
    q = N // p
    assert N % p == 0
    if p < q:
        p, q = q, p
    return (p, q)

def get_pubk(clcert):
    clcert_decoder = asn1.Decoder()
    clcert_decoder.start(clcert)
    clcert_decoder.enter() # Seq, 3 elem
    clcert_decoder.enter() # Seq, 8 elem
    clcert_decoder.read() 
    clcert_decoder.read()
    clcert_decoder.read()
    clcert_decoder.read()
    clcert_decoder.read()
    clcert_decoder.read()
    clcert_decoder.enter()
    clcert_decoder.enter()
    t, v = clcert_decoder.read()
    assert(v == '1.2.840.113549.1.1.1') # rsaEncryption(PKCS #1)
    clcert_decoder.leave()
    t, v = clcert_decoder.read()
    rsa_decoder = asn1.Decoder()
    rsa_decoder.start(v[1:])
    rsa_decoder.enter()
    t, N = rsa_decoder.read()
    t, E = rsa_decoder.read()
    return (E, N)


def main():
    '''Script to create switch der from raw private exponent.'''
    # Read files
    try:
        with open('clcert.der', 'rb') as f:
            clcert = f.read()
    except:
        print('Failed to read Client Cert from clcert.der!')
        sys.exit(1)
    try:
        with open('privk.bin', 'rb') as f:
            privk = f.read()
    except:
        print('Failed to read Private Key from privk.bin!')
        sys.exit(1)

    if len(privk) != 0x100:
        print('Error: Private key is not 0x100 bytes...')
        sys.exit(1)

    E, N = get_pubk(clcert)
    D = int(binascii.hexlify(privk), 0x10)
    if pow(pow(0xDEADCAFE, E, N), D, N) != 0xDEADCAFE:
        print('Error: privk does not appear to be inverse of pubk!')
        sys.exit(1)
    print('Found Key: ')
    print(('E: %X' % E))
    print(('D: %0512X' % D))
    print(('N: %0512X' % N))
    P, Q = get_primes(D, N, E)
    print(('P: %0256X' % P))
    print(('Q: %0255X' % Q))
    dP = D % (P - 1)
    dQ = D % (Q - 1)
    print(('dP: %0256X' % dP))
    print(('dQ: %0256X' % dQ))
    Q_inv = modinv(Q, P)
    print(('Q_inv: %0256X' % Q_inv))

    enc = asn1.Encoder()
    enc.start()
    enc.enter(0x10)
    enc.write(0)
    enc.write(N)
    enc.write(E)
    enc.write(D)
    enc.write(P)
    enc.write(Q)
    enc.write(dP)
    enc.write(dQ)
    enc.write(Q_inv)
    enc.leave()
    priv_der = enc.output()
    try:
        with open('privkey.der', 'wb') as f:
            f.write(priv_der)
    except:
        print('Failed to write privkey.der!')
        sys.exit(1)
    print('Successfully wrote to privkey.der!')
 


if __name__=='__main__':
    main()