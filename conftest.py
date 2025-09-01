import sys
import pathlib

root = pathlib.Path(__file__).resolve().parent
packages_dir = root / "packages"
if packages_dir.exists():
    for pkg in packages_dir.iterdir():
        if pkg.is_dir():
            sys.path.append(str(pkg))

services_dir = root / "services"
if services_dir.exists():
    for service in services_dir.iterdir():
        if service.is_dir():
            sys.path.append(str(service))
