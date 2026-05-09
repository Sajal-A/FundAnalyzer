"""
test_frontend_integration.py
──────────────────────────────
Test script to verify frontend-backend integration.

Run this before starting the full application to ensure everything is working.

Usage:
    python test_frontend_integration.py
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def test_api_connection(base_url: str = "http://localhost:8000") -> bool:
    """Test connection to backend API."""
    print_header("Testing Backend API Connection")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        
        health_data = response.json()
        print_success(f"Connected to backend API at {base_url}")
        
        print_info(f"API Status: {health_data.get('status')}")
        print_info(f"Version: {health_data.get('version')}")
        print_info(f"Database: {health_data.get('db')}")
        print_info(f"Vector Store: {health_data.get('vector_store')}")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {base_url}")
        print_warning("Make sure backend is running: python main.py")
        return False
    
    except Exception as e:
        print_error(f"API connection error: {str(e)}")
        return False


def test_dependencies():
    """Test if all required dependencies are installed."""
    print_header("Testing Dependencies")
    
    dependencies = {
        "streamlit": "Streamlit UI framework",
        "requests": "HTTP client library",
        "pandas": "Data processing",
        "plotly": "Interactive visualizations",
    }
    
    all_present = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print_success(f"{package} - {description}")
        except ImportError:
            print_error(f"{package} NOT INSTALLED - {description}")
            all_present = False
    
    if not all_present:
        print_warning("Install missing dependencies:")
        print(f"  cd frontend && pip install -r requirements.txt")
    
    return all_present


def test_frontend_files():
    """Test if all required frontend files exist."""
    print_header("Checking Frontend Files")
    
    required_files = {
        "frontend/app.py": "Main Streamlit application",
        "frontend/config.py": "Configuration file",
        "frontend/components/chat_interface.py": "Chat component",
        "frontend/components/diagnostic_response.py": "Diagnostic response component",
        "frontend/components/transparency_layer.py": "Transparency layer component",
        "frontend/components/orchestration_animation.py": "Orchestration animation",
        "frontend/utils/api_client.py": "API client",
        "frontend/utils/state_manager.py": "State management",
        "frontend/styles/theme.py": "Styling theme",
        "frontend/requirements.txt": "Dependencies",
    }
    
    all_present = True
    
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print_success(f"{file_path} - {description}")
        else:
            print_error(f"{file_path} NOT FOUND - {description}")
            all_present = False
    
    return all_present


def test_diagnose_endpoint(base_url: str = "http://localhost:8000") -> bool:
    """Test the diagnose endpoint with a sample query."""
    print_header("Testing Diagnose Endpoint")
    
    payload = {
        "query": "Why did our Global Equity Fund slow down this quarter?",
        "fund_id": "GEF001",
        "period": "2026-Q1",
        "user_id": "test_user",
        "mode": "standard"
    }
    
    try:
        print_info("Sending diagnostic request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/diagnose",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        elapsed_time = time.time() - start_time
        
        response_data = response.json()
        
        print_success(f"Diagnose endpoint responded in {elapsed_time:.2f}s")
        print_info(f"Trace ID: {response_data.get('trace_id')}")
        print_info(f"Fund ID: {response_data.get('fund_id')}")
        print_info(f"Period: {response_data.get('period')}")
        print_info(f"Confidence: {response_data.get('overall_confidence', {}).get('level')}")
        print_info(f"Latency: {response_data.get('latency_ms')}ms")
        
        # Check required fields
        required_fields = [
            "trace_id", "fund_id", "period", "overall_confidence",
            "root_cause", "peer_comparison", "recommendations"
        ]
        
        missing_fields = [f for f in required_fields if f not in response_data]
        if missing_fields:
            print_warning(f"Missing response fields: {missing_fields}")
            return False
        
        print_success("Response has all required fields")
        return True
    
    except requests.exceptions.Timeout:
        print_error("Request timeout - backend took too long to respond")
        return False
    
    except Exception as e:
        print_error(f"Diagnose endpoint error: {str(e)}")
        return False


def test_audit_endpoint(base_url: str = "http://localhost:8000", trace_id: str = None) -> bool:
    """Test the audit endpoint."""
    print_header("Testing Audit Endpoint")
    
    if not trace_id:
        print_warning("Skipping audit test - no trace_id available")
        return True
    
    try:
        print_info(f"Fetching audit data for trace: {trace_id[:16]}...")
        
        response = requests.get(
            f"{base_url}/audit/{trace_id}",
            timeout=30
        )
        response.raise_for_status()
        
        audit_data = response.json()
        
        print_success("Audit endpoint responded successfully")
        print_info(f"Session ID: {audit_data.get('trace_id', 'N/A')[:16]}...")
        print_info(f"Agent calls: {len(audit_data.get('agent_calls', []))}")
        print_info(f"Conflicts: {len(audit_data.get('conflicts', []))}")
        
        return True
    
    except Exception as e:
        print_error(f"Audit endpoint error: {str(e)}")
        return False


def test_configuration():
    """Test frontend configuration."""
    print_header("Testing Configuration")
    
    # Check for .env file
    env_file = Path("frontend/.env")
    env_example = Path("frontend/.env.example")
    
    if env_file.exists():
        print_success("frontend/.env found")
    else:
        print_warning("frontend/.env not found")
        print_info(f"Copy from template: cp frontend/.env.example frontend/.env")
    
    if env_example.exists():
        print_success("frontend/.env.example found")
    
    # Check config.py
    config_file = Path("frontend/config.py")
    if config_file.exists():
        print_success("frontend/config.py found")
    else:
        print_error("frontend/config.py not found")


def test_requirements():
    """Test if all requirements are met."""
    print_header("Testing Requirements")
    
    checks = {
        "Python 3.9+": True,  # Assumed if script runs
        "Backend running": False,
        "Frontend files present": False,
        "Dependencies installed": False,
    }
    
    # Test backend
    try:
        requests.get("http://localhost:8000/health", timeout=2)
        checks["Backend running"] = True
    except:
        checks["Backend running"] = False
    
    # Test files
    checks["Frontend files present"] = test_frontend_files()
    
    # Test dependencies
    checks["Dependencies installed"] = test_dependencies()
    
    print_header("Requirements Summary")
    
    all_met = True
    for requirement, status in checks.items():
        if status:
            print_success(requirement)
        else:
            print_error(requirement)
            all_met = False
    
    return all_met


def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   Fund Performance Diagnostic AI - Integration Test Suite  ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    print(Colors.RESET)
    
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    results = {}
    
    results["Dependencies"] = test_dependencies()
    results["Frontend Files"] = test_frontend_files()
    results["Configuration"] = test_configuration()
    results["API Connection"] = test_api_connection()
    
    # Get trace_id from diagnose endpoint for audit test
    trace_id = None
    if results["API Connection"]:
        diagnose_success = test_diagnose_endpoint()
        results["Diagnose Endpoint"] = diagnose_success
        # Note: In a real scenario, extract trace_id from response
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = Colors.GREEN + "✓" if result else Colors.RED + "✗"
        print(f"{symbol}{Colors.RESET} {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print(Colors.GREEN + Colors.BOLD)
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ✓ All tests passed! Ready to launch the application.     ║")
        print("║                                                            ║")
        print("║  Start the application:                                   ║")
        print("║    Windows: start.bat                                      ║")
        print("║    Linux/Mac: bash start.sh                                ║")
        print("║                                                            ║")
        print("║  Frontend: http://localhost:8501                          ║")
        print("║  Backend: http://localhost:8000                           ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(Colors.RESET)
        return 0
    else:
        print(Colors.RED + Colors.BOLD)
        print("╔════════════════════════════════════════════════════════════╗")
        print(f"║  ✗ {total - passed} test(s) failed. Check requirements above.         ║")
        print("║                                                            ║")
        print("║  Troubleshooting:                                          ║")
        print("║  1. Ensure backend is running: python main.py              ║")
        print("║  2. Install dependencies: pip install -r requirements.txt  ║")
        print("║  3. Check frontend files are in place                      ║")
        print("║                                                            ║")
        print("║  See QUICK_START.md for detailed setup instructions        ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(Colors.RESET)
        return 1


if __name__ == "__main__":
    exit(main())
