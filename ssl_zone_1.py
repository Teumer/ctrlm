class SSL:

    def __init__(self, hostname):
        self.hostname = hostname
        self.password = "changeit"
        self.ctmkeytool_em = "/home/em1/ctm_em/bin/ctmkeytool"
        # todo need to update this file
        self.zone_1_conf = "/home/em1/ctm_em/data/SSL/config/csr_params.cfg"
        self.zone_1_key = "/home/em1/ctm_em/data/SSL/private_keys/{}.pem".format(self.hostname)
        self.zone_1_csr = "/home/em1/ctm_em/data/SSL/certificate_requests/{}.csr".format(self.hostname)
        self.zone_1_cert = "/home/em1/{}.cert".format(self.hostname)
        self.chain_cert = "/home/em1/chain.cert"
        self.ca_key = "/home/em1/CA.key"
        self.ca_cert = "/home/em1/CA.cert"
        self.tomcat = "/home/em1/tomcat.p12"
        self.subject = "/C=US/" \
                       "ST=Texas/" \
                       "L=Austin/" \
                       "O=BMC Software Ltd./" \
                       "OU=Workload Automation/" \
                       "CN=Teumer/" \
                       "emailAddress=controlm_security@bmc.com"

    def run_ctmkeytool(self):
        # Private key file (.pem) and the CSR file (.csr)
        return "su - em1 -c \"{utility} " \
               "-create_csr " \
               "-password {password} " \
               "-conf_file {configuration} " \
               "-out {hostname}\"".format(
                utility=self.ctmkeytool_em,
                password=self.password,
                configuration=self.zone_1_conf,
                hostname=self.hostname
                )

    def run_create_ca_key(self):
        # Create CA private key with DES in ede cbc mode (168 bit key)
        return "su - em1 -c \"openssl genrsa " \
                "-des3 " \
                "-passout pass:{password} " \
                "-out {ca_key} " \
                "4096\"".format(
                 password=self.password,
                 ca_key=self.ca_key
                 )

    def run_create_ca_certificate(self):
        # Create CA certificate
        return "su - em1 -c \"openssl req -x509 " \
               "-new " \
               "-key " \
               "{ca_key} " \
               "-sha256 " \
               "-days 1825 " \
               "-passin pass:{password} " \
               "-out {ca_cert} " \
               "-subj {subject}\"".format(
                ca_key=self.ca_key,
                password=self.password,
                ca_cert=self.ca_cert,
                subject=str(self.subject)
                )

    def run_create_domain_certificate(self):
        # Create domain certificate
        return "su - em1 -c \"openssl x509 " \
                "-req " \
                "-in {zone_1_csr} " \
                "-out {zone_1_cert} " \
                "-CA {ca_cert} " \
                "-CAkey {ca_key} " \
                "-CAcreateserial " \
                "-passin pass:{password} " \
                "-extfile {ext_file} " \
                "-extensions req_ext\"".format(
                 zone_1_csr=self.zone_1_csr,
                 zone_1_cert=self.zone_1_cert,
                 ca_cert=self.ca_cert,
                 ca_key=self.ca_key,
                 password=self.password,
                 ext_file=self.zone_1_conf
                )

    def run_combine_domain_ca_certificate(self):
        return "su - em1 -c \"cat {zone_1_cert} {ca_cert} > {chain_cert} \"".format(
            zone_1_cert=self.zone_1_cert,
            ca_cert=self.ca_cert,
            chain_cert=self.chain_cert
        )

    def run_create_tomcat_keystore(self):
        # Create the tomcat.p12 keystore file
        return "su - em1 -c \"openssl pkcs12 " \
                "-inkey {zone_1_key} " \
                "-in {chain_cert} " \
                "-passin pass:{password} " \
                "-export " \
                "-passout pass:{password} " \
                "-CAfile {ca_key} " \
                "-out tomcat.p12 " \
                "-name {hostname}-keystore " \
                "-caname {hostname}-ca\"".format(
                 zone_1_key=self.zone_1_key,
                 chain_cert=self.chain_cert,
                 password=self.password,
                 ca_key=self.ca_key,
                 hostname=self.hostname
                 )


"""
Helpful verification commands for troubleshooting

# Verify key
# openssl rsa -check -in $domain_key -passin pass:$password
# openssl rsa -check -in $CA.key -passin pass:$password

# View domain certificate entries
#openssl x509 -text -noout -in $domain.cert

# Verify certificate was signed by a CA
#openssl verify -verbose -CAfile $CA.key $domain.cert

# Verify a private key matches a certificate and csr
openssl rsa -noout -modulus -in $domain_key -passin pass:$password | openssl md5
#openssl x509 -noout -modulus -in $domain.cert | openssl md5
openssl req -noout -modulus -in $domain_csr | openssl md5

# Zone 1
#cat "$domain".crt CA.pem > combined.pem
"""
