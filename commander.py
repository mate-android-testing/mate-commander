#!/usr/bin/env python3
import configparser
import subprocess
import os
import re
from pathlib import Path
from time import sleep
import sys
import signal
from _thread import start_new_thread
from enum import Enum, auto, unique

@unique
class OperatingSystem(Enum):
    Windows = auto()
    Linux = auto()


def get_operating_system() -> OperatingSystem:
    if sys.platform == "linux":
        return OperatingSystem.Linux
    elif sys.platform == "win32":
        return OperatingSystem.Windows
    else:
        print("Unsupported operating system")
        exit(1)


def cont_log(p, hf, f):
    encoding = {OperatingSystem.Linux: "utf-8", OperatingSystem.Windows: "windows-1252"}
    operating_system = get_operating_system()

    if hf:
        while True:
            line = p.readline().decode(encoding[operating_system])
            if line != '':
              #the real code does filtering here
              f.write(line + "\n")
            else:
              break
    else:
        while True:
            line = p.readline().decode()
            if line != '':
              #the real code does filtering here
              print(line)
            else:
              break

class Commander:
    def __init__(self):
        pass

    def parse_config(self, name="config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(name)

    def validate_config(self):
        valid_config = True
        if self.config.has_section("EMULATOR"):
            if not self.config.has_option('EMULATOR', 'command'):
                valid_config = False
                print("Missing mandatory EMULATOR options command")
            if not self.config.has_option('EMULATOR', 'device_id'):
                valid_config = False
                print("Missing mandatory EMULATOR options device_id")
            if ( self.config.has_option("EMULATOR", "log")
                 and self.config["EMULATOR"]["log"] == "yes"
                 and not (self.config.has_option('EMULATOR', 'logfile')
                          and self.config.has_option('EMULATOR', 'logfile_err'))
               ):
                valid_config = False
                print("With emulator log flag active: Missing mandatory EMULATOR options logfile and/or logfile_err")
            if ( self.config.has_option("EMULATOR", "create_avd")
                 and self.config["EMULATOR"]["create_avd"] == "yes"
                 and not self.config.has_option('EMULATOR', 'avdmanager_command')
               ):
                valid_config = False
                print("With emulator create_avd flag active: Missing mandatory EMULATOR option avdmanager_command")
        if self.config.has_section("APP"):
            if not self.config.has_option("APP", "id"):
                valid_config = False
                print("Missing mandatory APP option id")
        else:
            valid_config = False
            print("Missing mandatory section APP")
        if self.config.has_section("MATE_SERVER"):
            if not self.config.has_option("MATE_SERVER", "command"):
                valid_config = False
                print("Missing mandatory MATE_SERVER option command")
            if ( self.config.has_option("MATE_SERVER", "log")
                 and self.config["MATE_SERVER"]["log"] == "yes"
                 and not (self.config.has_option('MATE_SERVER', 'logfile')
                          and self.config.has_option('MATE_SERVER', 'logfile_err'))
               ):
                valid_config = False
                print("With server log flag active: Missing mandatory MATE_SERVER options logfile and/or logfile_err")
        if self.config.has_section("MATE"):
            if not self.config.has_option("MATE", "test"):
                valid_config = False
                print("Missing mandatory MATE option test")
            if not self.config.has_option("MATE", "wait_for_app"):
                valid_config = False
                print("Missing mandatory MATE option wait_for_app")
        else:
            valid_config = False
            print("Missing mandatory section MATE")
        self.valid_config = valid_config
        return self.valid_config

    def jar_prefix(self, section):
        if self.config.has_option(section, 'jar') and self.config[section]['jar'] == "yes":
            return ['java', '-Djava.awt.headless=true', '-Xmx16384m', '-jar']
        return []

    def create_avd(self):
        if not self.config.has_section("EMULATOR"):
            return
        emu_conf = self.config["EMULATOR"]
        if not (self.config.has_option('EMULATOR', 'create_avd') and emu_conf["create_avd"] == "yes"):
            return
        self.create_avd_command = [str(Path(emu_conf["avdmanager_command"]).expanduser()), "create", "avd", "--force", "--name", emu_conf["device_id"], "--abi", "google_apis/x86", "--package", "system-images;android-25;google_apis;x86"]
        print("Creating AVD...")
        p = subprocess.run(self.create_avd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=b'\n')
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def run_popen(self, cmd: list[str], use_shell: bool = True):
        shell_dict = {OperatingSystem.Linux: False, OperatingSystem.Windows: True}
        operating_system = get_operating_system()
        s = shell_dict[operating_system] and use_shell
        return subprocess.Popen(cmd, stdout=self.f, stderr=self.f_err, shell=s, bufsize=0)

    def run_subproc_out_err(self, cmd: list[str], use_shell: bool = True) -> tuple[str, str]:
        shell_dict = {OperatingSystem.Linux: False, OperatingSystem.Windows: True}
        operating_system = get_operating_system()
        s = shell_dict[operating_system] and use_shell
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=s)
        out = p.stdout.decode("utf-8").strip()
        err = p.stderr.decode("utf-8").strip()
        return out, err

    def print_subproc(self, cmd: list[str], use_shell: bool = True) -> tuple[str, str]:
        out, err = self.run_subproc_out_err(cmd, use_shell)
        print(out)
        print(err)

    def run_subproc(self, cmd: list[str], use_shell: bool = True) -> str:
        return self.run_subproc_out_err(cmd, use_shell)[0]

    def run_emulator(self):
        if not self.config.has_section("EMULATOR"):
            print("Running without emulator")
            return
        emu_conf = self.config["EMULATOR"]
        if not (self.config.has_option('EMULATOR', 'use_emulator') and emu_conf["use_emulator"] == "yes"):
            print("Running without emulator")
            return
        self.emu_command = self.jar_prefix("EMULATOR")
        self.emu_command = self.emu_command + [str(Path(emu_conf["command"]).expanduser()), "-avd",
                                               emu_conf["device_id"], "-verbose"]
        if self.config.has_option("EMULATOR", "logcat_tags"):
            self.emu_command = self.emu_command + ["-logcat", emu_conf["logcat_tags"]]
            # Alternative to specify logcat tags (unfortunately the format nor the behaviour is not well-documented):
            # os.environ["ANDROID_LOG_TAGS"] = "*:v" (requires import of os module!)
        if self.config.has_option("EMULATOR", "logcat_file"):
            self.emu_command.extend(("-logcat-output", emu_conf["logcat_file"]))
        print("Using Emulator")
        # self.emu_command = self.emu_command + ["-wipe-data","-no-window", "-qemu", "-enable-kvm"]
        self.emu_command = self.emu_command + ["-wipe-data", "-qemu"]
        # self.emu_command = self.emu_command + ["-wipe-data", "-no-window", "-show-kernel", "-debug-all", "-qemu"]
        if self.config.has_option("EMULATOR", "log") and emu_conf["log"] == "yes":
            self.f = open(emu_conf["logfile"], "a")
            self.f_err = open(emu_conf["logfile_err"], "a")
            self.f.write("\n\nRunning command " + str(self.emu_command) + "\n")
            self.f.flush()
            self.f_err.write("\n\nRunning command " + str(self.emu_command) + "\n")
            self.f_err.flush()
            print("Emulator logging enabled. Logging to " + emu_conf["logfile"] + " and " + emu_conf["logfile_err"])
            print("Starting Emulator...")
            self.emu_proc = self.run_popen(self.emu_command, False)
        else:
            print("Starting Emulator...")
            self.emu_proc = self.run_popen(self.emu_command, False)

        # wait for device to come online
        emu_log_file = self.config['EMULATOR']['logfile']
        self.adb_port_str = "console listening on port "
        self.adb_port_command = ["grep", self.adb_port_str, emu_log_file]
        self.emu_name = self.run_subproc(self.adb_port_command)
        while self.emu_name is None or self.adb_port_str not in self.emu_name:
            sleep(0.2)
            self.emu_name = self.run_subproc(self.adb_port_command)
        self.emu_name = self.emu_name.split(self.adb_port_str)[1]
        self.emu_name = re.findall('\d+', self.emu_name)[0]
        self.emu_name = "emulator-" + self.emu_name
        print("Emulator: " + self.emu_name)
        self.check_command = ["adb", "-s", self.emu_name, "shell", "getprop", "sys.boot_completed"]
        check_out = self.run_subproc(self.check_command)
        while check_out != "1":
            sleep(0.2)
            check_out = self.run_subproc(self.check_command)
        print("Emulator online!")

    def install_dependencies(self, apk):
        if not self.config.has_section("EMULATOR"):
            return
        emu_conf = self.config["EMULATOR"]
        if not (self.config.has_option('EMULATOR', 'install_dependencies') and emu_conf["install_dependencies"] == "yes"):
            return

        api_version_command = ["adb", "-s", self.emu_name, "shell", "getprop", "ro.build.version.sdk"]
        self.api_version = int(subprocess.run(api_version_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                               .stdout.decode("utf-8").strip())

        install_command = ["adb", "-s", self.emu_name, "install", "-g", "-r"]
        if self.api_version >= 30:
            install_command = install_command + ["--force-queryable"]

        install_app_command = install_command + [apk]

        self.config["APP"]["id"] = os.path.split(apk)[1].split(".apk")[0]

        # There seems to be a timing issue on an emulator running API 29 such that the call to 'adb install' is blocking
        # forever. Sleeping at least a couple of seconds seems to resolve the issue for now.
        if self.api_version == 29:
            sleep(5)

        print("Installing app: " + self.config["APP"]["id"] + ".apk" + "...")
        self.print_subproc(install_app_command)
        print("Done")

        print("Installing mate...")
        install_mate_command = install_command + ["app-debug.apk"]
        self.print_subproc(install_mate_command)
        print("Done")

        print("Installing mate tests...")
        install_mate_tests_command = install_command + ["app-debug-androidTest.apk"]
        self.print_subproc(install_mate_tests_command)
        print("Done")

        self.create_files_dir()

    def grant_runtime_permissions(self, package):
        print("Granting read/write/manage runtime permissions for external storage...")
        read_permission_command = ['adb', "-s", self.emu_name, 'shell', 'pm', 'grant', package,
                                   'android.permission.READ_EXTERNAL_STORAGE']
        self.print_subproc(read_permission_command)

        write_permission_command = ['adb', "-s", self.emu_name, 'shell', 'pm', 'grant', package,
                                    'android.permission.WRITE_EXTERNAL_STORAGE']
        self.print_subproc(write_permission_command)

        if self.api_version >= 30:
            # https://developer.android.com/training/data-storage/manage-all-files#enable-manage-external-storage-for-testing
            manage_permission_command = ["adb", "-s", self.emu_name, "shell", "appops", "set", "--uid", package,
                                         "MANAGE_EXTERNAL_STORAGE", "allow"]
            self.print_subproc(manage_permission_command)

        print("Done")

    def run_app(self):
        print("Starting app...")
        self.app_command = ['adb', "-s", self.emu_name, 'shell', 'monkey', '-p', self.config['APP']['id'], '1']
        self.print_subproc(self.app_command)
        print("Done")

    def read_mate_server_properties(self):
        if not os.path.exists("mate-server.properties"):
            return None

        # equip with virtual default section
        with open("mate-server.properties", 'r') as f:
            config_string = '[DEFAULT]\n' + f.read()

        config = configparser.ConfigParser()
        config.read_string(config_string)
        return config

    def run_mate_server(self):
        if not self.config.has_section("MATE_SERVER"):
            print("Running without starting MATE-Server")
            return
        sv_conf = self.config['MATE_SERVER']
        self.mate_server_command = self.jar_prefix("MATE_SERVER")
        self.mate_server_command.append(str(Path(sv_conf["command"]).expanduser()))

        if self.config.has_option("MATE_SERVER", "log") and sv_conf["log"] == "yes":
            self.fs = open(sv_conf["logfile"], "a")
            self.fs_err = open(sv_conf["logfile_err"], "a")
            self.fs.write("\n\nRunning command " + str(self.mate_server_command) + "\n")
            self.fs.flush()
            self.fs_err.write("\n\nRunning command " + str(self.mate_server_command) + "\n")
            self.fs_err.flush()
            print("Server logging enabled. Logging to " + sv_conf["logfile"] + " and " + sv_conf["logfile_err"])
            print("Starting mate server...")
            self.mate_server_proc = subprocess.Popen(self.mate_server_command, stdout=subprocess.PIPE, stderr=self.fs_err)
        else:
            print("Starting mate server...")
            self.mate_server_proc = subprocess.Popen(self.mate_server_command, stdout=subprocess.PIPE, stderr=self.fs_err)

        mate_server_config = self.read_mate_server_properties()

        if mate_server_config is not None:

            if mate_server_config.has_option("DEFAULT", "port"):
                self.mate_server_port = int(mate_server_config["DEFAULT"]["port"])

                if self.mate_server_port == 0:
                    # the mate server prints the actual port to stdout (first line)
                    self.mate_server_port = int(self.mate_server_proc.stdout.readline().strip())

                # share the port to mate
                self.set_port_for_mate()

        has_f = False
        out = None

        # redirect stdout of mate server to log file
        if self.config.has_option("MATE_SERVER", "log") and sv_conf["log"] == "yes":
            has_f = True
            out = self.fs

        # log to file or stdout depending on configuration
        start_new_thread(cont_log, (self.mate_server_proc.stdout, True, self.fs))

    def set_port_for_mate(self):
        exec_str = str.encode('run-as org.mate\ncd /data/user/0/org.mate\nmkdir files\ncd files\necho ' + str(self.mate_server_port) + ' > port\nexit\nexit\n', 'ascii')
        self.set_port_for_mate_command = ['adb', "-s", self.emu_name, 'shell']
        subprocess.run(self.set_port_for_mate_command, input=exec_str)

    def create_files_dir(self):
        # TODO: this seems to be only necessary for the manually-instrumented line coverage APKs
        # this only works if the AUT is debuggable
        print("Creating files dir")
        pkg_name = self.config['APP']['ID']
        exec_str = str.encode('run-as ' + pkg_name + '\nmkdir files\nexit\nexit\n', 'ascii')
        self.set_port_for_mate_command = ['adb', "-s", self.emu_name, 'shell']
        subprocess.run(self.set_port_for_mate_command, input=exec_str)
        print("Done.")

    def push(self, msg, cmd):
        print(msg)
        self.print_subproc(cmd)
        print("Done")

    def push_system_events(self):
        msg = "Pushing list of system events onto MATE's internal storage..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               [os.getcwd() + "/push-systemEvents.sh", self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./push-systemEvents.sh" + " " + self.config['APP']['ID'] + "'"
               }
        self.push(msg, cmd[operating_system])

    def push_manifest(self):
        msg = "Pushing Manifest onto MATE's internal storage..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               ['./push-manifest.sh', self.config[ 'APP']['id'], self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./push-manifest.sh" + " " + self.config['APP']['ID'] + "'"
               }
        self.push(msg, cmd[operating_system])

    def push_static_info(self):
        msg = "Pushing Static Info onto MATE's internal storage..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               ['./push-staticInfo.sh', self.config[ 'APP']['id'], self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./push-staticInfo.sh" + " " + self.config['APP']['ID'] + "'"
               }
        self.push(msg, cmd[operating_system])

    def push_static_strings(self):
        msg = "Pushing Static Strings onto external storage..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               ['./push-staticStrings.sh', self.config['APP']['id'], self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./push-staticStrings.sh" + " " + self.config['APP']['ID'] + "'"
               }
        self.push(msg, cmd[operating_system])

    def push_media_files(self):
        msg = "Pushing MediaFiles onto external storage..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               ['./push-mediafiles.sh', self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./push-mediafiles.sh" + " " + self.emu_name + "'"
               }
        self.push(msg, cmd[operating_system])

    def push_test_cases(self):
        msg = "Pushing recorded Test Cases onto Emulator..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               [os.getcwd() + "/push-testcases.sh", self.config['APP']['ID'], self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./push-testcases.sh" + " " + self.config['APP']['ID'] + "'"
               }
        self.push(msg, cmd[operating_system])

    def fetch_test_cases(self):
        msg = "Fetching recorded Test Cases from emulator..."
        operating_system = get_operating_system()
        cmd = {OperatingSystem.Linux:
               [os.getcwd() + "/fetch-testcases.sh", self.config['APP'][ 'ID'], self.emu_name],
               OperatingSystem.Windows:
               "bash.exe --login -i -c" + " " + "'./fetch-testcases.sh" + " " + self.config['APP']['ID'] + "'"
               }
        self.push(msg, cmd[operating_system])

    def run_mate_tests(self, flags):
        print("Wait for app to finish starting up...")
        sleep(float(self.config['MATE']['wait_for_app']))
        print("Running tests...")
        package = self.config['APP']['ID']
        strategy = self.config['MATE']['test']
        if "replay" in flags:
            strategy = "ExecuteMATEReplayRun"

        # check whether we like to attach a debugger
        debug = 'false'
        if "debug" in flags:
            debug = 'true'

        self.test_command = ['adb', "-s", self.emu_name, 'shell', 'am', 'instrument', '-w', '-r', '-e', 'debug', 'false',
                             '-e', 'jacoco', 'false', '-e', 'wait-for-debugger', debug, '-e', 'packageName', package, '-e', 'class',
                             "'org.mate." + strategy + "'", 'org.mate.test/android.support.test.runner.AndroidJUnitRunner']
        self.print_subproc(self.test_command, False)
        print("Done")

    def stop_emulator(self):
        print("Closing emulator...")
        cmd = {OperatingSystem.Linux: ['adb', "-s", self.emu_name, 'emu', 'kill'],
               OperatingSystem.Windows: "bash.exe --login -i -c" + " " + "'adb -s " + self.emu_name + " emu kill'"}
        operating_system = get_operating_system()
        print(cmd[operating_system])
        self.print_subproc(cmd[operating_system])
        print("Done")

    def adb_root(self):
        print("Restarting ADB as root...")
        cmd = {OperatingSystem.Linux: ['adb', "-s", self.emu_name, 'root'],
               OperatingSystem.Windows: "bash.exe --login -i -c" + " " + "'adb -s " + self.emu_name + " root'"}
        operating_system = get_operating_system()
        self.print_subproc(cmd[operating_system])
        print("Done")

    def merge_emu_log_files(self):
        """Merges the logcat.log and emu.log into a single file."""

        if self.config.has_option("EMULATOR", "logcat_file"):
            logcat_file = self.config["EMULATOR"]["logcat_file"]
            emu_log_file = self.config["EMULATOR"]["logfile"]
            print(f"Appending content of {logcat_file} to {emu_log_file}...")
            with open(emu_log_file, "a+", encoding="ISO-8859-1") as log, \
                    open(logcat_file, "r", encoding="ISO-8859-1") as logcat:
                log.write(logcat.read())
            print("Done")

    def stop(self):
        com.stop_emulator()
        if hasattr(self, "f"):
            self.f.close()
        if hasattr(self, "f_err"):
            self.f_err.close()
        if hasattr(self, "emu_proc"):
            self.emu_proc.terminate()
        if hasattr(self, "fs"):
            self.fs.close()
        if hasattr(self, "fs_err"):
            self.fs_err.close()
        if hasattr(self, "mate_server_proc"):
            self.mate_server_proc.terminate()


if __name__ == "__main__":
    com = Commander()
    def signal_handler(sig, frame):
        print("Received SIGINT, shutting down...")
        com.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    com.parse_config()
    if not com.validate_config():
        exit(1)
    com.create_avd()
    com.run_emulator()
    if len(sys.argv) > 1 and sys.argv[1] == "--emulator_only":
        com.emu_proc.wait()
    else:
        # the path to the APK file in the apps folder, the APK must follow the convention: <package-name>.apk
        apk = sys.argv[1]
        # optional flag(s): intent|record|replay
        flags = ""
        if len(sys.argv) > 2:
            flags = sys.argv[2]

        print("Flags: " + str(flags))

        com.install_dependencies(apk)
        com.grant_runtime_permissions("org.mate")
        com.grant_runtime_permissions(com.config["APP"]["id"])
        com.run_mate_server()
        com.run_app()
        com.adb_root()
        # it may take some time until ADB is ready in root mode
        sleep(3)
        com.push_manifest()
        com.push_static_strings()
        com.push_system_events()
        com.push_static_info()
        com.push_media_files()
        # com.grant_permission()
        if "replay" in flags:
            com.push_test_cases()
        com.run_mate_tests(flags)
        if "record" in flags:
            com.fetch_test_cases()
        com.merge_emu_log_files()
        sleep(5)
    com.stop()
