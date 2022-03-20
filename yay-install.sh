echo "Installing AUR Helper"
sudo pacman -S git
mkdir Githome
echo "Downloading yay..."
sudo git clone https://aur.archlinux.org/yay.git Githome/yay
cd Githome/yay
sudo chown -R orangethewell:orangethewell $HOME/Githome/yay
chmod 777 .
echo "Baking yay..."
makepkg -si
echo "Yay done!"
