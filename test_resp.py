import socket
import time

def test_ping_debug():
    """Debug test to see what data redis-cli actually sends."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 6379))
        
        print("✓ Connected to Redis server on localhost:6379")
        print("\nSending PING using raw socket (mimicking redis-cli format)...\n")
        
        # This is how redis-cli sends PING in RESP protocol
        # *1 = array with 1 element
        # $4 = bulk string of 4 bytes
        # PING = the command
        ping_command = b"*1\r\n$4\r\nPING\r\n"
        
        sock.sendall(ping_command)
        sock.sendall(ping_command)  # Send twice
        
        # Read responses
        response = sock.recv(1024)
        print(f"Raw response: {response}")
        print(f"Decoded: {response.decode('utf-8', errors='ignore')}")
        
        pong_count = response.count(b"+PONG")
        print(f"\n✅ Got {pong_count} PONGs (expected 2)")
        
        sock.close()
        
        if pong_count == 2:
            print("✅ Test PASSED!\n")
            return True
        else:
            print(f"❌ Test FAILED! Expected 2 PONGs but got {pong_count}\n")
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
    print("Redis RESP Protocol PING Test")
    print("=" * 50 + "\n")
    
    success = test_ping_debug()
    
    exit(0 if success else 1)
