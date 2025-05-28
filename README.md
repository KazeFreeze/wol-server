# WoL Server for Android (Termux)

A simple HTTP server that sends Wake-on-LAN magic packets to wake up your PC remotely.

## Features

- HTTP API to send Wake-on-LAN packets
- Status and configuration endpoints
- Logging support
- Service management scripts
- Easy Git-based updates

## Installation

### On Android (Termux)

1. **Clone this repository:**

   ```bash
   git clone https://github.com/KazeFreeze/wol-server.git
   cd wol-server
   ```

2. **Run the installation script:**

   ```bash
   ./install.sh
   ```

3. **Configure your settings:**

   ```bash
   nano config.py
   ```

   Edit the MAC address and network settings for your PC.

4. **Start the server:**
   ```bash
   ./service.sh start
   ```

## Configuration

Edit `config.py` to set:

- `PC_MAC_ADDRESS`: Your PC's network card MAC address
- `BROADCAST_IP`: Your network's broadcast IP (usually `192.168.1.255`)
- `PORT`: Server port (default: 8080)
- `LOG_ENABLED`: Enable/disable logging

### Finding Your MAC Address

**Windows:**

```cmd
ipconfig /all
```

Look for "Physical Address"

**Linux/Mac:**

```bash
ip link show
# or
ifconfig
```

Look for "HWaddr" or "ether"

## API Endpoints

- `GET /wol` - Send magic packet to wake PC
- `GET /status` - Check server status
- `GET /config` - View current configuration

## Service Management

```bash
./service.sh start    # Start the server
./service.sh stop     # Stop the server
./service.sh restart  # Restart the server
./service.sh status   # Check if running
```

## Updates

To update the server from Git:

```bash
./update.sh
```

## Usage with Tasker

Create a Tasker task with HTTP Request action:

- Method: GET
- URL: `http://[TAILSCALE_IP]:8080/wol`

## Troubleshooting

1. **Check if wol is installed:**

   ```bash
   wol
   ```

2. **Test locally:**

   ```bash
   curl http://localhost:8080/status
   ```

3. **Check logs:**

   ```bash
   tail -f wol_server.log
   ```

4. **Verify your PC supports WoL:**
   - Enable in BIOS/UEFI settings
   - Enable in network adapter properties (Windows)
   - Use `ethtool -s eth0 wol g` (Linux)

## Security Notes

- This server has no authentication
- Use only on trusted networks
- Consider using Tailscale for secure remote access
