# WoL Server Configuration
# Copy this file and rename to config.py, then edit the values below

CONFIG = {
    # Server port - change if 6969 is already in use
    "PORT": 6969,
    
    # Your PC's MAC address - MUST be changed for WoL to work
    # Accepts formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, or XXXXXXXXXXXX
    "PC_MAC_ADDRESS": "2C:F0:5D:57:5C:63",
    
    # Your network's broadcast IP - usually your router IP with .255 at the end
    "BROADCAST_IP": "192.168.254.255",

    # Enable logging to file and console
    "LOG_ENABLED": True
}

# How to find your MAC address:
# Windows: ipconfig /all (look for Physical Address, format like XX-XX-XX-XX-XX-XX)
# Linux/Mac: ip link show or ifconfig (look for HWaddr or ether, format like xx:xx:xx:xx:xx:xx)
# All formats work: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX

# How to find your broadcast IP:
# Usually your network IP with .255 at the end
# e.g., if your router is 192.168.1.1, broadcast is likely 192.168.1.255
# You can also use: ip route show | grep broadcast