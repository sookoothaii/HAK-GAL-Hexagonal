#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRM Frontend Auto-Integration Script - FIXED VERSION
=====================================================

Automatische Integration der HRM-Komponenten ins Frontend.
HAK/GAL Verfassung-konform nach Artikel 6 (Empirische Validierung).
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Basis-Pfad
BASE_PATH = Path("D:/MCP Mods/HAK_GAL_SUITE/frontend_new")

def backup_file(filepath):
    """Erstellt Backup einer Datei (KOPIERT statt verschiebt)"""
    if filepath.exists():
        backup_path = filepath.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        shutil.copy2(filepath, backup_path)  # FIXED: Use copy instead of rename
        print(f"✅ Backup erstellt: {backup_path.name}")
        return backup_path
    return None

def update_pro_app():
    """Update ProApp.tsx mit HRM-Integration"""
    app_file = BASE_PATH / "src" / "ProApp.tsx"
    
    print("\n📝 Updating ProApp.tsx...")
    
    if not app_file.exists():
        print("❌ ProApp.tsx nicht gefunden!")
        return False
    
    content = app_file.read_text(encoding='utf-8')
    
    # Check if already integrated
    if 'useHRMSocket' in content:
        print("⚠️ HRM bereits integriert in ProApp.tsx")
        return True
    
    # Add imports
    import_section = """// Components
import ProNavigation from '@/components/ProNavigation';
import ProHeader from '@/components/ProHeader';
import { EnterpriseErrorBoundary } from '@/components/EnterpriseErrorBoundary';
import LoadingScreen from '@/components/LoadingScreen';

// HRM Integration
import { useHRMSocket } from '@/hooks/useHRMSocket';
import HRMDashboard from '@/components/dashboard/HRMDashboard';
import HRMQueryInterface from '@/components/interaction/HRMQueryInterface';"""
    
    content = content.replace(
        "// Components\nimport ProNavigation from '@/components/ProNavigation';\nimport ProHeader from '@/components/ProHeader';\nimport { EnterpriseErrorBoundary } from '@/components/EnterpriseErrorBoundary';\nimport LoadingScreen from '@/components/LoadingScreen';",
        import_section
    )
    
    # Add HRM Socket Hook
    hook_section = """  const [isLoading, setIsLoading] = useState(true);
  
  useGovernorSocket();
  useHRMSocket(); // HRM Integration"""
    
    content = content.replace(
        "  const [isLoading, setIsLoading] = useState(true);\n  \n  useGovernorSocket();",
        hook_section
    )
    
    # Add HRM Routes
    routes_addition = """        {/* HRM Neural Reasoning Routes */}
        <Route path="/hrm" element={<HRMQueryInterface />} />
        <Route path="/hrm/dashboard" element={<HRMDashboard />} />
        
        {/* Enterprise route redirects to monitoring */}"""
    
    content = content.replace(
        "        {/* Enterprise route redirects to monitoring */}",
        routes_addition
    )
    
    # Write updated content
    app_file.write_text(content, encoding='utf-8')
    print("✅ ProApp.tsx updated successfully!")
    return True

def update_pro_navigation():
    """Update ProNavigation.tsx mit HRM Links"""
    nav_file = BASE_PATH / "src" / "components" / "ProNavigation.tsx"
    
    print("\n📝 Updating ProNavigation.tsx...")
    
    if not nav_file.exists():
        print("❌ ProNavigation.tsx nicht gefunden!")
        return False
    
    content = nav_file.read_text(encoding='utf-8')
    
    # Check if already integrated
    if 'HRM Query' in content or '/hrm' in content:
        print("⚠️ HRM bereits integriert in ProNavigation.tsx")
        return True
    
    # Find the navigation items section and add HRM
    # Look for the navigationItems array
    nav_pattern = r'(const navigationItems[^=]*=\s*\[)'
    
    if re.search(nav_pattern, content):
        # Create HRM navigation item
        hrm_item = """
  {
    name: 'HRM Neural',
    href: '/hrm',
    icon: Brain,
    description: 'Neural Reasoning System',
    badge: 'NEW'
  },"""
        
        # Insert after the first item in the array
        content = re.sub(
            r'(const navigationItems[^=]*=\s*\[\s*{[^}]+},)',
            r'\1' + hrm_item,
            content,
            count=1
        )
        
        # Add Brain import if not present
        if "Brain" not in content:
            import_pattern = r'(import {[^}]*)'
            content = re.sub(
                import_pattern,
                r'\1, Brain',
                content,
                count=1
            )
        
        nav_file.write_text(content, encoding='utf-8')
        print("✅ ProNavigation.tsx updated successfully!")
        return True
    else:
        print("⚠️ Could not find navigation items section")
        return False

def update_pro_dashboard():
    """Update ProDashboard.tsx mit HRM Widget"""
    dash_file = BASE_PATH / "src" / "pages" / "ProDashboard.tsx"
    
    print("\n📝 Updating ProDashboard.tsx...")
    
    if not dash_file.exists():
        print("❌ ProDashboard.tsx nicht gefunden!")
        return False
    
    content = dash_file.read_text(encoding='utf-8')
    
    # Check if already integrated
    if 'HRMDashboard' in content:
        print("⚠️ HRM bereits integriert in ProDashboard.tsx")
        return True
    
    # Add import at the end of import section
    import_pattern = r'(import[^;]+;\n)(?=\n)'
    last_import = None
    for match in re.finditer(import_pattern, content):
        last_import = match
    
    if last_import:
        insert_pos = last_import.end()
        import_line = "import HRMDashboard from '@/components/dashboard/HRMDashboard';\n"
        content = content[:insert_pos] + import_line + content[insert_pos:]
    
    # Add HRM Dashboard component in the grid
    # Look for a good place to insert it
    grid_pattern = r'(<div className="[^"]*grid[^"]*"[^>]*>)'
    
    if re.search(grid_pattern, content):
        # Find the last card/component in the grid
        last_component = None
        for match in re.finditer(r'</Card>\s*</div>', content):
            last_component = match
        
        if last_component:
            insert_pos = last_component.end()
            hrm_widget = """

        {/* HRM Neural Reasoning System */}
        <div className="col-span-12 lg:col-span-8">
          <HRMDashboard />
        </div>"""
            
            content = content[:insert_pos] + hrm_widget + content[insert_pos:]
            
            dash_file.write_text(content, encoding='utf-8')
            print("✅ ProDashboard.tsx updated successfully!")
            return True
    
    print("⚠️ Could not find suitable insertion point for HRM widget")
    return False

def check_dependencies():
    """Prüft ob alle Dependencies installiert sind"""
    package_json = BASE_PATH / "package.json"
    
    print("\n🔍 Checking dependencies...")
    
    if not package_json.exists():
        print("❌ package.json nicht gefunden!")
        return False
    
    content = package_json.read_text()
    
    required = ['zustand', 'socket.io-client', 'framer-motion', 'lucide-react', 'sonner']
    missing = []
    
    for dep in required:
        if dep not in content:
            missing.append(dep)
    
    if missing:
        print(f"⚠️ Missing dependencies: {', '.join(missing)}")
        print("Run: npm install " + " ".join(missing))
        return False
    
    print("✅ All required dependencies installed!")
    return True

def verify_hrm_files():
    """Verifiziert dass alle HRM-Dateien existieren"""
    print("\n🔍 Verifying HRM files...")
    
    hrm_files = [
        BASE_PATH / "src" / "stores" / "useHRMStore.ts",
        BASE_PATH / "src" / "hooks" / "useHRMSocket.ts",
        BASE_PATH / "src" / "components" / "dashboard" / "HRMDashboard.tsx",
        BASE_PATH / "src" / "components" / "interaction" / "HRMQueryInterface.tsx"
    ]
    
    all_exist = True
    for file in hrm_files:
        if file.exists():
            print(f"✅ {file.name} exists")
        else:
            print(f"❌ {file.name} missing!")
            all_exist = False
    
    return all_exist

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("HRM Frontend Integration Script - FIXED VERSION")
    print("HAK/GAL Verfassung-konform")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not BASE_PATH.exists():
        print(f"❌ Frontend directory not found: {BASE_PATH}")
        return
    
    # Check dependencies
    check_dependencies()
    
    # Verify HRM files exist
    if not verify_hrm_files():
        print("\n⚠️ Some HRM files are missing. Please ensure all HRM components are created first.")
        return
    
    # Create backups
    print("\n📦 Creating backups...")
    files_to_backup = [
        BASE_PATH / "src" / "ProApp.tsx",
        BASE_PATH / "src" / "components" / "ProNavigation.tsx",
        BASE_PATH / "src" / "pages" / "ProDashboard.tsx"
    ]
    
    for file in files_to_backup:
        if file.exists():
            backup_file(file)
    
    # Perform updates
    print("\n🚀 Starting integration...")
    
    results = {
        "ProApp.tsx": update_pro_app(),
        "ProNavigation.tsx": update_pro_navigation(),
        "ProDashboard.tsx": update_pro_dashboard()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)
    
    for file, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{file}: {status}")
    
    if all(results.values()):
        print("\n🎉 HRM Integration completed successfully!")
        print("\nNext steps:")
        print("1. Restart the frontend: npm run dev")
        print("2. Navigate to /hrm to test the new interface")
        print("3. Check /dashboard for HRM widget")
    else:
        print("\n⚠️ Some integrations failed. Please check manually.")
        print("\nManual integration steps:")
        print("1. Add 'import { useHRMSocket } from '@/hooks/useHRMSocket';' to ProApp.tsx")
        print("2. Add 'useHRMSocket();' after useGovernorSocket() in ProApp.tsx")
        print("3. Add HRM routes to ProApp.tsx")
        print("4. Add HRM navigation item to ProNavigation.tsx")
        print("5. Import and add HRMDashboard to ProDashboard.tsx")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
