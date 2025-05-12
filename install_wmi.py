import subprocess
import sys
import os
import platform

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def run_command(command):
    """Run a command and return its output."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main function to install and verify WMI."""
    print("=" * 50)
    print("WMI Module Installation Helper")
    print("=" * 50)
    print()
    
    # Check for administrator privileges
    if not is_admin():
        print("WARNING: This script is not running with administrator privileges.")
        print("Some installation steps may fail without admin rights.")
        print("Please run this script as administrator for best results.")
        print()
        input("Press Enter to continue anyway or Ctrl+C to exit...")
        print()
    
    # Check Python version
    print(f"Python version: {platform.python_version()}")
    print(f"Python path: {sys.executable}")
    print()
    
    # Step 1: Install pywin32
    print("Step 1: Installing pywin32 (required for WMI)")
    success = run_command("pip install pywin32==306")
    if not success:
        print("Failed to install pywin32. Trying alternative method...")
        success = run_command("pip install --upgrade --force-reinstall pywin32==306")
    print()
    
    # Step 2: Install WMI
    print("Step 2: Installing WMI module")
    success = run_command("pip install wmi==1.5.1")
    if not success:
        print("Failed to install WMI. Trying alternative method...")
        success = run_command("pip install --upgrade --force-reinstall wmi==1.5.1")
    print()
    
    # Step 3: Run pywin32 post-install script if on Windows
    if platform.system() == 'Windows':
        print("Step 3: Running pywin32 post-install script")
        scripts_dir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
        postinstall_script = os.path.join(scripts_dir, 'pywin32_postinstall.py')
        
        if os.path.exists(postinstall_script):
            success = run_command(f'"{sys.executable}" "{postinstall_script}" -install')
        else:
            print(f"Could not find pywin32_postinstall.py at {postinstall_script}")
            # Try to find it elsewhere
            for root, dirs, files in os.walk(os.path.dirname(os.path.dirname(sys.executable))):
                if 'pywin32_postinstall.py' in files:
                    postinstall_script = os.path.join(root, 'pywin32_postinstall.py')
                    print(f"Found pywin32_postinstall.py at {postinstall_script}")
                    success = run_command(f'"{sys.executable}" "{postinstall_script}" -install')
                    break
        print()
    
    # Step 4: Verify installation
    print("Step 4: Verifying installation")
    try:
        print("Trying to import wmi module...")
        import wmi
        print("SUCCESS: WMI module imported successfully!")
        
        # Try to use WMI
        print("Trying to create WMI connection...")
        c = wmi.WMI()
        print("SUCCESS: WMI connection created!")
        
        # Try to get some basic info
        print("Trying to get system information...")
        for os_info in c.Win32_OperatingSystem():
            print(f"Computer Name: {os_info.CSName}")
            print(f"Windows Version: {os_info.Caption}")
        
        print("\nWMI is working correctly!")
        return True
    except ImportError as e:
        print(f"FAILED: Could not import wmi module. Error: {e}")
    except Exception as e:
        print(f"FAILED: Error using WMI. Error: {e}")
    
    print("\nTroubleshooting tips:")
    print("1. Make sure you're running this script as administrator")
    print("2. Try restarting your computer")
    print("3. Check if your antivirus is blocking the installation")
    print("4. Try using the basic version of the USB monitoring system that doesn't require WMI")
    return False

if __name__ == "__main__":
    success = main()
    print("\nPress Enter to exit...")
    input()
    sys.exit(0 if success else 1)
