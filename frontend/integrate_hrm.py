#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRM Frontend Auto-Integration Script
=====================================

Automatische Integration der HRM-Komponenten ins Frontend.
HAK/GAL Verfassung-konform nach Artikel 6 (Empirische Validierung).
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Basis-Pfad
BASE_PATH = Path("D:/MCP Mods/HAK_GAL_SUITE/frontend_new")

def backup_file(filepath):
    """Erstellt Backup einer Datei"""
    if filepath.exists():
        backup_path = filepath.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        filepath.rename(backup_path)
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
    
    # Find the navigation items section
    if "const navigationItems = [" in content:
        # Add HRM items after Query item
        hrm_items = """  {
    name: 'Query',
    href: '/query',
    icon: MessageSquare,
    description: 'Query Interface'
  },
  {
    name: 'HRM',
    href: '/hrm',
    icon: Brain,
    description: 'Neural Reasoning',
    badge: 'NEW'
  },"""
        
        content = content.replace(
            "  {\n    name: 'Query',\n    href: '/query',\n    icon: MessageSquare,\n    description: 'Query Interface'\n  },",
            hrm_items
        )
        
        # Add Brain import if not present
        if "Brain" not in content:
            content = content.replace(
                "import {",
                "import {\n  Brain,"
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
    
    # Add import
    if "import" in content:
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import'):
                import_end = i
                break
        
        lines.insert(import_end, "import HRMDashboard from '@/components/dashboard/HRMDashboard';")
        content = '\n'.join(lines)
    
    # Add HRM Dashboard component (find a good place in the grid)
    if "<div className=" in content and "grid" in content:
        # Add before the closing of main content div
        insertion_point = content.rfind("</div>\n    </div>\n  );")
        if insertion_point > 0:
            hrm_widget = """
        {/* HRM Neural Reasoning System */}
        <div className="col-span-12 lg:col-span-8">
          <HRMDashboard />
        </div>
"""
            content = content[:insertion_point] + hrm_widget + content[insertion_point:]
            
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

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("HRM Frontend Integration Script")
    print("HAK/GAL Verfassung-konform")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not BASE_PATH.exists():
        print(f"❌ Frontend directory not found: {BASE_PATH}")
        return
    
    # Check dependencies
    check_dependencies()
    
    # Create backups
    print("\n📦 Creating backups...")
    files_to_backup = [
        BASE_PATH / "src" / "ProApp.tsx",
        BASE_PATH / "src" / "components" / "ProNavigation.tsx",
        BASE_PATH / "src" / "pages" / "ProDashboard.tsx"
    ]
    
    for file in files_to_backup:
        if file.exists():
            backup_file(file.parent / file.name)
    
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
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
