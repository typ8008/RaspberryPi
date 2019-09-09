# RaspberryPi
Project to add I2C devices to the Classes.py so it's easier to use

Setup Guide (assumption Rasbian is already installed)

1. Enable I2C in Raspberry PI
    
		sudo raspi-config
    enable I2C under Interfacing Options
2. Add I2C module in modules file
    
		sudo nano /etc/modules
    file need to contain as follows:
  
      
      i2c-bcm2708
      
      i2c-dev
3. Edit modules blacklist
    
		sudo nano /etc/modprobe.d/raspi-blacklist.config
    
		comment out using '#' if #blacklist i2c-bcm2708 exist
4. Install I2C utilities (this may already exist)
    
		sudo apt-get update
    
		sudo apt-get install python-smbus i2c-tools
		
		pip install smbus2 - for Python 2
		
		pip3 install smbus2 - for Python 3
