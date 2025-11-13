#!/usr/bin/env python3
"""
Dependency validation and conflict detection for CI/CD pipeline
"""
import sys
import subprocess
import json
from packaging import version

def check_dependency_conflicts():
    """Check for dependency conflicts using pip check"""
    print("Checking for dependency conflicts...")
    
    try:
        result = subprocess.run(
            ['pip', 'check'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("No dependency conflicts found")
            return True
        else:
            print("Dependency conflicts detected:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False

def check_critical_versions():
    """Verify versions of critical packages meet requirements"""
    print("\nChecking critical package versions...")
    
    critical_packages = {
        'torch': ('1.10.0', None),
        'numpy': ('1.21.0', '1.24.0'),
        'opencv-python': ('4.5.0', None),
        'pillow': ('8.0.0', None),
    }
    
    all_ok = True
    
    for package, (min_ver, max_ver) in critical_packages.items():
        try:
            result = subprocess.run(
                ['pip', 'show', package],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"{package}: NOT INSTALLED")
                all_ok = False
                continue
            
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    pkg_version = line.split(':')[1].strip()
                    
                    if min_ver and version.parse(pkg_version) < version.parse(min_ver):
                        print(f"{package}: {pkg_version} is below minimum {min_ver}")
                        all_ok = False
                    elif max_ver and version.parse(pkg_version) > version.parse(max_ver):
                        print(f"{package}: {pkg_version} exceeds maximum {max_ver}")
                    else:
                        print(f"{package}: {pkg_version} (valid)")
                    break
        
        except Exception as e:
            print(f"Error checking {package}: {e}")
            all_ok = False
    
    return all_ok

def generate_dependency_report():
    """Generate detailed dependency report in JSON format"""
    print("\nGenerating dependency report...")
    
    try:
        result = subprocess.run(
            ['pip', 'list', '--format=json'],
            capture_output=True,
            text=True
        )
        
        packages = json.loads(result.stdout)
        
        print(f"Total packages installed: {len(packages)}")
        
        with open('dependency_report.json', 'w') as f:
            json.dump(packages, f, indent=2)
        
        print("Dependency report saved to dependency_report.json")
        
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    conflicts_ok = check_dependency_conflicts()
    versions_ok = check_critical_versions()
    generate_dependency_report()
    
    if conflicts_ok and versions_ok:
        print("\nAll dependency checks passed")
        sys.exit(0)
    else:
        print("\nDependency validation failed")
        sys.exit(1)

# Make it executable:
# bashchmod +x .github/scripts/check_dependencies.py