import threading
import requests
import time

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.lock = threading.Lock()
    
    def add_proxies(self, proxy_list):
        """Add new proxies to the list"""
        with self.lock:
            self.proxies.extend(proxy_list)

    def check_proxies(self):
        """Check each proxy every 10s, remove dead ones"""
        while True:
            time.sleep(10)
            with self.lock:
                for proxy in list(self.proxies):  # Copy to avoid modifying during iteration
                    if not self.is_proxy_alive(proxy):
                        self.proxies.remove(proxy)
                        print(f"Removed dead proxy: {proxy}")
    
    def is_proxy_alive(self, proxy):
        """Check if a proxy is alive (5s timeout)"""
        try:
            response = requests.get("http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def rotate_proxy(self):
        """Rotate proxies every 30s"""
        while True:
            time.sleep(30)
            with self.lock:
                if self.proxies:
                    self.current_proxy = self.proxies[0]
                    self.proxies = self.proxies[1:] + [self.current_proxy]  # Rotate proxies
                    print(f"Rotated to proxy: {self.current_proxy}")

    def get_current_proxy(self):
        """Get the currently active proxy"""
        with self.lock:
            return self.current_proxy

proxy_manager = ProxyManager()

# Start background tasks
threading.Thread(target=proxy_manager.check_proxies, daemon=True).start()
threading.Thread(target=proxy_manager.rotate_proxy, daemon=True).start()
