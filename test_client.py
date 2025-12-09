import socket
import time

def test_ping_server():
    """Test the Redis server with multiple PINGs."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 6379))
        
        print("✓ Connected to Redis server on localhost:6379")
        print("\nSending 3 PING commands...\n")
        
        # Send 3 PINGs in one batch
        sock.sendall(b"PING\r\nPING\r\nPING\r\n")
        
        # Read responses
        response = sock.recv(1024)
        print(f"Raw response: {response}")
        print(f"Decoded: {response.decode('utf-8', errors='ignore')}")
        
        pong_count = response.count(b"+PONG")
        print(f"\n✅ Got {pong_count} PONGs (expected 3)")
        
        sock.close()
        
        if pong_count == 3:
            print("✅ Test PASSED! Server handles multiple PINGs correctly.\n")
            return True
        else:
            print(f"❌ Test FAILED! Expected 3 PONGs but got {pong_count}\n")
            return False
            
    except ConnectionRefusedError:
        print("❌ ERROR: Could not connect to server at localhost:6379")
        print("   Make sure the server is running with: python3 app/main.py\n")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Redis PING Server Test")
    print("=" * 50 + "\n")
    
    success = test_ping_server()
    
    exit(0 if success else 1)
