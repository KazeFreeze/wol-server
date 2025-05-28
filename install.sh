#!/bin/bash

# WoL Server Installation Script for Termux
# This script sets up the Wake-on-LAN server

echo "🚀 WoL Server Installation Script"
echo "=================================="

# Update packages
echo "📦 Updating packages..."
pkg update && pkg upgrade -y

# Install required packages
echo "📦 Installing required packages..."
pkg install -y python nodejs-lts wol termux-api git curl

# Create config if it doesn't exist
if [ ! -f "config.py" ]; then
  echo "⚙️  Creating config file from template..."
  cp config_template.py config.py
  echo "✏️  Please edit config.py with your MAC address and network settings!"
else
  echo "✅ Config file already exists"
fi

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x wol_server.py
chmod +x install.sh

# Create systemd-style service script for termux
echo "📋 Creating service management script..."
cat >service.sh <<'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "Starting WoL Server..."
        python3 wol_server.py &
        echo $! > wol_server.pid
        echo "WoL Server started (PID: $(cat wol_server.pid))"
        ;;
    stop)
        if [ -f wol_server.pid ]; then
            PID=$(cat wol_server.pid)
            kill $PID 2>/dev/null
            rm wol_server.pid
            echo "WoL Server stopped"
        else
            echo "WoL Server is not running"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f wol_server.pid ] && kill -0 $(cat wol_server.pid) 2>/dev/null; then
            echo "WoL Server is running (PID: $(cat wol_server.pid))"
        else
            echo "WoL Server is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF

chmod +x service.sh

# Create update script
echo "🔄 Creating update script..."
cat >update.sh <<'EOF'
#!/bin/bash
echo "🔄 Updating WoL Server from Git..."

# Stop service if running
./service.sh stop

# Pull latest changes
git pull origin main

# Restart service
./service.sh start

echo "✅ Update complete!"
EOF

chmod +x update.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit config.py with your PC's MAC address"
echo "2. Run: ./service.sh start"
echo "3. Test: curl http://localhost:8080/status"
echo ""
echo "🔧 Service management:"
echo "  ./service.sh start   - Start the server"
echo "  ./service.sh stop    - Stop the server"
echo "  ./service.sh restart - Restart the server"
echo "  ./service.sh status  - Check status"
echo ""
echo "🔄 To update from Git:"
echo "  ./update.sh"
