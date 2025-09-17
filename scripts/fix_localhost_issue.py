#!/usr/bin/env python3
"""
FIX LOCALHOST ISSUE - Behebt Windows localhost-Resolution Problem
"""

import subprocess
import sys
import os

def check_hosts_file():
    """Prüfe Windows hosts-Datei"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    
    print("🔍 Checking Windows hosts file...")
    
    try:
        with open(hosts_path, 'r') as f:
            content = f.read()
            
        print("📄 Current hosts file content:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # Prüfe auf IPv6 localhost Einträge
        if "::1 localhost" in content:
            print("⚠️  Found IPv6 localhost entry - this causes the delay!")
            return True
        else:
            print("✅ No problematic IPv6 localhost entry found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading hosts file: {e}")
        return False

def create_hosts_backup():
    """Erstelle Backup der hosts-Datei"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    backup_path = r"C:\Windows\System32\drivers\etc\hosts.backup"
    
    try:
        import shutil
        shutil.copy2(hosts_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def fix_hosts_file():
    """Behebt die hosts-Datei"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    
    print("🔧 Fixing hosts file...")
    print("⚠️  This requires Administrator privileges!")
    
    try:
        with open(hosts_path, 'r') as f:
            lines = f.readlines()
        
        # Entferne IPv6 localhost Einträge
        fixed_lines = []
        for line in lines:
            if "::1 localhost" in line and not line.strip().startswith('#'):
                print(f"🗑️  Removing: {line.strip()}")
                # Kommentiere aus statt zu löschen
                fixed_lines.append(f"# {line.strip()}  # Disabled to fix localhost delay\n")
            else:
                fixed_lines.append(line)
        
        # Schreibe gefixte Datei
        with open(hosts_path, 'w') as f:
            f.writelines(fixed_lines)
        
        print("✅ Hosts file fixed!")
        return True
        
    except PermissionError:
        print("❌ Permission denied - run as Administrator!")
        return False
    except Exception as e:
        print(f"❌ Error fixing hosts file: {e}")
        return False

def test_localhost_fix():
    """Teste ob localhost-Fix funktioniert"""
    print("🧪 Testing localhost fix...")
    
    import requests
    import time
    
    # Test localhost
    start = time.time()
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        end = time.time()
        localhost_time = (end - start) * 1000
        
        print(f"📊 localhost response time: {localhost_time:.2f}ms")
        
        if localhost_time < 100:
            print("✅ localhost fix successful!")
            return True
        else:
            print("❌ localhost still slow")
            return False
            
    except Exception as e:
        print(f"❌ localhost test failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 LOCALHOST ISSUE FIXER")
    print("=" * 50)
    print("Fixes Windows localhost resolution delay")
    print("=" * 50)
    
    # Prüfe hosts-Datei
    has_issue = check_hosts_file()
    
    if has_issue:
        print("\n🔧 FIXING LOCALHOST ISSUE...")
        
        # Erstelle Backup
        if create_hosts_backup():
            # Behebe hosts-Datei
            if fix_hosts_file():
                print("\n🧪 Testing fix...")
                test_localhost_fix()
            else:
                print("\n❌ Fix failed - manual intervention required")
        else:
            print("\n❌ Could not create backup - aborting")
    else:
        print("\n✅ No localhost issue detected")
    
    print("\n" + "=" * 50)
    print("🎯 ALTERNATIVE SOLUTIONS:")
    print("1. Always use 127.0.0.1 instead of localhost")
    print("2. Run as Administrator and fix hosts file")
    print("3. Disable IPv6 in Windows network settings")
    print("=" * 50)

if __name__ == "__main__":
    main()


