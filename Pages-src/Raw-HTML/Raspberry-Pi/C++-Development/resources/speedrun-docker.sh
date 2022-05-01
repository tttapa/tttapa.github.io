sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
# Add the Docker GPG key and PPA repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
source /etc/os-release
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable"
# Install Docker
sudo apt install -y docker-ce
# Add your user to the docker group so you can run Docker without sudo
sudo usermod -aG docker ${USER}
# Log in again so group membership is up-to-date
su - ${USER}