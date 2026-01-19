import os
import subprocess
import shutil
import json
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox

# === CONFIG FOR THIS BUILD ===
MINECRAFT_VERSION = "1.21.10"
MOD_TYPE = "performance"              # performance, quality, pvp, etc.
FABRIC_LOADER_VERSION = "0.18.3"       # Latest stable

# Fabric logo base64 for profile icon
FABRIC_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAAsTAAALEwEAmpwYAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNi4wLjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgPHRpZmY6T3JpZW50YXRpb24+MTwvdGlmZjpPcmllbnRhdGlvbj4KICAgICAgPC9yZGY6RGVzY3JpcHRpb24+CiAgIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+AAAACklEQVQ4y+3TsQ1AIBBE0Z3nOQsg8wD0BQ9fZx/2AAAAAElFTkSuQmCC
"""

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GGStudios Mod Installer")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(root, text="GGStudios Mod Pack", font=("Segoe UI", 20, "bold"), fg="#bb86fc", bg="#1e1e1e").pack(pady=20)
        tk.Label(root, text=f"{MINECRAFT_VERSION} - {MOD_TYPE.capitalize()} Edition", font=("Segoe UI", 12), fg="#ffffff", bg="#1e1e1e").pack(pady=5)

        self.status_label = tk.Label(root, text="Preparing installation...", font=("Segoe UI", 11), fg="#ffffff", bg="#1e1e1e")
        self.status_label.pack(pady=20)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=20, troughcolor="#333333", background="#bb86fc")
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", style="TProgressbar")
        self.progress.pack(pady=20)

        self.root.after(500, self.run_installation)

    def update_status(self, text, progress_value):
        self.status_label.config(text=text)
        self.progress['value'] = progress_value
        self.root.update_idletasks()

    def run_installation(self):
        try:
            self.update_status("Finding Minecraft directory...", 20)
            time.sleep(0.8)
            mc_dir = self.get_minecraft_dir()
            if not os.path.exists(mc_dir):
                raise Exception("Minecraft folder not found!\nInstall Java Edition first.")

            self.update_status("Installing Fabric loader...", 40)
            self.root.update()
            java_exe = self.get_bundled_java()
            if not java_exe:
                raise Exception("Bundled Java not found!")
            version_id, version_folder = self.install_fabric(mc_dir, java_exe)

            self.update_status("Copying mods, packs, and configs...", 60)
            time.sleep(0.6)
            self.root.update()
            self.copy_minecraft_files(version_folder)

            self.update_status("Creating optimized launcher profile...", 80)
            time.sleep(0.4)
            self.root.update()
            self.create_launcher_profile(mc_dir, version_id, version_folder)

            self.update_status("Applying your perfect settings...", 100)
            time.sleep(0.5)
            self.root.update()
            self.set_performance_settings(version_folder)

            time.sleep(0.8)
            self.show_success(version_id, version_folder)

        except Exception as e:
            self.update_status("Installation Failed", 0)
            messagebox.showerror("Error", str(e))

    def show_success(self, version_id, version_folder):
        profile_name = f"GGStudios {MINECRAFT_VERSION} {MOD_TYPE.capitalize()}"
        success_text = f"""
Success! Your pack is ready.

Open Minecraft Launcher → Installations tab
Select '{profile_name}'
→ Click Play!

All your mods and custom settings have been installed.

Enjoy the best performance! 🚀
        """
        success_window = tk.Toplevel(self.root)
        success_window.title("Installation Complete!")
        success_window.geometry("600x400")
        success_window.configure(bg="#1e1e1e")
        success_window.resizable(False, False)

        tk.Label(success_window, text=success_text, font=("Segoe UI", 11), fg="#ffffff", bg="#1e1e1e", justify="left").pack(padx=30, pady=30)
        tk.Button(success_window, text="Close Installer", command=self.root.quit, bg="#bb86fc", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=10)

    def set_performance_settings(self, version_folder):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        bundled_options = os.path.join(base_dir, "minecraftfiles", "options.txt")
        
        if not os.path.exists(bundled_options):
            self.status_label.config(text="Warning: options.txt not found – using Minecraft defaults")
            return
        
        target_options = os.path.join(version_folder, "options.txt")
        shutil.copy2(bundled_options, target_options)
        self.status_label.config(text="Your mods have been installed!")

    def get_minecraft_dir(self):
        home = os.path.expanduser("~")
        if sys.platform == "win32":
            return os.path.join(home, "AppData", "Roaming", ".minecraft")
        elif sys.platform == "darwin":
            return os.path.join(home, "Library", "Application Support", "minecraft")
        else:
            return os.path.join(home, ".minecraft")

    def get_bundled_java(self):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        jdk_dir = os.path.join(base_dir, "java", "jdk-25.0.1+8")
        if not os.path.exists(jdk_dir):
            return None
        java_exe = os.path.join(jdk_dir, "bin", "java.exe" if sys.platform == "win32" else "java")
        return java_exe if os.path.exists(java_exe) else None

    def install_fabric(self, mc_dir, java_exe):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        fabric_jar = os.path.join(base_dir, "fabric", "fabric-installer-1.1.0.jar")
        if not os.path.exists(fabric_jar):
            raise Exception("fabric-installer.jar missing!")
        
        cmd = [java_exe, "-jar", fabric_jar, "client", "-dir", mc_dir, "-mcversion", MINECRAFT_VERSION, "-loader", FABRIC_LOADER_VERSION]
        result = subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0, capture_output=True)
        if result.returncode != 0:
            raise Exception(f"Fabric install failed:\n{result.stderr.decode()}")
        
        version_id = f"fabric-loader-{FABRIC_LOADER_VERSION}-{MINECRAFT_VERSION}"
        version_folder = os.path.join(mc_dir, "versions", version_id)
        if not os.path.exists(version_folder):
            raise Exception("Fabric version folder not created!")
        return version_id, version_folder

    def copy_minecraft_files(self, version_folder):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        mc_files_dir = os.path.join(base_dir, "minecraftfiles")
        if not os.path.exists(mc_files_dir):
            raise Exception("minecraftfiles/ folder missing!")
        
        folders = ["mods", "resourcepacks", "shaderpacks", "config"]
        for folder in folders:
            src = os.path.join(mc_files_dir, folder)
            if os.path.exists(src):
                dst = os.path.join(version_folder, folder)
                shutil.copytree(src, dst, dirs_exist_ok=True)

    def create_launcher_profile(self, mc_dir, version_id, version_folder):
        profiles_file = os.path.join(mc_dir, "launcher_profiles.json")
        if not os.path.exists(profiles_file):
            return
        
        with open(profiles_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        profile_name = f"GGStudios {MINECRAFT_VERSION} {MOD_TYPE.capitalize()}"
        
        java_args = "-Xmx6G -Xms2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M"
        
        data["profiles"][profile_name] = {
            "name": profile_name,
            "type": "custom",
            "lastVersionId": version_id,
            "icon": "data:image/png;base64," + FABRIC_ICON_BASE64.strip(),
            "javaArgs": java_args,
            "gameDir": version_folder
        }
        
        with open(profiles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()