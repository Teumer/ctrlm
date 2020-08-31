class SSL:

    def __init__(self, hostname):
        self.hostname = hostname
        self.password = "changeit"
        self.ctmkeytool_em = "/home/em1/ctm_em/bin/ctmkeytool"
        self.conf_file_zone_1 = "/home/em1/ctm_em/data/SSL/config/csr_params.cfg"
        self.subject = "/C=US/\
                        ST=Texas/\
                        L=Austin/\
                        O=BMC Software Ltd./\
                        OU=Workload Automation/\
                        CN={hostname}/\
                        emailAddress=controlm_security@bmc.com".format(hostname=self.hostname)

    def run_ctmkeytool(self):
        # Private key file (.pem) and the CSR file (.csr)
        return("su - em1 -c \"{utility} -create_csr -password {password} -conf_file {configuration} -out {hostname}\"".
               format(utility=self.ctmkeytool_em,
                      password=self.password,
                      configuration=self.conf_file_zone_1,
                      hostname=self.hostname))



"""

# Zone 1
#ext_file="/home/em1/ctm_em/data/SSL/config/csr_params.cfg"

# Zone 1
#domain_csr="/home/em1/ctm_em/data/SSL/certificate_requests/clm-aus-u525tn_20200826_140836.csr"

# Zone 1
#domain_key="/home/em1/ctm_em/data/SSL/private_keys/clm-aus-u525tn_20200826_140836.pem"

# Create the private key and certificate signing request file
#/home/em1/ctm_em/bin/ctmkeytool -create_csr -"password" empass11

# Create CA private key
#openssl genrsa -des3 -passout pass:"$password" -out CA.key 4096

# Verify key
# openssl rsa -check -in "$domain_key" -passin pass:"$password"
# openssl rsa -check -in CA.key -passin pass:"$password"

# Create CA root certificate
# todo - test the subj variable
#openssl req -x509 -new -key CA.key -sha256 -days 1825 -passin pass:"$password" -subj "$subject" -out CA.pem

# Create domain certificate
openssl x509 -req -in "$domain_csr" -out "$domain"-zone23.crt -CA CA.pem -CAkey CA.key -CAcreateserial -passin pass:"$password" -extfile "$ext_file" -extensions req_ext


# View domain certificate entries
#openssl x509 -text -noout -in "$domain".crt

# Verify a private key matches a certificate and csr
openssl rsa -noout -modulus -in "$domain_key" -passin pass:"$password" | openssl md5
#openssl x509 -noout -modulus -in "$domain".crt | openssl md5
openssl x509 -noout -modulus -in "$domain"-zone23.crt | openssl md5
openssl req -noout -modulus -in "$domain_csr" | openssl md5


# 9.0.20 SSL step Zone 1
#openssl pkcs12 -inkey "$domain_key" -in "$domain".crt -passin pass:"$password" -export -passout pass:"$password" -CAfile CA.pem -chain -out tomcat.p12 -name "$domain"-keystore -caname "$domain"-ca


# Zone 1
#cat "$domain".crt CA.pem > combined.pem

# Verify certificate was signed by a CA
#openssl verify -verbose -CAfile CA.pem "$domain".crt
"""