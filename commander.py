#! python
import configparser
import subprocess
import os
import re
from pathlib import Path
from time import sleep
import sys
import signal
from _thread import start_new_thread

def cont_log(p, hf, f):
    if hf:
        while True:
            line = p.readline().decode('windows-1252')
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

    def run_emulator(self):
        if not self.config.has_section("EMULATOR"):
            print("Running without emulator")
            return
        emu_conf = self.config["EMULATOR"]
        if not (self.config.has_option('EMULATOR', 'use_emulator') and emu_conf["use_emulator"] == "yes"):
            print("Running without emulator")
            return
        self.emu_command = self.jar_prefix("EMULATOR")
        self.emu_command = self.emu_command + [str(Path(emu_conf["command"]).expanduser()) , "-avd", emu_conf["device_id"], "-verbose"]
        if self.config.has_option("EMULATOR", "logcat_tags"):
            self.emu_command = self.emu_command + ["-logcat", emu_conf["logcat_tags"]]
        print("Using Emulator")
        # self.emu_command = self.emu_command + ["-wipe-data","-qemu"]
        self.emu_command = self.emu_command + ["-wipe-data","-no-window","-qemu"] #, "-enable-kvm"]
        if self.config.has_option("EMULATOR", "log") and emu_conf["log"] == "yes":
            self.f = open(emu_conf["logfile"], "a")
            self.f_err = open(emu_conf["logfile_err"], "a")
            self.f.write("\n\nRunning command " + str(self.emu_command) + "\n")
            self.f.flush()
            self.f_err.write("\n\nRunning command " + str(self.emu_command) + "\n")
            self.f_err.flush()
            print("Emulator logging enabled. Logging to " + emu_conf["logfile"] + " and " + emu_conf["logfile_err"])
            print("Starting Emulator...")
            self.emu_proc = subprocess.Popen(self.emu_command, stdout=self.f, stderr=self.f_err)
        else:
            print("Starting Emulator...")
            self.emu_proc = subprocess.Popen(self.emu_command)
        # wait for device to come online
        print("Emulator invoked!")
        # on Windows you have to use 'findstr' instead of 'grep' and use the right syntax for paths, e.g. \\ instead of /
        self.adb_port_command = ["grep", "emulator: control console listening on port ",  "log/emu.log"]
        # on Windows the option 'shell=True' is necessary to run the command
        self.emu_name = subprocess.run(self.adb_port_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.decode("utf-8").strip()
        while self.emu_name == None or not self.emu_name.startswith("emulator: control console listening on port "):
            sleep(0.2)
            print("sleeping")
            self.emu_name = subprocess.run(self.adb_port_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.decode("utf-8").strip()
        print("Done emulator init!")
        self.emu_name = self.emu_name[len("emulator: control console listening on port "):]
        self.emu_name = re.findall('\d+', self.emu_name)[0]
        self.emu_name = "emulator-" + self.emu_name
        print("Emulator: " + self.emu_name)
        self.check_command = ["adb", "-s", self.emu_name, "shell", "getprop", "sys.boot_completed"]
        check_out = subprocess.run(self.check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip()
        while check_out != "1":
            sleep(0.2)
            check_out = subprocess.run(self.check_command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout.decode("utf-8").strip()
        print("Emulator online!")

    def install_dependencies(self,apk):
        if not self.config.has_section("EMULATOR"):
            return
        emu_conf = self.config["EMULATOR"]
        if not (self.config.has_option('EMULATOR', 'install_dependencies') and emu_conf["install_dependencies"] == "yes"):
            return
        self.install_app_command = ["adb", "-s", self.emu_name, "install", "-g", apk]

        self.config["APP"]["id"] = os.path.split(apk)[1].split(".apk")[0]

        print("Installing app: " + self.config["APP"]["id"] + ".apk" + "...")
        p = subprocess.run(self.install_app_command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

        print("Installing mate...")
        self.install_mate_command = ["adb", "-s", self.emu_name, "install", "app-debug.apk"]

        p = subprocess.run(self.install_mate_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

        print("Installing mate tests...")
        self.install_mate_tests_command = ["adb", "-s", self.emu_name, "install", "app-debug-androidTest.apk"]

        p = subprocess.run(self.install_mate_tests_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

        self.create_files_dir()
        
    def grant_permission(self):
        print("Granting read/write permission for external storage...")
        self.app_command = ['adb', "-s", self.emu_name, 'shell', 'pm', 'grant', self.config['APP']['id'], 'android.permission.READ_EXTERNAL_STORAGE']
        cmd = "adb -s " + self.emu_name + " shell pm grant" + " " + self.config['APP']['ID'] + " " + "android.permission.READ_EXTERNAL_STORAGE"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        
        self.app_command = ['adb', "-s", self.emu_name, 'shell', 'pm', 'grant', self.config['APP']['id'], 'android.permission.WRITE_EXTERNAL_STORAGE']
        cmd = "adb -s " + self.emu_name + " shell pm grant" + " " + self.config['APP']['ID'] + " " + "android.permission.WRITE_EXTERNAL_STORAGE"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def run_app(self):
        print("Starting app...")
        self.app_command = ['adb', "-s", self.emu_name, 'shell', 'monkey', '-p', self.config['APP']['id'], '1']
        p = subprocess.run(self.app_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
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
            self.mate_server_proc = subprocess.Popen(self.mate_server_command, stdout=subprocess.PIPE)
            
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

    def push_system_events(self):
        print("Pushing list of system events onto app-internal storage of MATE...")
        cmd = "bash.exe --login -i -c" + " " + "'./push-systemEvents.sh" + " " + self.config['APP']['ID'] + "'"   
        print(cmd)        
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()             
        print(out)                
        print(err)              
        print("Done") 

    def push_manifest(self):
        print("Pushing Manifest onto app-internal storage of MATE...")
        cmd = "bash.exe --login -i -c" + " " + "'./push-manifest.sh" + " " + self.config['APP']['ID'] + "'"   
        print(cmd)        
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()             
        print(out)                
        print(err)              
        print("Done") 

    def push_static_info(self):
        print("Pushing Static Info onto app-internal storage of MATE...")           
        cmd = "bash.exe --login -i -c" + " " + "'./push-staticInfo.sh" + " " + self.config['APP']['ID'] + "'"  
        print(cmd)  
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()              
        print(out)                  
        print(err)               
        print("Done")

    def push_static_strings(self):
        print("Pushing Static Strings onto app-internal storage of MATE...")
        cmd = "bash.exe --login -i -c" + " " + "'./push-staticStrings.sh" + " " + self.config['APP']['ID'] + "'"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def push_media_files(self):
        print("Pushing MediaFiles onto external storage...")
        cmd = "bash.exe --login -i -c" + " " + "'./push-mediafiles.sh" + " " + self.emu_name + "'"   
        print(cmd)        
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()             
        print(out)                
        print(err)              
        print("Done") 

    def push_test_cases(self):
        print("Pushing recorded Test Cases onto Emulator...")
        cmd = "bash.exe --login -i -c" + " " + "'./push-testcases.sh" + " " + self.config['APP']['ID'] + "'"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def fetch_test_cases(self):
        print("Fetching recorded Test Cases from emulator...")
        cmd = "bash.exe --login -i -c" + " " + "'./fetch-testcases.sh" + " " + self.config['APP']['ID'] + "'"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def run_mate_tests(self, flag):
        print("Wait for app to finish starting up...")
        sleep(float(self.config['MATE']['wait_for_app']))
        print("Running tests...")
        package = self.config['APP']['ID']
        strategy = self.config['MATE']['test']
        if "replay" in flag:
            strategy = "ExecuteMATEReplayRun"

        self.test_command = ['adb', "-s", self.emu_name, 'shell', 'am', 'instrument', '-w', '-r', '-e', 'debug', 'false',
                             '-e', 'jacoco', 'false', '-e', 'packageName', package, '-e', 'class',
                             "'org.mate." + strategy + "'", 'org.mate.test/android.support.test.runner.AndroidJUnitRunner']
        p = subprocess.run(self.test_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def stop_emulator(self):
        print("Closing emulator...")
        cmd = "bash.exe --login -i -c" + " " + "'adb -s " + self.emu_name + " emu kill'"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
        print("Done")

    def adb_root(self):
        print("Restarting ADB as root...")
        cmd = "bash.exe --login -i -c" + " " + "'adb -s " + self.emu_name + " root'"
        print(cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.stdout.decode("utf-8").strip(), p.stderr.decode("utf-8").strip()
        print(out)
        print(err)
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
        flag = ""
        if len(sys.argv) > 2:
            flag = sys.argv[2]

        print("Flags: " + str(flag))

        com.install_dependencies(apk)
        com.run_mate_server()
        com.run_app()
        com.adb_root()
        # it may take some time until ADB is ready in root mode
        sleep(3)
        com.push_static_strings()
        if "intent" in flag:
            com.push_system_events()
            com.push_manifest()
            com.push_static_info()
            com.push_media_files()
        # com.grant_permission()
        if "replay" in flag:
            com.push_test_cases()
        com.run_mate_tests(flag)
        if "record" in flag:
            com.fetch_test_cases()
        sleep(5)
    com.stop()
