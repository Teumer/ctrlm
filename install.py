#!/usr/bin/env python3
import base64
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from time import sleep

__author__ = "joe_teumer@bmc.com"

"""
Todo
- add MOTD
"""

# Log directory and log filename
file_path = "/tmp/control-m/"
if os.path.exists(file_path):
    shutil.rmtree(file_path, ignore_errors=True)
os.mkdir(file_path)
log_filename = "{}.log".format(os.path.basename(__file__))

# Control-M installation information
# Variables not able to be customized

# Linux user accounts
user_em = 'em1'
user_srv = 's1'
user_list = [user_em, user_srv]

# Password for the above linux accounts
# note Control-M EM & Server silent installation files have hardcoded password 'empass'
password = 'empass'

# Version controlled files directory
path = os.path.dirname(os.path.abspath(__file__)) + "/files/"

# Services
service_directory = "/etc/systemd/system/"
service_ctm_enterprise_manager = service_directory + "ctm_enterprise_manager.service"
service_ctm_server = service_directory + "ctm_server.service"
service_ctm_agent = service_directory + "ctm_agent.service"
service_list = service_ctm_enterprise_manager, service_ctm_server, service_ctm_agent

# Silent installation files
install_enterprise_manager_file = "ctm_enterprise_manager_silent_install.xml"
install_server_file = "ctm_server_silent_install.xml"

# Managed File Transfer
install_mft_silent_file = "ctm_mft_silent_install.xml"
install_mft_file = "DRAFP.9.0.20.000_Linux-x86_64.z"

# Advanced File Transfer
install_aft_agent_silent_file = "ctm_aft_agent_silent_install.xml"
install_aft_enterprise_manager_silent_file = "ctm_aft_enterprise_manager_silent_install.xml"
install_aft_agent_file = "DRAFT.8.2.00_Linux-x86_64.z"
install_aft_agent_fix_pack_file = "PAAFT.8.2.00.300_Linux-x86_64_INSTALL.BIN"
install_aft_enterprise_manager_file = "EM_Side_Installation.zip"

# Forecast
install_forecast_silent_file = "ctm_forecast_silent_install.xml"
install_forecast_file = "DRFOR_Linux-x86_64.tar.Z*"

# Batch Impact Manager
install_bim_silent_file = "ctm_bim_silent_install.xml"
install_bim_file = "DRCBM_Linux-x86_64.tar.Z"

# Self Service
install_self_service_silent_file = "ctm_sls_silent_install.xml"
install_self_service_file = "DRCAG_Linux-x86_64.tar.Z*"

# Workload Change Manager
install_workload_change_manager_silent_file = "ctm_wcm_silent_install.xml"
install_workload_change_manager_file = "DRWCM_Linux-x86_64.tar.Z"

# Web Services Java, and Messaging
install_wjm_em_silent_file = "ctm_wjm_em_silent_install.xml"
install_wjm_agent_silent_file = "ctm_wjm_agent_silent_install.xml"
install_wjm_file = "DRCOB.9.0.00_Linux-x86_64.z"
install_wjm_patch_file = "PACOB.9.0.00.006_linux.tar.Z"

# Control-M/Enterprise Manager and Control-M/Server version
version_dict = {
    1: {"version": "9.0.20.000", "filename": "DROST.9.0.20.000_Linux-x86_64.z"},
    2: {"version": "9.0.19.200", "filename": "DROST.9.0.19.200_Linux-x86_64.tar.Z"},
    3: {"version": "9.0.19.100", "filename": "DROST.9.0.19.100_Linux-x86_64.tar.Z"},
    4: {"version": "9.0.19.000", "filename": "DROST.9.0.19.000_Linux-x86_64.z"}
}


class InstallationMenu:

    def __init__(self):
        self.version = self.run()
        logging.info("Installation version: {}".format(self.version))

    def run(self):
        while True:
            value = 0
            try:
                # Draw Menu
                os.system('clear')
                sys.stdout.write(self.menu())
                sys.stdout.flush()
                # Get user input
                value = int(input(""))
                if value == 0:
                    sys.exit(0)
                # Check if user input is valid
                elif value not in version_dict.keys():
                    continue
            except ValueError:
                continue
            except KeyboardInterrupt:
                # User ctrl c'd
                sys.exit(1)
            else:
                break
        return value

    @staticmethod
    def menu():
        versions = ""
        for key in version_dict:
            versions += "{key} - {version}\n".format(key=key, version=version_dict[key]['version'])
        string = "\nCONTROL-M Installation Menu\n" \
                 "{line}\n" \
                 "\nSelect one of the following versions:\n" \
                 "\n" \
                 "{versions}" \
                 "\n" \
                 "0 - Quit\n" \
                 "\n" \
                 " Enter option number --->   []:".format(line="-" * 29,
                                                          versions=versions)
        return string


class CustomFormatter(logging.Formatter):
    """ Add color support to logger"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    format_detail = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format_detail + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Command:
    """ run shell command and handle logging and return code """

    def __init__(self, command, realtime=False, critical=False):
        self.command = command
        self.realtime = realtime
        self.critical = critical

        if self.realtime:
            self.data = self.run_command_realtime(self.command)
        else:
            self.data = self.run_command(self.command)

        self.stdout = self.data[0]
        self.exit_code = self.data[1]
        self.logger()

    def __str__(self):
        return self.stdout

    def logger(self):
        if self.exit_code != 0:
            logging.warning(" \\___{} exit code {}".format(self.__str__(), self.exit_code))
            if self.critical:
                sys.exit(self.exit_code)

    def run_command_realtime(self, cmd):
        logging.info(self.command)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        while True:
            realtime_output = p.stdout.readline()
            if realtime_output == '' and p.poll() is not None:
                break
            sys.stdout.write(realtime_output)
        return p.communicate()[0].strip().rstrip(), p.returncode

    def run_command(self, cmd):
        logging.info(self.command)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.communicate()[0].strip().rstrip().decode('utf-8'), p.returncode


def set_cshrc_profile():
    # Who the hell thought remapping backspace was a good idea in the Control-M install?
    # Fix the current logged in user env
    Command("stty erase '^?'")
    # Comment out line: stty erase '^H' intr '^C' >& /dev/null
    for user in user_list:
        profile_file = "/home/{}/.cshrc".format(user)
        if os.path.isfile(profile_file):
            Command("sed -i 's/^stty erase/# stty erase/' {}".format(profile_file))


def set_shell_alias():
    # Define ls alias for root in .bashrc
    root_file = "/root/.bashrc"
    if os.path.isfile(root_file):
        with open(root_file, 'r+') as f:
            if not re.search(r"alias ls", f.read()):
                logging.info("Writing {}".format(root_file))
                f.write("alias ls=\"ls -lhF --color\"")

    # Define ls alias for users in .cshrc
    for user in user_list:
        user_file = "/home/{}/.cshrc".format(user)
        if os.path.isfile(user_file):
            with open(user_file, 'r+') as f:
                if not re.search(r"alias ls", f.read()):
                    logging.info("Writing {}".format(user_file))
                    f.write("alias ls ls -lhF --color")


def set_add_user():
    # Add user and specify shell
    for user in user_list:
        cmd = "adduser {} -s /bin/csh".format(user)
        Command(cmd)


def set_user_password():
    # Set user password
    for user in user_list:
        cmd = "echo {}:{} | chpasswd".format(user, password)
        Command(cmd)


def set_user_group_wheel():
    # Add user to wheel group
    for user in user_list:
        cmd = "usermod -aG wheel {}".format(user)
        Command(cmd)


def set_auto_script_cleanup():
    # Remove already existing services if any
    for service in service_list:
        if os.path.exists(service):
            logging.info("Removing {}".format(service))
            os.remove(service)


def set_auto_script_write():
    for service in service_list:
        logging.info("Writing {}".format(service))
        with open("{}{}".format(path, service.split('/')[-1], 'r')) as f:
            data = f.read()
        with open(service, 'w') as f:
            for line in data:
                f.write(line)


def set_auto_script_permissions():
    for service in service_list:
        cmd = "chmod 644 {}".format(service)
        Command(cmd)


def set_auto_script_reload():
    cmd = "systemctl daemon-reload"
    Command(cmd)


def set_auto_script_enable():
    for service in service_list:
        cmd = "systemctl enable {}".format(service)
        Command(cmd)


def install_copy():
    # Copy ctm installation files to working directory
    Command("rsync -avP {}* {}".format(path, file_path))


def set_enterprise_manager_service():
    # Update service file with hostname
    em_service_file = "ctm_enterprise_manager.service"
    Command("sed -i 's/changeme/{hostname}/' {path}{file}".format(path=file_path,
                                                                  hostname=hostname,
                                                                  file=em_service_file))


def set_enterprise_manager_install():
    # Update installation file with version
    Command("sed -i 's/changeme/{version}/' {path}{file}".format(path=file_path,
                                                                 version=version_dict[version]['version'],
                                                                 file=install_enterprise_manager_file))


def set_password_install():
    # Update installation file with password
    # Password 'empass'
    # 9.0.20.000 has a different password encryption
    if version == 1:
        install_password = "!!!iQCq44Zczw9356oE6g3Y5Q=="
    else:
        install_password = "!!!eUYsg3ad1gI="
    Command("sed -i 's/changepassword/{password}/' {path}{file}".format(path=file_path,
                                                                        password=install_password,
                                                                        file=install_enterprise_manager_file))
    Command("sed -i 's/changepassword/{password}/' {path}{file}".format(path=file_path,
                                                                        password=install_password,
                                                                        file=install_server_file))


def set_server_install():
    # Update installation file with version
    Command("sed -i 's/changeme/{version}/' {path}{file}".format(path=file_path,
                                                                 version=version_dict[version]['version'],
                                                                 file=install_server_file))


def repo_mount():
    # Unmount /mnt if mounted
    Command("if grep -qs '/mnt ' /proc/mounts; then umount /mnt; fi")
    # Mount remote repository
    Command("mount {}:{} /mnt/".format(base64.b64decode('Y2xtLWF1cy10dmwzcnQ=').decode('utf-8'), '/nfs/repo'))


def repo_copy():
    # Copy remote pack to local
    Command("rsync -avP /mnt/{}/* {}".format(version_dict[version]['version'], file_path))


def repo_extract():
    # Make extract directory
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)
    # Untar package to extract directory
    Command("tar xzf {}{} -C {}".format(file_path, version_dict[version]['filename'], version_dir))


def install_ctm_enterprise_manager():
    # Install Control-M/Enterprise Manager
    Command("su - em1 -c \"{}/setup.sh -silent {}{}\"".format(
        version_dir,
        file_path,
        install_enterprise_manager_file
    ), realtime=True, critical=False)


def install_ctm_server():
    # Install Control-M/Server
    Command("su - s1 -c \"{}/setup.sh -silent {}{}\"".format(
        version_dir,
        file_path,
        install_server_file
    ), realtime=True, critical=False)


def install_ctm_3719():
    # KA 000365525 Fix download defect
    # Insert 'allow-downloads' after sandbox before allow-scripts if missing
    Command("sed -i 's/sandbox allow-scripts/sandbox allow-downloads allow-scripts/' "
            "/home/em1/ctm_em/etc/emweb/tomcat/conf/web.xml")


def install_epel_repository():
    # Install the epel repository for RHEL 7
    Command("rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm")


def install_htop():
    # Install htop
    Command("yum install htop -y")


def api_install_application_pack():
    # Install Control-M/Agent Application Pack
    # Control-M/Agent must be started
    start_agent_process()
    Command("su - em1 -c \"ctm provision upgrade::install {server} {agent} AppPack {version}\"".format(
        server="Server1",
        agent=hostname,
        version=version_dict[version]['version']
    ))


def install_managed_file_transfer():
    if version != 1:
        return
    # Install MFT - Managed File Transfer
    f_path = file_path + 'mft/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_mft_file, f_path))
    Command("su - em1 -c \"{}setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_mft_silent_file
    ), realtime=True)


def install_advanced_file_transfer():
    if version == 1:
        return
    # Stop Control-M/Agent process before install
    stop_agent_process()
    install_advanced_file_transfer_agent()
    install_advanced_file_transfer_agent_fix_pack()
    install_advanced_file_transfer_enterprise_manager()


def install_advanced_file_transfer_agent():
    # Install AFT - Advanced File Transfer for Control-M/Agent
    f_path = file_path + 'aft/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_aft_agent_file, f_path))
    Command("su - s1 -c \"{}setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_aft_agent_silent_file
    ), realtime=True)


def install_advanced_file_transfer_agent_fix_pack():
    # Install AFT - Advanced File Transfer Fix Pack 3
    Command("su - s1 -c \"{}{} -s\"".format(
        file_path,
        install_aft_agent_fix_pack_file
    ), realtime=True)
    # Force update
    # Command("su - s1 -c \"ctmgetcm -HOST {} -APPLTYPE FILE_TRANS -ACTION get\"".format(hostname))


def install_advanced_file_transfer_enterprise_manager():
    # Install AFT - Advanced File Transfer for Control-M/Enterprise Manager
    f_path = file_path + 'aft/'
    Command("su - em1 -c \"{}EM/setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_aft_enterprise_manager_silent_file
    ), realtime=True)


def install_forecast():
    # Install forecast
    f_path = file_path + 'forecast/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_forecast_file, f_path))
    Command("su - em1 -c \"{}setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_forecast_silent_file
    ), realtime=True)


def install_bim():
    # Install bim
    f_path = file_path + 'bim/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_bim_file, f_path))
    Command("su - em1 -c \"{}setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_bim_silent_file
    ), realtime=True)


def install_workload_change_manager():
    # Install workload change manager
    f_path = file_path + 'workload_change_manager/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_workload_change_manager_file, f_path))
    Command("su - em1 -c \"{}setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_workload_change_manager_silent_file
    ), realtime=True)


def install_self_service():
    # Install self service
    f_path = file_path + 'self_service/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_self_service_file, f_path))
    Command("su - em1 -c \"{}setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_self_service_silent_file
    ), realtime=True)


def install_wjm_enterprise_manager():
    # Install WJM for Control-M/Enterprise Manager
    f_path = file_path + 'wjm/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_wjm_file, f_path))
    Command("su - em1 -c \"{}EM/setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_wjm_em_silent_file
    ), realtime=True)


def install_wjm_agent():
    # Install WJM for Control-M/Agent
    f_path = file_path + 'wjm/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    # Command("tar xzf {}{} -C {}".format(file_path, install_wjm_file, f_path))
    Command("su - s1 -c \"{}Setup_files/components/cm/cmbpi/setup.sh -silent {}{}\"".format(
        f_path,
        file_path,
        install_wjm_agent_silent_file
    ), realtime=True)


def install_wjm_agent_patch():
    # Install WJM Patch PACOB.9.0.00.006
    f_path = file_path + 'wjm_patch/'
    if not os.path.exists(f_path):
        os.makedirs(f_path)
    Command("tar xzf {}{} -C {}".format(file_path, install_wjm_patch_file, f_path))
    # realtime=False as the patch has a clear command to clear the terminal
    Command("su - s1 -c \"echo y | {}PACOB.9.0.00.006/install_patch.sh\"".format(
        f_path
    ), realtime=False)


def start_agent_process():
    # Start the Control-M/Agent process
    Command("su - s1 -c \"start-ag -u s1 -p ALL -s\"")


def stop_agent_process():
    # Stop the Control-M/Agent process
    Command("su - s1 -c \"shut-ag -u s1 -p ALL -s\"")


def api_get_port():
    """
    Get the port used for API calls
    $ manage_webserver -action get_ports
    HTTP_PORT=[18080],HTTPS_PORT=[8446],SHUTDOWN_PORT=[8006],AJP_PORT=[NA]
    """
    port_data = Command("su - em1 -c \"manage_webserver -action get_ports\"")
    port = re.search(r"HTTPS_PORT=\[(?P<port>\d+)]", str(port_data.stdout))
    if port:
        return port.group('port')
    else:
        return "8446"


def api_add_environment():
    # Add API environment
    environment_name = 'devEnvironment'
    # Check if environment name already exists
    if not re.search(r"{}".format(environment_name), Command("su - em1 -c \"ctm environment show\"").stdout):
        Command("su - em1 -c \"ctm environment add {env} "
                "\"https://{hostname}:{port}/automation-api\" "
                "\"{user}\" "
                "\"{password}\"\"".format(env=environment_name,
                                          hostname=hostname,
                                          port=api_get_port(),
                                          user="emuser",
                                          password=password))


def api_login():
    # Login to the API dev environment via an API call
    Command("su - em1 -c \"ctm session login\"")


def api_server_already_added():
    """
    Check if Control-M/Server already added to Control-M/Enterprise Manager
    Return True if server present
    Return False if not present
    """
    try:
        data = json.loads(Command("su - em1 -c \"ctm config servers::get\"").stdout)
        if not any(key.get('name', None) == 'Server1' for key in data):
            return False
        else:
            return True
    except ValueError:
        return False


def api_add_server():
    """
    Adds Control-M/Server to Control-M/Enterprise Manager
    host - Control-M/Server host name
    ctm  - Control-M/Server name
    id   - Defines a unique 3-character code to identify the Control-M/Server
    """
    if api_server_already_added():
        return
    # Sleep after running command to allow for changes to take effect or following commands will fail
    Command("su - em1 -c \"ctm config server::add {host} {ctm} {id}\" && sleep 30".format(host=hostname,
                                                                                          ctm="Server1",
                                                                                          id="001"))


def install_ssl_zones():
    from ssl import SSL, SSLZone1, SSLZone23
    ssl = SSL()
    Command(ssl.run_create_ca_key())
    Command(ssl.run_create_ca_certificate())

    ssl_zone_1 = SSLZone1(hostname)
    Command(ssl_zone_1.run_create_csr_params())
    Command(ssl_zone_1.run_create_domain_key_csr())
    Command(ssl_zone_1.run_create_domain_certificate())
    Command(ssl_zone_1.run_create_combined_certificate())
    Command(ssl_zone_1.run_create_tomcat_keystore())
    ssl_zone_1.run_install_keystore()

    # Tomcat Configuration Manager > SSL Mode > Enable SSL (requires web server recycle)
    Command("su - em1 -c \"manage_webserver -action set_tomcat_conf -sslMode TRUE\"")

    # Manuals steps > Follow Control-M SSL Guide to configure SSL system parameters and recycle components
    ssl_zone_23 = SSLZone23(hostname)
    ssl.run_open_file_permissions()
    Command(ssl_zone_23.run_create_csr_params())
    Command(ssl_zone_23.run_create_domain_key_csr())
    Command(ssl_zone_23.run_create_domain_certificate())
    Command(ssl_zone_23.run_create_combined_certificate())
    Command(ssl_zone_23.run_create_tomcat_keystore())
    ssl.run_open_file_permissions()
    Command(ssl_zone_23.run_install_enterprise_manager())
    Command(ssl_zone_23.run_install_server())
    Command(ssl_zone_23.run_install_agent())


if __name__ == '__main__':

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CustomFormatter())

    # Create file handler
    file_handler = logging.FileHandler(file_path + log_filename)
    file_handler_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
    file_handler.setFormatter(file_handler_format)

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-ssl", "--setup-ssl", action='store_true',
                        help="setup SSL Zones 1 2 3")
    parser.add_argument("-s", "--skip-install", action='store_true',
                        help="dev testing only - skip Control-M installation")
    args = parser.parse_args()

    # Add handles to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Initialize installation menu
    menu = InstallationMenu()
    version = menu.version
    # Example /tmp/9.0.19.200
    version_dir = file_path + version_dict[version]['version']

    # Get hostname
    hostname = Command('hostname').stdout

    # SSL
    if args.setup_ssl:
        install_ssl_zones()
        exit(0)

    # Download package to mount
    repo_mount()
    repo_copy()
    repo_extract()

    # Exit here if skip install - download only
    if args.skip_install:
        exit(0)

    #####################
    # CTM installation  #
    #####################

    # Housekeeping
    set_add_user()
    set_user_password()
    set_user_group_wheel()
    install_copy()
    set_enterprise_manager_service()
    set_enterprise_manager_install()
    set_server_install()
    set_password_install()
    set_auto_script_cleanup()
    set_auto_script_write()
    set_auto_script_permissions()
    set_auto_script_reload()
    set_auto_script_enable()

    # Core
    install_ctm_enterprise_manager()
    install_ctm_server()

    # Core - CAR FIX
    install_ctm_3719()

    # Add-Ons
    install_forecast()
    install_bim()
    install_self_service()
    install_workload_change_manager()
    install_wjm_enterprise_manager()
    install_wjm_agent()
    install_wjm_agent_patch()
    install_advanced_file_transfer()
    install_managed_file_transfer()

    # EPEL repository
    install_epel_repository()
    install_htop()

    # API
    api_add_environment()
    api_login()
    api_add_server()
    api_install_application_pack()

    # CSH Profile Fix
    set_cshrc_profile()
    set_shell_alias()

    logging.info("Control-M v{} installed successfully".format(version_dict[version]['version']))
