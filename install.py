#!/usr/bin/python
import json
import logging
import os
import re
import subprocess
import sys

__author__ = "joe_teumer@bmc.com"

# NFS share with Control-M installation files
repo_host = "clm-aus-tvl3rt"
repo_host_dir = "/nfs/repo"

# Log directory and log filename
file_path = "/tmp/"
log_filename = "{}.log".format(os.path.basename(__file__))

# Control-M installation information
# Variables not able to be customized
user_em = 'em1'
user_srv = 's1'
# Password for the above linux accounts
# note Control-M EM & Server silent installation files have hardcoded password 'empass'
password = 'empass'
user_list = [user_em, user_srv]
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
# Forecast
install_forecast_silent_file = "ctm_forecast_silent_install.xml"
install_forecast_file = "DRFOR_Linux-x86_64.tar.Z*"
# Batch Impact Manager
install_bim_silent_file = "ctm_bim_silent_install.xml"
install_bim_file = "DRCBM_Linux-x86_64.tar.Z"

# Control-M/Enterprise Manager and Control-M/Server version
version_dict = {
    1: {"version": "9.0.19.200", "filename": "DROST.9.0.19.200_Linux-x86_64.tar.Z"},
    2: {"version": "9.0.19.100", "filename": "DROST.9.0.19.100_Linux-x86_64.tar.Z"},
    3: {"version": "9.0.19.000", "filename": "DROST.9.0.19.000_Linux-x86_64.z"}
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
                value = int(raw_input(""))
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
            logging.warning(" \\___{} exit code {}".format(self, self.exit_code))
            if self.critical:
                sys.exit(self.exit_code)

    def run_command_realtime(self, cmd):
        logging.info(self.command)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
            sys.stdout.flush()
        return p.communicate()[0].strip().rstrip(), p.returncode

    def run_command(self, cmd):
        logging.info(self.command)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.communicate()[0].strip().rstrip(), p.returncode


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


def set_enterprise_manager_service():
    em_service_file = "ctm_enterprise_manager.service"
    Command("cd {path} && sed -i 's/changeme/{hostname}/g' {a_file}".format(path=path,
                                                                            hostname=Command('hostname'),
                                                                            a_file=em_service_file))


def set_enterprise_manager_install():
    Command("cd {} && sed -i 's/changeme/{}/g' {}".format(path,
                                                          version_dict[version]['version'],
                                                          install_enterprise_manager_file))


def set_server_install():
    Command("cd {} && sed -i 's/changeme/{}/g' {}".format(path,
                                                          version_dict[version]['version'],
                                                          install_server_file))


def repo_mount():
    # Unmount /mnt if mounted
    Command("if grep -qs '/mnt ' /proc/mounts; then umount /mnt; fi")
    # Mount remote repository
    Command("mount {}:{} /mnt/".format(repo_host, repo_host_dir))


def repo_copy():
    # Copy remote pack to local
    Command("rsync -avP /mnt/{}/* {}".format(version_dict[version]['version'], file_path))


def install_copy():
    # Copy ctm installation files to working directory
    Command("rsync -avP {}/*.xml {}".format(path, file_path))


def repo_extract():
    # Make extract directory
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)
    # Untar package to extract directory
    Command("tar xzf {}{} -C {}".format(file_path, version_dict[version]['filename'], version_dir))


def install_ctm_enterprise_manager():
    # Install Control-M/Enterprise Manager
    Command("cd /home/em1 && sudo -u em1 {}/setup.sh -silent {}{}".format(
        version_dir,
        file_path,
        install_enterprise_manager_file
    ), realtime=True, critical=True)


def install_ctm_server():
    # Install Control-M/Server
    Command("cd /home/s1 && sudo -u s1 {}/setup.sh -silent {}{}".format(
        version_dir,
        file_path,
        install_server_file
    ), realtime=True, critical=True)


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


def start_agent_process():
    # Start the Control-M/Agent process
    Command("su - s1 -c \"start-ag -u s1 -p ALL -s\"")


def api_get_port():
    """
    Get the port used for API calls
    $ manage_webserver -action get_ports
    HTTP_PORT=[18080],HTTPS_PORT=[8446],SHUTDOWN_PORT=[8006],AJP_PORT=[NA]
    """
    port_data = Command("su - em1 -c \"manage_webserver -action get_ports\"")
    port = re.search(r"HTTPS_PORT=\[(?P<port>\d+)\]", str(port_data.stdout))
    if port:
        return port.group('port')
    else:
        return "8446"


def api_add_environment():
    """
    Add dev environment
    """
    Command("su - em1 -c \"ctm environment add devEnvironment "
            "\"https://{hostname}:{port}/automation-api\" \"{user}\" \"{password}\"\"".format(
                                                                                        hostname=Command("hostname"),
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
    Command("su - em1 -c \"ctm config server::add {host} {ctm} {id}\"".format(host=Command("hostname"),
                                                                              ctm="Server1",
                                                                              id="001"))


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

    # Add handles to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Initialize installation menu
    menu = InstallationMenu()
    version = menu.version
    # Example /tmp/9.0.19.200
    version_dir = file_path + version_dict[version]['version']

    # Housekeeping
    set_add_user()
    set_user_password()
    set_user_group_wheel()
    set_enterprise_manager_service()
    set_enterprise_manager_install()
    set_server_install()
    set_auto_script_cleanup()
    set_auto_script_write()
    set_auto_script_permissions()
    set_auto_script_reload()
    set_auto_script_enable()

    # Download package to mount
    repo_mount()
    repo_copy()
    repo_extract()

    # CTM installation
    install_copy()
    install_ctm_enterprise_manager()
    install_ctm_server()

    # API
    api_add_environment()
    api_login()
    # Add server
    if not api_server_already_added():
        api_add_server()

    # Start Control-M/Agent
    start_agent_process()

    # Install add ons
    install_forecast()
    install_bim()

    logging.info("Control-M v{} installed successfully".format(version_dict[version]['version']))
