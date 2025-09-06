#!/usr/bin/env python3
"""
OpenCode Universal Launcher with Binary Detection and Environment Injection
Advanced solution with automatic platform detection and binary analysis
"""

import os
import sys
import subprocess
import platform
import struct
import json
import hashlib
import ctypes
from pathlib import Path
import importlib.util
import mmap
import re

class BinaryAnalyzer:
    """Advanced PE/ELF binary analyzer"""
    
    PE_SIGNATURE = b'MZ'
    ELF_SIGNATURE = b'\x7fELF'
    MACHO_SIGNATURES = [0xfeedface, 0xfeedfacf, 0xcafebabe, 0xcefaedfe]
    
    @staticmethod
    def get_binary_type(filepath):
        """Detect binary type through header analysis"""
        with open(filepath, 'rb') as f:
            header = f.read(16)
            
            if header[:2] == BinaryAnalyzer.PE_SIGNATURE:
                return 'PE_WINDOWS'
            elif header[:4] == BinaryAnalyzer.ELF_SIGNATURE:
                return 'ELF_LINUX'
            elif struct.unpack('>I', header[:4])[0] in BinaryAnalyzer.MACHO_SIGNATURES:
                return 'MACHO_DARWIN'
            else:
                # Deep scan for Node.js shebang
                f.seek(0)
                first_line = f.readline()
                if b'#!/usr/bin/env node' in first_line or b'#!/usr/bin/node' in first_line:
                    return 'NODE_SCRIPT'
                return 'UNKNOWN'

class OpenCodeLocator:
    """Sophisticated OpenCode binary locator with multiple search strategies"""
    
    def __init__(self):
        self.platform_system = platform.system()
        self.arch = platform.machine()
        self.npm_global = self._get_npm_global_path()
        self.search_paths = self._build_search_paths()
        
    def _get_npm_global_path(self):
        """Get NPM global installation path"""
        try:
            result = subprocess.run(['npm', 'root', '-g'], 
                                  capture_output=True, 
                                  text=True, 
                                  shell=True)
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except:
            pass
            
        # Fallback paths
        if self.platform_system == 'Windows':
            return Path(os.environ.get('APPDATA', '')) / 'npm' / 'node_modules'
        else:
            return Path.home() / '.npm' / 'node_modules'
    
    def _build_search_paths(self):
        """Build comprehensive search path list"""
        paths = []
        
        # NPM global modules
        if self.npm_global:
            paths.append(self.npm_global / 'opencode-ai')
            
        # Common installation paths
        base_paths = [
            Path.cwd(),
            Path.home() / '.local',
            Path('/usr/local'),
            Path('/opt'),
            Path('C:/Program Files'),
            Path('C:/Program Files (x86)'),
            Path(os.environ.get('PROGRAMFILES', '')),
            Path(os.environ.get('PROGRAMFILES(X86)', '')),
            Path(os.environ.get('LOCALAPPDATA', '')),
            Path(os.environ.get('APPDATA', '')) / 'npm' / 'node_modules'
        ]
        
        # Architecture-specific paths
        arch_variants = {
            'AMD64': ['x64', 'amd64', 'x86_64'],
            'x86': ['x86', 'i386', 'i686'],
            'ARM64': ['arm64', 'aarch64'],
            'arm': ['arm', 'armv7']
        }
        
        current_arch_variants = arch_variants.get(self.arch, [self.arch.lower()])
        
        # Generate all possible paths
        for base in base_paths:
            if not base or not base.exists():
                continue
                
            # Direct paths
            paths.append(base / 'opencode-ai')
            paths.append(base / 'opencode')
            
            # Platform-specific paths
            for arch_variant in current_arch_variants:
                platform_dir = f"opencode-{self.platform_system.lower()}-{arch_variant}"
                paths.append(base / 'opencode-ai' / 'node_modules' / platform_dir)
                paths.append(base / platform_dir)
        
        return [p for p in paths if p and p.exists()]
    
    def find_opencode_binary(self):
        """Locate OpenCode binary using multiple strategies"""
        candidates = []
        
        # Search patterns
        patterns = [
            'opencode.exe',
            'opencode',
            'opencode.app',
            'OpenCode.exe',
            'OpenCode'
        ]
        
        # Binary directories
        bin_dirs = ['bin', 'dist', 'build', 'out', '.', 'lib']
        
        for search_path in self.search_paths:
            for bin_dir in bin_dirs:
                bin_path = search_path / bin_dir
                if not bin_path.exists():
                    continue
                    
                for pattern in patterns:
                    matches = list(bin_path.glob(pattern))
                    for match in matches:
                        if match.is_file():
                            binary_type = BinaryAnalyzer.get_binary_type(str(match))
                            candidates.append({
                                'path': match,
                                'type': binary_type,
                                'size': match.stat().st_size,
                                'score': self._score_candidate(match, binary_type)
                            })
        
        # Sort by score and return best match
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[0] if candidates else None
    
    def _score_candidate(self, path, binary_type):
        """Score candidate based on multiple factors"""
        score = 0
        
        # Binary type matching
        if self.platform_system == 'Windows' and binary_type == 'PE_WINDOWS':
            score += 100
        elif self.platform_system == 'Linux' and binary_type == 'ELF_LINUX':
            score += 100
        elif self.platform_system == 'Darwin' and binary_type == 'MACHO_DARWIN':
            score += 100
        elif binary_type == 'NODE_SCRIPT':
            score += 50
            
        # Path quality
        if 'node_modules' in str(path):
            score += 20
        if self.arch.lower() in str(path).lower():
            score += 30
        if 'bin' in path.parts:
            score += 10
            
        # File size (reasonable executable size)
        size_mb = path.stat().st_size / (1024 * 1024)
        if 1 < size_mb < 200:
            score += 15
            
        return score

class EnvironmentInjector:
    """Advanced environment setup for OpenCode"""
    
    @staticmethod
    def setup_environment():
        """Setup optimal environment for OpenCode"""
        env = os.environ.copy()
        
        # Electron/Chromium flags
        env['ELECTRON_NO_ATTACH_CONSOLE'] = '1'
        env['ELECTRON_ENABLE_LOGGING'] = '0'
        env['NODE_ENV'] = 'production'
        
        # GPU acceleration
        if platform.system() == 'Windows':
            env['OPENCODE_GPU_ACCELERATION'] = '1'
            
        # Memory optimization
        env['NODE_OPTIONS'] = '--max-old-space-size=4096'
        
        return env

class OpenCodeLauncher:
    """Master launcher orchestrating all components"""
    
    def __init__(self):
        self.locator = OpenCodeLocator()
        self.candidate = None
        
    def launch(self):
        """Main launch sequence"""
        print("[*] OpenCode Advanced Launcher v2.0")
        print(f"[*] Platform: {platform.system()} {platform.machine()}")
        
        # Locate binary
        print("[*] Searching for OpenCode binary...")
        self.candidate = self.locator.find_opencode_binary()
        
        if not self.candidate:
            print("[!] OpenCode binary not found")
            self._offer_installation()
            return 1
            
        print(f"[+] Found: {self.candidate['path']}")
        print(f"[+] Type: {self.candidate['type']}")
        
        # Setup environment
        env = EnvironmentInjector.setup_environment()
        
        # Launch based on type
        if self.candidate['type'] == 'NODE_SCRIPT':
            self._launch_node_script(self.candidate['path'], env)
        else:
            self._launch_native_binary(self.candidate['path'], env)
            
        return 0
    
    def _launch_native_binary(self, binary_path, env):
        """Launch native binary with proper setup"""
        print(f"[*] Launching native binary...")
        
        if platform.system() == 'Windows':
            # Windows-specific launch with elevated permissions if needed
            try:
                # Try normal launch first
                subprocess.Popen([str(binary_path)], env=env)
            except Exception as e:
                # Try with shell execute for elevation
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", str(binary_path), None, None, 1
                )
        else:
            # Unix-like systems
            os.execve(str(binary_path), [str(binary_path)], env)
    
    def _launch_node_script(self, script_path, env):
        """Launch Node.js script"""
        print(f"[*] Launching Node.js script...")
        node_cmd = 'node.exe' if platform.system() == 'Windows' else 'node'
        subprocess.Popen([node_cmd, str(script_path)], env=env)
    
    def _offer_installation(self):
        """Offer installation options"""
        print("\n[!] OpenCode not found. Installation commands:")
        print("    npm install -g opencode-ai")
        print("    yarn global add opencode-ai")
        print("    pnpm add -g opencode-ai")

if __name__ == '__main__':
    launcher = OpenCodeLauncher()
    sys.exit(launcher.launch())
