sudo cp /home/pi/lab/lighting.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl start lighting
sudo systemctl enable lighting
