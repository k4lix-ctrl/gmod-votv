import os
import sys
import time
import ctypes
import requests
import zipfile
import tempfile
import shutil
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)

REPO_ZIP_URL = "https://github.com/goochmikrob/gmod-votv/archive/refs/heads/main.zip"
TARGET_SUBDIR = "gmod-votv-main/gm-votv/resources"
UI_LIB_PATH_IN_ARCHIVE = "gmod-votv-main/gm-votv/code/ui_lib/wingui.txt"

FONTS_DIR = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
STEAM_DIR = Path("C:/Program Files (x86)/Steam")  # стандартный путь
GARRYSMOD_DATA = STEAM_DIR / "steamapps/common/GarrysMod/garrysmod/data/starfall"
TARGET_UI_DIR = Path("gmod-votv/gm-votv/code/ui_lib")  # относительный путь внутри starfall

TEMP_WORK_DIR = Path.cwd() / "votv_temp"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_font(font_path):
    try:
        font_name = font_path.name
        target_path = FONTS_DIR / font_name
        
        if target_path.exists():
            return True
        
        shutil.copy2(font_path, target_path)
        
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, font_name)
        winreg.CloseKey(key)
        return True
    except:
        return False

def find_garrysmod_folder():
    """Ищет папку Garry's Mod автоматически"""
    possible_paths = [
        Path("C:/Program Files (x86)/Steam/steamapps/common/GarrysMod"),
        Path("C:/Program Files/Steam/steamapps/common/GarrysMod"),
        Path("D:/Steam/steamapps/common/GarrysMod"),
        Path("E:/Steam/steamapps/common/GarrysMod"),
        Path(os.path.expanduser("~") + "/.steam/steam/steamapps/common/GarrysMod"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def main():
    print(f"{Fore.RED}╔══════════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.RED}║     V O T V   -   F O N T   &   U I   I N S T A L L E R                  ║")
    print(f"{Fore.RED}╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

    if not is_admin():
        print(f"{Fore.YELLOW}[!] Administrator rights required for font installation.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    print(f"{Fore.CYAN}[0/4] Locating Garry's Mod installation...")
    gmod_path = find_garrysmod_folder()
    
    if not gmod_path:
        print(f"{Fore.RED}[!] Garry's Mod not found in default locations!")
        custom_path = input("Enter path to Garry's Mod folder manually (or press Enter to exit): ").strip()
        if custom_path:
            gmod_path = Path(custom_path)
        else:
            sys.exit(1)
    
    starfall_path = gmod_path / "garrysmod/data/starfall"
    ui_dest_path = starfall_path / TARGET_UI_DIR
    
    print(f"{Fore.GREEN}[OK] Found Garry's Mod at: {gmod_path}")
    print(f"{Fore.GREEN}[OK] Starfall UI target: {ui_dest_path}\n")

    TEMP_WORK_DIR.mkdir(exist_ok=True)
    
    print(f"{Fore.CYAN}[1/4] Downloading from GitHub...")
    try:
        resp = requests.get(REPO_ZIP_URL, stream=True)
        resp.raise_for_status()
        
        zip_path = TEMP_WORK_DIR / "repo.zip"
        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"{Fore.GREEN}[OK] Downloaded\n")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        input("Press Enter...")
        sys.exit(1)

    print(f"{Fore.CYAN}[2/4] Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(TEMP_WORK_DIR)
    print(f"{Fore.GREEN}[OK] Extracted\n")

    resources_path = TEMP_WORK_DIR / TARGET_SUBDIR
    print(f"{Fore.MAGENTA}╔══════════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.MAGENTA}║                    [1/2] INSTALLING FONTS                                ║")
    print(f"{Fore.MAGENTA}╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    if resources_path.exists():
        ttf_files = list(resources_path.rglob("*.ttf"))
        
        if ttf_files:
            installed = 0
            for font in ttf_files:
                print(f"  → {font.name}...", end=' ')
                if install_font(font):
                    print(f"{Fore.GREEN}✓")
                    installed += 1
                else:
                    print(f"{Fore.YELLOW}⊙ already installed")
                time.sleep(5)
            print(f"\n{Fore.GREEN}[OK] Installed {installed}/{len(ttf_files)} fonts\n")
        else:
            print(f"{Fore.YELLOW}[!] No TTF files found\n")
    else:
        print(f"{Fore.RED}[!] Resources folder not found!\n")

    print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║                    [2/2] INSTALLING UI LIBRARY                           ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    ui_source = TEMP_WORK_DIR / UI_LIB_PATH_IN_ARCHIVE
    if ui_source.exists():

        ui_dest_path.mkdir(parents=True, exist_ok=True)
        
        dest_file = ui_dest_path / "wingui.lua"
        shutil.copy2(ui_source, dest_file)
        
        print(f"{Fore.GREEN}[OK] Installed: {dest_file}")
        
        readme_file = ui_dest_path / "README.txt"
        with open(readme_file, 'w') as f:
            f.write("WinGUI Library for StarfallEx\n")
            f.write("================================\n")
            f.write(f"Installed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("How to use:\n")
            f.write("1. Open Starfall Editor in Garry's Mod\n")
            f.write("2. Create new script\n")
            f.write("3. Use: require('gmod-votv/gm-votv/code/ui_lib/wingui')\n")
            f.write("\nOriginal author: StyledStrike\n")
            f.write("Required permission: 'input'\n")
        print(f"{Fore.GREEN}[OK] Created README.txt with usage info\n")
    else:
        print(f"{Fore.RED}[!] UI library not found in archive!\n")

    print(f"{Fore.CYAN}[4/4] Cleaning up...")
    shutil.rmtree(TEMP_WORK_DIR, ignore_errors=True)
    print(f"{Fore.GREEN}  → Removed temporary files\n")

    print(f"{Fore.GREEN}╔══════════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.GREEN}║                         INSTALLATION COMPLETE                            ║")
    print(f"{Fore.GREEN}╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Fore.CYAN}✓ Fonts installed to Windows")
    print(f"{Fore.CYAN}✓ UI library installed to: {ui_dest_path}")
    print(f"\n{Fore.YELLOW}Next steps:")
    print(f"  1. Restart Garry's Mod (if open)")
    print(f"  2. Open Starfall Editor")
    print(f"  3. Use: {Fore.GREEN}require('gmod-votv/gm-votv/code/ui_lib/wingui')")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}")
        input("Press Enter...")