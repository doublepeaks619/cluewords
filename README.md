# cluewords
Game server for cluewords.

# Install guide
## Ubuntu 16.04
install mysql:
````sh
sudo apt-get update
sudo apt-get install mysql-server
````

clone code base:
````sh
git clone https://github.com/doublepeaks619/cluewords.git && cd cluewords
````

install pip:
````sh
sudo apt-get install python-pip`
````

install python dependencies:
````sh
cd server
sudo pip install -r python_dependencies.txt
````

install mysql-client:
````sh
sudo apt-get install mysql-client
````

setup database:
````sh
mysql --host localhost --user root --password < create_database.txt
````

forward port 80 to port 5000 (optional, do this if you want to access it via port 80):
````sh
sudo sysctl -w net.ipv4.ip_forward=1
sudo /etc/init.d/procps restart
sudo iptables -t nat -A POSTROUTING -j MASQUERADE
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000
````

run web app:
````sh
python app.py
````
