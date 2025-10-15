#!/usr/bin/env python3
"""
Setup script for connecting to external API at 85.208.254.187
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, Any

class ExternalAPISetup:
    def __init__(self, ip_address: str = "85.208.254.187"):
        self.ip_address = ip_address
        self.common_ports = [80, 443, 8000, 8001, 8002, 8003, 8080, 3000, 5000]
        self.common_endpoints = [
            "/health",
            "/api/health", 
            "/api/chat",
            "/api/simple-chat",
            "/api/smart-chat",
            "/docs",
            "/openapi.json",
            "/status"
        ]
    
    async def test_port(self, port: int) -> Dict[str, Any]:
        """Test if a specific port is open and responding"""
        try:
            url = f"http://{self.ip_address}:{port}"
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as response:
                    return {
                        "port": port,
                        "status": "open",
                        "http_status": response.status,
                        "url": url
                    }
        except aiohttp.ClientError:
            return {
                "port": port,
                "status": "closed",
                "url": f"http://{self.ip_address}:{port}"
            }
        except Exception as e:
            return {
                "port": port,
                "status": "error",
                "error": str(e),
                "url": f"http://{self.ip_address}:{port}"
            }
    
    async def test_endpoints(self, base_url: str) -> Dict[str, Any]:
        """Test common endpoints on a given base URL"""
        results = {}
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                for endpoint in self.common_endpoints:
                    try:
                        url = f"{base_url}{endpoint}"
                        async with session.get(url) as response:
                            results[endpoint] = {
                                "status": response.status,
                                "url": url,
                                "accessible": True
                            }
                    except:
                        results[endpoint] = {
                            "status": "error",
                            "url": f"{base_url}{endpoint}",
                            "accessible": False
                        }
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    async def scan_server(self) -> Dict[str, Any]:
        """Scan the server for open ports and accessible endpoints"""
        print(f"🔍 Scanning server {self.ip_address}...")
        
        # Test common ports
        port_results = []
        for port in self.common_ports:
            result = await self.test_port(port)
            port_results.append(result)
            if result["status"] == "open":
                print(f"✅ Port {port} is open (HTTP {result.get('http_status', 'N/A')})")
            else:
                print(f"❌ Port {port} is closed")
        
        # Find working ports
        working_ports = [r for r in port_results if r["status"] == "open"]
        
        # Test endpoints on working ports
        endpoint_results = {}
        for port_result in working_ports:
            port = port_result["port"]
            base_url = f"http://{self.ip_address}:{port}"
            print(f"\n🔍 Testing endpoints on {base_url}...")
            
            endpoints = await self.test_endpoints(base_url)
            endpoint_results[port] = endpoints
            
            for endpoint, result in endpoints.items():
                if result.get("accessible"):
                    print(f"✅ {endpoint} - Status {result['status']}")
                else:
                    print(f"❌ {endpoint} - Not accessible")
        
        return {
            "ip_address": self.ip_address,
            "port_scan": port_results,
            "working_ports": working_ports,
            "endpoint_tests": endpoint_results
        }
    
    def generate_config(self, scan_results: Dict[str, Any]) -> str:
        """Generate configuration based on scan results"""
        working_ports = scan_results.get("working_ports", [])
        
        if not working_ports:
            return """
# No working ports found. The server might be:
# 1. Behind a firewall
# 2. Running on a non-standard port
# 3. Not configured properly
# 4. Using a different protocol (HTTPS, custom protocol)

# Try these manual configurations:
EXTERNAL_API_URL=http://85.208.254.187
EXTERNAL_API_PORT=8000
EXTERNAL_API_TIMEOUT=30
EXTERNAL_API_ENABLED=true
"""
        
        # Use the first working port
        best_port = working_ports[0]["port"]
        base_url = f"http://{self.ip_address}:{best_port}"
        
        config = f"""# External API Configuration for {self.ip_address}
# Generated based on server scan results

# Basic Configuration
EXTERNAL_API_URL=http://{self.ip_address}
EXTERNAL_API_PORT={best_port}
EXTERNAL_API_TIMEOUT=30
EXTERNAL_API_ENABLED=true

# Full API URL: {base_url}

# Available endpoints found:
"""
        
        # Add endpoint information
        endpoint_tests = scan_results.get("endpoint_tests", {}).get(best_port, {})
        for endpoint, result in endpoint_tests.items():
            if result.get("accessible"):
                config += f"# ✅ {endpoint} - Status {result['status']}\n"
            else:
                config += f"# ❌ {endpoint} - Not accessible\n"
        
        return config

async def main():
    """Main setup function"""
    print("🚀 External API Setup for 85.208.254.187")
    print("=" * 50)
    
    setup = ExternalAPISetup()
    
    # Scan the server
    scan_results = await setup.scan_server()
    
    # Generate configuration
    config = setup.generate_config(scan_results)
    
    # Save configuration
    with open(".env.external_api", "w") as f:
        f.write(config)
    
    print("\n📝 Configuration saved to .env.external_api")
    print("\n" + "=" * 50)
    print("CONFIGURATION:")
    print("=" * 50)
    print(config)
    
    print("\n🔧 Next Steps:")
    print("1. Copy the configuration to your .env file")
    print("2. Start your chatbot server")
    print("3. Test the connection: http://localhost:8002/api/external-api/status")
    print("4. Try sending a message: http://localhost:8002/api/external-api/chat")

if __name__ == "__main__":
    asyncio.run(main())
