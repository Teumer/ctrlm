#!/usr/bin/python
import logging
import os
import re
import subprocess
import sys

__author__ = "Joe_Teumer@bmc.com"

log_path = "/tmp/"
log_filename = "{}.log".format(os.path.basename(__file__))


class Menu:

    def __init__(self):
        self.version = 'none'
        os.system('clear')
        sys.stdout.write(self.menu())
        sys.stdout.flush()
        user_input = input()
        logging.info(user_input)

    def test_dict(self):
        version_dict = {
            1: "Control-M 9.0.19.200",
            2: "Control-M 9.0.19.100",
            3: "Control-M 9.0.19.000"
        }
        return version_dict

    def error(self):
        string = "This option is invalid\n" \
                 "\n" \
                 "Press Enter to continue"
        return string

    def menu(self):
        ostring = "\nCONTROL-M Installation Menu\n" \
                 "{}\n" \
                 "\nSelect one of the following menus:\n" \
                 "\n" \
                 "1 - Control-M 9.0.19.200\n" \
                 "2 - Control-M 9.0.19.100\n" \
                 "\n" \
                 "q - Quit\n" \
                 "\n" \
                 " Enter option number --->   []:".format("-" * 29)

        string = "\nCONTROL-M Installation Menu\n" \
                  "{}\n" \
                  "\nSelect one of the following menus:\n" \
                  "\n" \
                  "1 - Control-M 9.0.19.200\n" \
                  "2 - Control-M 9.0.19.100\n" \
                  "\n" \
                  "q - Quit\n" \
                  "\n" \
                  " Enter option number --->   []:".format("-" * 29)
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


class ControlM:
    """ todo move to configparser format """

    def __init__(self):
        self.user_em = 'em1'
        self.user_srv = 's1'
        self.password = 'empass'
        self.user_list = [self.user_em, self.user_srv]
        self.service_directory = "/etc/systemd/system/"
        self.service_ctm_enterprise_manager = self.service_directory + "ctm_enterprise_manager.service"
        self.service_ctm_server = self.service_directory + "ctm_server.service"
        self.service_ctm_agent = self.service_directory + "ctm_agent.service"
        self.service_list = self.service_ctm_enterprise_manager, self.service_ctm_server, self.service_ctm_agent


class InstallationPackage:
    """ todo move to configparser format """

    def __init__(self):
        self.drost = "DROST.9.0.19.200_Linux-x86_64.tar.Z"


class Command:
    """ run shell command and handle logging and return code """

    def __init__(self, command, realtime=False):
        self.command = command
        self.realtime = realtime

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
    for user in ControlM().user_list:
        cmd = "adduser {} -s /bin/csh".format(user)
        Command(cmd)


def set_user_password():
    # Set user password
    password = ControlM().password
    for user in ControlM().user_list:
        cmd = "echo {}:{} | chpasswd".format(user, password)
        Command(cmd)


def set_user_group_wheel():
    # Add user to wheel group
    for user in ControlM().user_list:
        cmd = "usermod -aG wheel {}".format(user)
        Command(cmd)


def set_auto_script_cleanup():
    # Remove already existing services if any
    for service in ControlM().service_list:
        if os.path.exists(service):
            logging.info("Removing {}".format(service))
            os.remove(service)


def set_auto_script_write():
    #
    for service in ControlM().service_list:
        logging.info("Writing {}".format(service))
        with open("/tmp/files/{}".format(service.split('/')[-1], 'r')) as f:
            data = f.read()
        with open(service, 'w') as f:
            for line in data:
                f.write(line)


def set_auto_script_permissions():
    for service in ControlM().service_list:
        cmd = "chmod 644 {}".format(service)
        Command(cmd)


def set_auto_script_reload():
    cmd = "systemctl daemon-reload"
    Command(cmd)


def set_auto_script_enable():
    for service in ControlM().service_list:
        cmd = "systemctl enable {}".format(service)
        Command(cmd)


def set_enterprise_manager_service():
    em_service_file = "ctm_enterprise_manager.service"
    Command("cd /tmp/files && sed -i 's/changeme/{hostname}/g' {a_file}".format(hostname=Command('hostname'),
                                                                                a_file=em_service_file))


def mount_nfs_share():
    # Unmount /mnt if mounted
    Command("if grep -qs '/mnt ' /proc/mounts; then umount /mnt; fi")
    # Mount remote repository
    Command("mount clm-aus-tvl3rt:/nfs/repo /mnt/")


def copy_repo_tmp():
    # Copy remote pack to local
    Command("rsync -avP /mnt/9.0.19.200/* /tmp")


def extract_repo_tmp():
    # Make extract directory
    Command("mkdir /tmp/extract")
    # Untar package to extract directory
    Command("tar xzf /tmp/DROST.9.0.19.200_Linux-x86_64.tar.Z -C /tmp/extract")


def install_ctm_enterprise_manager():
    # Install Control-M/Enterprise Manager
    Command("cd /home/em1 && sudo -u em1 /tmp/extract/setup.sh -silent "
            "/tmp/files/ctm_enterprise_manager_silent_install.xml", realtime=True)


def install_ctm_server():
    # Install Control-M/Server
    Command("cd /home/s1 && sudo -u s1 /tmp/extract/setup.sh -silent "
            "/tmp/files/ctm_server_silent_install.xml", realtime=True)


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
    test
    """
    Command("su - em1 -c \"ctm environment add devEnvironment "
            "\"https://{hostname}:{port}/automation-api\" \"{user}\" \"{password}\"\"".format(
                                                                                        hostname=Command("hostname"),
                                                                                        port=api_get_port(),
                                                                                        user="emuser",
                                                                                        password=ControlM().password))


def api_login():
    # Login to the API dev environment via an API call
    Command("su - em1 -c \"ctm session login\"")


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
    file_handler = logging.FileHandler(log_path + log_filename)
    file_handler_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
    file_handler.setFormatter(file_handler_format)

    # Add handles to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Initialize installation menu
    menu = Menu()
    version = menu.version

    logging.info(version)

    sys.exit(1)

    # Housekeeping
    set_add_user()
    set_user_password()
    set_user_group_wheel()
    set_enterprise_manager_service()
    set_auto_script_cleanup()
    set_auto_script_write()
    set_auto_script_permissions()
    set_auto_script_reload()
    set_auto_script_enable()

    # Download package to mount
    mount_nfs_share()
    copy_repo_tmp()
    extract_repo_tmp()

    # CTM installation
    install_ctm_enterprise_manager()
    install_ctm_server()

    # API
    api_add_environment()
    api_login()
    api_add_server()
