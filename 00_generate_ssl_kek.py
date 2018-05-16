import sys
from binascii import unhexlify as uhx, hexlify as hx
from Crypto.Cipher import AES

def decrypt(inputkey, iv):
    return AES.new(iv, AES.MODE_ECB).decrypt(inputkey)

def unwrap(wrappedkey, iv):
    return decrypt(wrappedkey, iv)

rsa_private_kek_generation_source = uhx('EF2C........................')
master_key = uhx('C2CA............................')
ssl_aes_key_x = uhx('7F5B............................')
ssl_rsa_key_y = uhx('9A38............................')

def GenerateAesKek(rsa_private_kek_generation_source, key_x_gak, master_key):
    unwrapped_kek = unwrap(rsa_private_kek_generation_source, master_key)
    unwrapped_kekek = unwrap(key_x_gak, unwrapped_kek)
    return unwrap(rpk_key_y, unwrapped_kekek)

rpk_key = GenerateAesKek(rsa_private_kek_generation_source, key_x_gak, master_key)
print("eticket_ssl_rpk = " + hx(rpk_key).upper())