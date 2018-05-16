openssl x509 -inform DER -in clcert.der -outform PEM -out clcert.pem
openssl rsa -inform DER -in privkey.der -outform PEM -out privkey.pem
cat clcert.pem privkey.pem > nx_tls_client_cert.pem
openssl pkcs12 -export -in nx_tls_client_cert.pem -out nx_tls_client_cert.pfx -passout pass:switch
md Out
move nx_tls_client_cert.pfx Out/nx_tls_client_cert.pfx
del privk.bin
del clcert.der
del privkey.der
del clcert.pem
del privkey.pem
del nx_tls_client_cert.pem
