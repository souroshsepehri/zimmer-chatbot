#!/bin/bash

echo "PM2 Management Script for Persian Chatbot"
echo "=========================================="

while true; do
    echo ""
    echo "Select an option:"
    echo "1. Start all services"
    echo "2. Stop all services"
    echo "3. Restart all services"
    echo "4. Reload all services (zero-downtime)"
    echo "5. Check status"
    echo "6. View logs"
    echo "7. Monitor services"
    echo "8. Save configuration"
    echo "9. Delete all processes"
    echo "10. Health check"
    echo "11. Exit"
    echo ""
    read -p "Enter your choice (1-11): " choice

    case $choice in
        1)
            echo "Starting all services..."
            pm2 start ecosystem.config.js --env production
            pm2 save
            ;;
        2)
            echo "Stopping all services..."
            pm2 stop all
            ;;
        3)
            echo "Restarting all services..."
            pm2 restart all
            ;;
        4)
            echo "Reloading all services (zero-downtime)..."
            pm2 reload all
            ;;
        5)
            echo "Current status:"
            pm2 status
            echo ""
            read -p "Press Enter to continue..."
            ;;
        6)
            echo "Viewing logs (Press Ctrl+C to exit):"
            pm2 logs
            ;;
        7)
            echo "Opening monitoring dashboard..."
            pm2 monit
            ;;
        8)
            echo "Saving PM2 configuration..."
            pm2 save
            echo "Configuration saved!"
            read -p "Press Enter to continue..."
            ;;
        9)
            echo "Deleting all processes..."
            pm2 delete all
            echo "All processes deleted!"
            read -p "Press Enter to continue..."
            ;;
        10)
            echo "Checking service health..."
            echo ""
            echo "Backend Health:"
            curl -s http://localhost:8000/health || echo "Backend not responding"
            echo ""
            echo "Frontend Health:"
            curl -s http://localhost:3000 || echo "Frontend not responding"
            echo ""
            read -p "Press Enter to continue..."
            ;;
        11)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done
