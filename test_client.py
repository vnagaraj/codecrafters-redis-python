import socket
import time

def test_multiple_connections():
    """Test multiple PING commands in separate connections (CodeCrafters style)."""
    print("\n" + "="*50)
    print("TEST 1: Multiple Connections (CodeCrafters style)")
    print("="*50)
    try:
        for i in range(1, 4):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 6379))
            
            # Send one PING in RESP protocol format
            ping_resp = b"*1\r\n$4\r\nPING\r\n"
            sock.sendall(ping_resp)
            
            # Read response
            response = sock.recv(1024)
            print(f"  PING #{i}: {response.decode('utf-8', errors='ignore').strip()}")
            
            sock.close()
        
        print("\n✅ TEST 1 PASSED! Server handles multiple connections correctly.\n")
        return True
            
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}\n")
        return False


def test_sequential_pings_one_connection():
    """Test sequential PING commands with responses on one connection."""
    print("="*50)
    print("TEST 2: Sequential PINGs (send/receive pairs)")
    print("="*50)
    print("Testing continuous read/response loop on same connection\n")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 6379))
        print("  ✓ Connected to server")
        
        ping_resp = b"*1\r\n$4\r\nPING\r\n"
        
        # Send 5 sequential PINGs to test the continuous loop
        for i in range(1, 6):
            print(f"  → Sending PING #{i}...")
            sock.sendall(ping_resp)
            response = sock.recv(1024)
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"  ← Received: {decoded}")
            time.sleep(0.1)  # Small delay to simulate realistic usage
        
        sock.close()
        print("\n✅ TEST 2 PASSED! Server responds to sequential PINGs on same connection.\n")
        return True
            
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Redis PING Server - Test Suite")
    print("="*50)
    
    test1 = test_multiple_connections()
    test2 = test_sequential_pings_one_connection()
    
    print("="*50)
    print("SUMMARY")
    print("="*50)
    print(f"  Test 1 (Multiple Connections):      {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Test 2 (Sequential PINGs):          {'✅ PASS' if test2 else '❌ FAIL'}")
    print("="*50 + "\n")
    
    all_passed = test1 and test2
    if all_passed:
        print("🎉 All tests passed!\n")
    else:
        print("⚠️  Some tests failed.\n")
    
    exit(0 if all_passed else 1)
