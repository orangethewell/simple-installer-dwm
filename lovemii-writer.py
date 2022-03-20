import os
import sys
import subprocess as sp

if os.getuid() != 0:
    print("It only works a root")
    os.system("sudo python " + sys.argv[0])

username = sp.getoutput("whoami")
doasconfig = f"""permit persist :{username}
permit nopass :{username} cmd zzz
permit nopass :{username} cmd halt
permit nopass :{username} cmd shutdown
"""
print(doasconfig)
file1 = open("/etc/doas.conf", "w")
file1.write(doasconfig)
print("writing xsession...")
sp.call(["sudo", "mkdir", "/usr/share/xsessions/"])
xsession = """[Desktop Entry]
Name=DWM
Comment=Starts Dynamic Window Manager
Exec=/usr/local/bin/dwm
Type=Application
"""
file2 = open("/usr/share/xsessions/dwm.desktop", "w")
file2.write(xsession)
