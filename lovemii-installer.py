from gettext import install
from operator import is_
from pathlib import Path
import  subprocess as sp
import os
import pip
import socket
import pacman

home = Path(os.environ.get('HOME'))

def check_connection(host="8.8.8.8", port=53, timeout=3):
    load = ["/", "|", "\\", "-"]
    loadid = 0
    def check():
        try: 
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            return False

    while check() != True:
        print(f"checking internet connection... {load[loadid]}\r")

        if loadid > len(load) - 1:
            loadid = 0
        else:
            loadid += 1
                    
def import_with_autoinstall(package: str, import_name=None):
    try:
        if import_name:
            return __import__(import_name)
        else:
            return __import__(package)
    except ImportError:
        pip.main(["install", package])
    if import_name:
        return __import__(import_name)
    else:
        return __import__(package)

def check_on_path(app: str) -> bool :
    whereis = sp.getoutput(f"whereis {app}")
    if whereis.split(":")[1] in ("", " "):
        return False
    else:
        return True

def check_package_exists(package: str) -> bool :
    pacman_is = sp.getstatusoutput(f"pacman -Qi {package}")[0]
    if pacman_is == 1:
        return False
    elif pacman_is == 0:
        return True

def install_package(name: str, dependencies: list[str] = None, aur_dependencies: list[str] = None, git_repository: str | None = None, git_home: Path = home.joinpath("git"), is_aur: bool = False, baking_closure = None):
    print(f"installing {name}...")
    
    if check_package_exists(name) or check_on_path(name):
        print(f"{name} is already installed, skipping...")
    
    else:
        if dependencies != None and len(dependencies) > 0:
            print("installing dependencies...")
            cmd = ['sudo', "pacman", "-Sy", "--noconfirm"]
            cmd.extend(dependencies)
            check_connection()
            if os.getuid != 0:
                retcode = sp.call(cmd)

            print(f"installed {len(dependencies)} with retcode {retcode}")
            if retcode != 0:
                Exception("Error trying to install package.")
            else:
                print(f"{name}'s dependencies installed!")

        if aur_dependencies != None and len(aur_dependencies) > 0:
            print("installing AUR dependencies...")
            check_connection()
            cmd = ["yay", "-Sy", "--noconfirm"]
            cmd.extend(aur_dependencies)
            retcode = sp.call(cmd)

            if retcode != 0:
                Exception("Error trying to install package.")
            else:
                print(f"{name}'s AUR dependencies installed!")

        if is_aur: 
            print("downloading package...")
            check_connection()
            retcode = sp.call(["yay", "-Sy", "--noconfirm", name])

            if retcode != 0:
                Exception("Error trying to install package.")
            else:
                print(f"{name} installed!")

        elif not is_aur and git_repository == "" or git_repository == None:
            print("installing package...")
            check_connection()
            if os.getuid != 0:
                retcode = sp.call(['sudo', "pacman", "-Sy", "--noconfirm", name])
            
            if retcode != 0:
                Exception("Error trying to install package.")
            else:
                print(f"{name} installed!")

        elif git_repository != "" and git_repository != None:
            print(f"Cloning {name} repo...")
            sp.call(["mkdir", f"{git_home.as_posix()}/{name}"])
            check_connection()
            sp.call(["git", "clone", git_repository, f"{git_home.as_posix()}/{name}"])
            print("Clone done!")
            print(f"Baking {name}...")
            if baking_closure:
                baking_closure(f"{git_home.as_posix()}/{name}")
            else:
                sp.call(["make", "-C", f"{git_home.as_posix()}/{name}"])
                sp.call(["sudo", "make", "-C", f"{git_home.as_posix()}/{name}", "install"])

if __name__ == "__main__":
    print("Loading pip dependencies for this installer")
    pacman = import_with_autoinstall("python-pacman", "pacman")

    print()
    print("Starting LovingMii install...".center(40))
    print(40 * "=")
    print("Checking installed deps...")

    install_package("dwm",
            ["libx11", "libxinerama", "slop"
            "libxft"],
            git_repository="https://github.com/orangethewell/dwm.git"
        )

    install_package("flarity",
        aur_dependencies=[
            "ttf-fira-code",
            "ttf-blex-nerd-font-git",
            "nerd-fonts-victor-mono",
            "libxft-bgra",
            "ttf-material-design-iconic-font",
            "noto-fonts-cjk-jp-vf",
            "tff-joypixels"
        ],
        git_repository="https://github.com/BeyondMagic/flarity.git"
    )

    install_package("dmenu",
        git_repository="https://github.com/BeyondMagic/dmenu.git"
    )    

    if not check_on_path("eww"):
        print("Installing eww...")
        print("eww is made in rust, you will need to wait Rust configuration to continue the installation if it's not configured")
        deps = []
        if not check_package_exists("rustup"):
            deps.append("rustup")
        if not check_package_exists("gtk3"):
            deps.append("gtk3")
        if not check_package_exists("pango"):
            deps.append("pango")
        if not check_package_exists("gdk-pixbuf2"):
            deps.append("gdk-pixbuf2")
        if not check_package_exists("cairo"):
            deps.append("cairo")
        if not check_package_exists("glib2"):
            deps.append("glib2")
        if not check_package_exists("gcc-libs"):
            deps.append("gcc-libs")
        if not check_package_exists("glibc"):
            deps.append("glibc")
        print("installing any dependency...")
        if os.getuid != 0:
            sp.call(['sudo', 'python', '-c', '"import pacman; pacman.install([' + ', '.join(deps) + '], needed=True"'])
        print("Cloning eww repo...")
        sp.call(["mkdir", f"{home}/Githome/suckless/eww"])
        sp.call(["git", "clone", "https://github.com/elkowar/eww.git", f"{home}/Githome/suckless/eww"])
        print("Clone done!")
        print("Cargoring eww...")
        sp.call(["cargo", "build", "--manifest-path", f"{home}/Githome/suckless/eww"])
        sp.call(["sudo", "mv", f"{home}/Githome/suckless/eww/target/release/eww", "usr/local/bin"])
        print("eww installed!")
    else:
        print("eww is already installed, skipping...")

    install_package("picom-ibhagwan-git", is_aur=True) 
    install_package("zsh",
    dependencies=[
        "zsh-autosuggestions",
        "zsh-syntax-highlighting"
    ])
    install_package("xorg-xrdb", aur_dependencies=["xgetres"])
    install_package("pulseaudio", dependencies=[
        "pulseaudio-alsa", 
        "alsa-card-profiles", 
        "alsa-firmware", 
        "alsa-lib", 
        "alsa-plugins", 
        "alsa-utils",
        "mpd",
        "mpc",
        "doas",
        "dash",
        "ncmpcpp"
    ])

    install_package("feh")
    install_package("polkit-dumb-agent-git", is_aur=True)
    install_package("dunst")
    install_package("notify-send.sh",
        dependencies=[
            "libnotify"
        ],
        is_aur=True
    )
    install_package("xdotool")
    install_package("colorpicker",
        dependencies=[
            "libxcomposite",
            "libxfixes"
        ],
        git_repository="https://github.com/BeyondMagic/mod-colorpicker.git"
    )
    install_package("xnotify",
        dependencies=[
            "imlib2"
        ],
        git_repository="https://github.com/BeyondMagic/mod-xnotify.git"
    )
    install_package("sddm")
    install_package("xsettingsd")
    install_package("c-lolcat", is_aur=True)
    install_package("imagemagick")
    install_package("exa")
    install_package("scrot")
    install_package("nsxiv", is_aur=True)
    install_package("dash",
    aur_dependencies=[
        "dashbinsh"
    ]
    )
    install_package("unclutter")
    install_package("skippy-xd-git", is_aur=True)
    install_package("mpv")
    install_package("zathura",
    dependencies=[
        "zathura-pdf-poppler",
        "zathura-cb"
    ])
    install_package("slock",
        git_repository="https://github.com/BeyondMagic/slock.git")

    install_package("songrec")
    install_package("nincat-git", is_aur=True)
    install_package("neovim")
    install_package("advcpmv", is_aur=True)
    install_package("brave-bin", is_aur=True)
    print()
    print(40*"=")
    print()
    print("Starting system configuration...")
    print("enabling sddm...")
    sp.call(["sudo", "systemctl", "enable", "sddm.service"])
    print("Configuring zsh...")
    zsh_path = sp.getoutput("which zsh")
    sp.call(["sudo", "chsh", "-s", zsh_path])
    print("Adding extra config into .zshrc...")
    try:
        zshrc = open(f"{home}/.zshrc", "a")

    except FileNotFoundError:
        zshrc = open(f"{home}/.zshrc", "x")
     
    nincat_path = sp.getoutput("which nincat")
    zshrc.write(f"dash {nincat_path} --random --center")
    print("nincat attached")
    
    print("configuring doas and dwm...")
    sp.call(["sudo", "python", os.path.realpath(__file__).replace("lovemii-installer.py", "") + "lovemii-writer.py"])
    
    print("configuring mpd...")
    sp.call(["mkdir", "-p", f"{home.as_posix()}/.config/mpd"])
    try: mpd_config = open(f"{home.as_posix()}/.config/mpd.conf", "x")
    except: mpd_config = open(f"{home.as_posix()}/.config/mpd.conf", "w")
    mpdconf = f"""music_directory "{home.as_posix()}/music//"
    playlist_directory "{home.as_posix()}/music/playlists"
    db_file "{home.as_posix()}/.config/mpd.db"
    log_file "{home.as_posix()}/.config/mpd.log"
    pid_file "{home.as_posix()}/.config/mpd.pid"
    state_file "{home.as_posix()}/.config/mpdstate"
    
    audio_output {{
        type "pulse"
        name "pulse audio"
    }}
    
    port "6600" """
    print(mpdconf)
    mpd_config.write(mpdconf)
    
    print("Configuring xbindkeys...")
    xbkconf = open(home.as_posix() + "/.xbindkeysrc", "w")
    xbkconfig = """# Flarity Terminal
    "flarity"
        m:0x50 + c:36
            Super + Return
            
    # Simple terminal with float status
    "flarity -T 'float'"
        m:0x90 + c:22
            Super + Back

    # See all windows open
    "skippy-xd"
        m:0x90 + c:135
            Super + Menu

    # Seek more mpd
    "mpc -q seek +00:00:04"
        m:0x90 + c:171
            Mod2+Mod4 + XF86AudioNext
    
    # Seek less mpd
    "mpc -q seek -00:00:04"
        m:0x90 + c:173
            Mod2+Mod4 + XF86AudioPrev

    # Increase volume of mpc
    "mpc -q volume $(( $(mpc | grep --line-buffered -hoE '[0-9] {2, }' | tail -n 1) + 1))"
        m:0x90 + c:123
            Mod2+Mod4 + XF86AudioRaiseVolume
    
    # Decrease volume of mpc
    "mpc -q volume $(( $(mpc | grep --line-buffered -hoE '[0-9] {2, }' | tail -n 1) - 1))"
        m:0x90 + c:123
            Mod2+Mod4 + XF86AudioLowerVolume
    """
    xbkconf.write(xbkconfig)

    git_home: Path = home.joinpath("git")
    print("Cloning MaGiCK repo...")
    sp.call(["mkdir", f"{git_home.as_posix()}/MaGiCK"])
    check_connection()
    sp.call(["git", "clone", "https://github.com/BeyondMagic/MaGiCK.git", f"{git_home.as_posix()}/MaGiCK"])
    print("Clone done!")
    print("moving .config...")
    sp.call(["mv", f"{git_home}/MaGiCK/.config/", f"{home}/.config/"])
    print("moving shared icons...")
    sp.call(["sudo", "mv", f"{git_home}/MaGiCK/usr/share/icons/", f"/usr/share/icons/"])
    print("moving sddm...")
    sp.call(["sudo", "mv", f"{git_home}/MaGiCK/usr/share/sddm/", f"/usr/share/sddm/"])
    print("moving sddm.conf...")
    sp.call(["sudo", "mv", f"{git_home}/MaGiCK/etc/sddm.conf", f"/etc/sddm.conf"])
    print("moving local icons...")
    sp.call(["mv", f"{git_home}/MaGiCK/.local/icons/", f"{home.as_posix()}/.local/icons/"])
    print("Configuring autostart.sh...")
    dwm_path = Path(home.as_posix() + "/dwm/")
    if not dwm_path.exists(): dwm_path.mkdir()
    try:
        autostart = open(f"{dwm_path.as_posix()}/autostart.sh", "x")
    except:
        autostart = open(f"{dwm_path.as_posix()}/autostart.sh", "w")
    
    autostart_script = """
    eww daemon
    eww open bottom
    eww open top
    picom --blur-method dual_kawase --blur-strength 20 -b
    
    feh --bg-scale $HOME/Imagens/wallpaper.png &
    xbindkeys
    mpd & disown
    """
    print("setting autostart.sh...")
    autostart.write(autostart_script)
    print("install done!")
   