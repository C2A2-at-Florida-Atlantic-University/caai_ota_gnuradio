wget -qO - http://repos.emulab.net/emulab.key | sudo apt-key add -
sudo add-apt-repository -y http://repos.emulab.net/powder/ubuntu/
sudo apt-get update

for thing in $*
do
    case $thing in
        gnuradio)
	    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libuhd4.0.0 uhd-host python3-uhd gnuradio
            ;;

        srslte)
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y srslte
            ;;
    esac
done

sudo sysctl -w net.core.rmem_max=24862979
sudo sysctl -w net.core.wmem_max=24862979

sudo ed /etc/sysctl.conf << "EDEND"
a
net.core.rmem_max=24862979
net.core.wmem_max=24862979
.
w
EDEND

#sudo "/usr/lib/uhd/utils/uhd_images_downloader.py -t x310"
