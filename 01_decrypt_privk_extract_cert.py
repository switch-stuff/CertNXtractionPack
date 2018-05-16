import os, sys
from binascii import unhexlify as uhx, hexlify as hx
from Crypto.Cipher import AES
from Crypto.Util import Counter

def get_ssl_privk(cal0):
    ssl_kek = uhx('B011............................')
    cal0.seek(0x0AE0)
    sec_block = cal0.read(0x800)
    with open('clcert.der', 'wb') as cert:
        cert.write(sec_block)
    
    cal0.seek(0x3AE0)
    ctr = Counter.new(128, initial_value=int(hx(cal0.read(0x10)), 16))
    dec = AES.new(ssl_kek, AES.MODE_CTR, counter=ctr).decrypt(cal0.read(0x120))
    privk = hx(dec[:0x100])
    
    with open('privk.bin', 'wb') as out:
        out.write(uhx(privk))
    return None
    
def main(argc, argv):
    if argc != 2:
        print('Usage: %s PRODINFO.bin' % argv[0])
        return 1
    
    try:
        with open(argv[1], 'rb') as cal0:
            get_ssl_privk(cal0)
            return 0
    except:
        print('Failed to open %s!' % argv[1])
        return 1

if __name__=='__main__':
    sys.exit(main(len(sys.argv), sys.argv))