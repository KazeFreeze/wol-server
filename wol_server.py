#!/usr/bin/env python3
import http.server
import socketserver
import subprocess
import json
import urllib.parse
import os
import logging
from datetime import datetime

# Load configuration from config.py
try:
    from config import CONFIG
    print("✅ Configuration loaded from config.py")
except ImportError:
    print("⚠️  config.py not found, using default configuration")
    print("   Please copy config_template.py to config.py and edit it")
    CONFIG = {
        "PORT": 6969,
        "PC_MAC_ADDRESS": "2C:F0:5D:57:5C:63",  # Replace with your PC's MAC address
        "BROADCAST_IP": "192.168.254.255",       # Replace with your network's broadcast IP
        "LOG_ENABLED": True
    }

# Setup logging
if CONFIG["LOG_ENABLED"]:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('wol_server.log'),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.CRITICAL)

class WoLHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default HTTP server logs to avoid clutter
        if CONFIG["LOG_ENABLED"]:
            logging.info(f"HTTP: {format % args}")
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        client_ip = self.client_address[0]
        
        logging.info(f"Request from {client_ip}: {self.path}")
        
        if parsed_path.path == '/wol':
            self.handle_wol_request()
        elif parsed_path.path == '/status':
            self.handle_status_request()
        elif parsed_path.path == '/config':
            self.handle_config_request()
        else:
            self.send_404()
    
    def handle_wol_request(self):
        try:
            # Check if MAC address is configured
            if CONFIG["PC_MAC_ADDRESS"] == "XX:XX:XX:XX:XX:XX":
                response = {
                    "status": "error", 
                    "message": "MAC address not configured. Please edit the script."
                }
                self.send_json_response(response, 400)
                return
            
            # Normalize MAC address format (wol prefers colons)
            mac_address = self.normalize_mac_address(CONFIG["PC_MAC_ADDRESS"])
            
            # Send magic packet using wol
            cmd = ['wol', '-i', CONFIG["BROADCAST_IP"], mac_address]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                response = {
                    "status": "success", 
                    "message": f"Magic packet sent to {mac_address}",
                    "timestamp": datetime.now().isoformat()
                }
                logging.info(f"Magic packet sent successfully to {mac_address}")
                self.send_json_response(response, 200)
            else:
                response = {
                    "status": "error", 
                    "message": f"Failed to send packet: {result.stderr.strip()}",
                    "timestamp": datetime.now().isoformat()
                }
                logging.error(f"wol failed: {result.stderr}")
                self.send_json_response(response, 500)
                
        except subprocess.TimeoutExpired:
            response = {
                "status": "error", 
                "message": "Command timeout",
                "timestamp": datetime.now().isoformat()
            }
            logging.error("wol command timed out")
            self.send_json_response(response, 500)
        except Exception as e:
            response = {
                "status": "error", 
                "message": f"Unexpected error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Unexpected error in WoL request: {str(e)}")
            self.send_json_response(response, 500)
    
    def handle_status_request(self):
        response = {
            "status": "online",
            "service": "WoL Server",
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "configured_mac": CONFIG["PC_MAC_ADDRESS"] != "XX:XX:XX:XX:XX:XX"
        }
        self.send_json_response(response, 200)
    
    def handle_config_request(self):
        # Return sanitized config (without sensitive info)
        response = {
            "port": CONFIG["PORT"],
            "mac_configured": CONFIG["PC_MAC_ADDRESS"] != "XX:XX:XX:XX:XX:XX",
            "broadcast_ip": CONFIG["BROADCAST_IP"],
            "log_enabled": CONFIG["LOG_ENABLED"]
        }
        self.send_json_response(response, 200)
    
    def normalize_mac_address(self, mac):
        """
        Normalize MAC address to colon-separated format that wol prefers.
        Accepts formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX
        """
        # Remove any separators and convert to uppercase
        clean_mac = mac.replace(':', '').replace('-', '').replace(' ', '').upper()
        
        # Validate length
        if len(clean_mac) != 12:
            raise ValueError(f"Invalid MAC address length: {mac}")
        
        # Validate hex characters
        try:
            int(clean_mac, 16)
        except ValueError:
            raise ValueError(f"Invalid MAC address characters: {mac}")
        
        # Format with colons (preferred by wol command)
        formatted_mac = ':'.join([clean_mac[i:i+2] for i in range(0, 12, 2)])
        return formatted_mac
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # For web testing
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_404(self):
        response = {
            "status": "error",
            "message": "Endpoint not found",
            "available_endpoints": ["/wol", "/status", "/config"]
        }
        self.send_json_response(response, 404)

def main():
    PORT = CONFIG["PORT"]
    
    # Check if wol is available
    try:
        subprocess.run(['wol'], capture_output=True)
    except FileNotFoundError:
        print("Error: 'wol' command not found. Please install it:")
        print("  pkg install wol")
        exit(1)
    
    print(f"Starting WoL Server on port {PORT}")
    print(f"Target MAC: {CONFIG['PC_MAC_ADDRESS']}")
    print(f"Broadcast IP: {CONFIG['BROADCAST_IP']}")
    print(f"Logging: {'Enabled' if CONFIG['LOG_ENABLED'] else 'Disabled'}")
    print("\nAvailable endpoints:")
    print(f"  http://localhost:{PORT}/wol - Send magic packet")
    print(f"  http://localhost:{PORT}/status - Check server status")
    print(f"  http://localhost:{PORT}/config - View configuration")
    print("\nPress Ctrl+C to stop the server")
    
    logging.info("WoL Server starting up")
    
    try:
        with socketserver.TCPServer(("", PORT), WoLHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        logging.info("Server shut down by user")
    except Exception as e:
        print(f"Server error: {e}")
        logging.error(f"Server error: {e}")

if __name__ == "__main__":
    main()