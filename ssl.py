import os
import shutil


class SSL:

    ssl_dir = "/home/em1/ssl"
    ca_cert = ssl_dir + "CA.cert"
    ca_key = ssl_dir + "CA.key"
    ca_days_to_expire = '1825'
    domain_days_to_expire = '365'
    password = 'changeit'
    subject = "/C=US/" \
              "ST=Texas/" \
              "L=Austin/" \
              "O=Control-M/" \
              "OU=Control-M/" \
              "CN=Control-M-CA/" \
              "emailAddress=admin@controlm.com"

    def __init__(self):
        if not os.path.exists(self.ssl_dir):
            os.mkdir(self.ssl_dir)
            os.chmod(self.ssl_dir, 0777)

    def run_create_ca_key(self):
        # Create CA private key with DES in ede cbc mode (168 bit key)
        return "su - em1 -c \"openssl genrsa " \
               "-des3 " \
               "-passout pass:{password} " \
               "-out {ca_key} " \
               "4096\"".format(
                password=SSL.password,
                ca_key=self.ca_key
                )

    def run_create_ca_certificate(self):
        # Create CA certificate
        return "su - em1 -c \"openssl req -x509 " \
               "-new " \
               "-key " \
               "{ca_key} " \
               "-sha256 " \
               "-days {days} " \
               "-passin pass:{password} " \
               "-out {ca_cert} " \
               "-subj \"{subject}\"\"".format(
                ca_key=self.ca_key,
                days=self.ca_days_to_expire,
                password=SSL.password,
                ca_cert=self.ca_cert,
                subject=self.subject
                )


class SSLZone23:

    def __init__(self, hostname):
        self.hostname = hostname
        self.ctmkeytool_em = "/home/em1/ctm_em/bin/ctmkeytool"
        self.zone_23_key = "/home/em1/ctm_em/data/SSL/private_keys/{}.pem".format(self.hostname)
        self.zone_23_csr = "/home/em1/ctm_em/data/SSL/certificate_requests/{}.csr".format(self.hostname)
        self.zone_23_conf = "/home/em1/ctm_em/data/SSL/config/csr_params_zone_2_3.cfg"
        self.ssl_dir = "/home/em1/ssl"
        self.zone_23_cert = self.ssl_dir + self.hostname + ".cert"
        self.filename = self.hostname + "_zone_2_3"
        self.keystore = self.hostname + "_zone_2_3.p12"
        self.combined_cert = self.ssl_dir + self.hostname + "_combined_zone_2_3.cert"

    def run_create_csr_params(self):
        # Copy the csr params config file to ctm
        path = os.path.dirname(os.path.abspath(__file__)) + "/files/"
        shutil.copyfile(path + 'csr_params_zone_23.cfg', self.zone_23_conf)
        # Modify the csr params configuration file
        return "sed -i 's/example.hostname/{hostname}/' {path}".format(hostname=self.hostname,
                                                                       path=self.zone_23_conf)

    def run_create_domain_key_csr(self):
        # Private key file (.pem) and the CSR file (.csr)
        return "su - em1 -c \"{utility} " \
               "-create_csr " \
               "-password {password} " \
               "-conf_file {configuration} " \
               "-out {filename}\"".format(
                utility=self.ctmkeytool_em,
                password=SSL.password,
                configuration=self.zone_23_conf,
                filename=self.filename
                )

    def run_create_domain_certificate(self):
        # Create domain certificate
        return "su - em1 -c \"openssl x509 " \
               "-req " \
               "-in {zone_23_csr} " \
               "-out {zone_23_cert} " \
               "-CA {ca_cert} " \
               "-CAkey {ca_key} " \
               "-CAcreateserial " \
               "-days {days} " \
               "-passin pass:{password} " \
               "-extfile {ext_file} " \
               "-extensions req_ext\"".format(
                zone_23_csr=self.zone_23_csr,
                zone_23_cert=self.zone_23_cert,
                ca_cert=SSL.ca_cert,
                ca_key=SSL.ca_key,
                days=SSL.domain_days_to_expire,
                password=SSL.password,
                ext_file=self.zone_23_conf
                )

    def run_create_combined_certificate(self):
        # Combine CA and domain certificates
        return "su - em1 -c \"cat {zone_23_cert} {ca_cert} > {combined_cert} \"".format(
                zone_23_cert=self.zone_23_cert,
                ca_cert=SSL.ca_cert,
                combined_cert=self.combined_cert
                )

    def run_create_tomcat_keystore(self):
        # Create the p12 keystore file
        return "su - em1 -c \"openssl pkcs12 " \
               "-inkey {zone_23_key} " \
               "-in {combined_cert} " \
               "-passin pass:{password} " \
               "-export " \
               "-passout pass:{password} " \
               "-CAfile {ca_key} " \
               "-out {keystore}\"".format(
                zone_23_key=self.zone_23_key,
                combined_cert=self.combined_cert,
                password=SSL.password,
                ca_key=SSL.ca_key,
                keystore=self.keystore,
                hostname=self.hostname
                )


class SSLZone1:

    def __init__(self, hostname):
        self.hostname = hostname
        self.ctmkeytool_em = "/home/em1/ctm_em/bin/ctmkeytool"
        self.zone_1_conf = "/home/em1/ctm_em/data/SSL/config/csr_params_zone_1.cfg"
        self.zone_1_key = "/home/em1/ctm_em/data/SSL/private_keys/{}.pem".format(self.hostname)
        self.zone_1_csr = "/home/em1/ctm_em/data/SSL/certificate_requests/{}.csr".format(self.hostname)
        self.ssl_dir = "/home/em1/ssl/"
        self.zone_1_cert = self.ssl_dir + self.hostname + ".cert"
        self.combined_cert = self.ssl_dir + "combined.cert"
        self.ca_key = self.ssl_dir + "CA.key"
        self.ca_cert = self.ssl_dir + "CA.cert"
        self.keystore = self.ssl_dir + "tomcat.p12"
        self.keystore_source = "/home/em1/ctm_em/ini/ssl/tomcat.p12"

    def run_create_csr_params(self):
        # Copy the csr params config file to ctm
        path = os.path.dirname(os.path.abspath(__file__)) + "/files/"
        shutil.copyfile(path + 'csr_params_zone_1.cfg', self.zone_1_conf)
        # Modify the csr params configuration file
        return "sed -i 's/example.hostname/{hostname}/' {path}".format(hostname=self.hostname, path=self.zone_1_conf)

    def run_create_domain_key_csr(self):
        # Private key file (.pem) and the CSR file (.csr)
        return "su - em1 -c \"{utility} " \
               "-create_csr " \
               "-password {password} " \
               "-conf_file {configuration} " \
               "-out {hostname}\"".format(
                utility=self.ctmkeytool_em,
                password=SSL.password,
                configuration=self.zone_1_conf,
                hostname=self.hostname
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
                "-days 365 " \
                "-passin pass:{password} " \
                "-extfile {ext_file} " \
                "-extensions req_ext\"".format(
                 zone_1_csr=self.zone_1_csr,
                 zone_1_cert=self.zone_1_cert,
                 ca_cert=self.ca_cert,
                 ca_key=self.ca_key,
                 password=SSL.password,
                 ext_file=self.zone_1_conf
                )

    def run_create_combined_certificate(self):
        # Combine CA and domain certificates
        return "su - em1 -c \"cat {zone_1_cert} {ca_cert} > {combined_cert} \"".format(
            zone_1_cert=self.zone_1_cert,
            ca_cert=self.ca_cert,
            combined_cert=self.combined_cert
        )

    def run_create_tomcat_keystore(self):
        # Create the tomcat.p12 keystore file
        return "su - em1 -c \"openssl pkcs12 " \
                "-inkey {zone_1_key} " \
                "-in {combined_cert} " \
                "-passin pass:{password} " \
                "-export " \
                "-passout pass:{password} " \
                "-CAfile {ca_key} " \
                "-out {keystore} " \
                "-name {hostname}-keystore " \
                "-caname {hostname}-ca\"".format(
                 zone_1_key=self.zone_1_key,
                 combined_cert=self.combined_cert,
                 password=SSL.password,
                 ca_key=self.ca_key,
                 keystore=self.keystore,
                 hostname=self.hostname
                 )

    def run_install_keystore(self):
        from datetime import datetime
        shutil.copyfile(self.keystore_source, self.keystore_source + '.' +
                        datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"))
        shutil.copyfile(self.keystore, self.keystore_source)
        return "echo Keystore installed successfully"


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
"""
