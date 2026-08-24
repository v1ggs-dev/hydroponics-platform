"""
Hydroponics Platform — Database & Supabase Manager
Handles Prisma schema pushes, Prisma Studio web UI, and database seeding.
"""

import os
import sys
import subprocess
import webbrowser

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

class DatabaseManager:
    @staticmethod
    def push_schema() -> bool:
        """Pushes Prisma schema to Supabase Cloud PostgreSQL database."""
        print_header("Synchronizing Database Schema", "Prisma db push to Supabase PostgreSQL")
        print_info(f"Executing: npx prisma db push in {BACKEND_DIR}")

        try:
            cmd = ["npx", "prisma", "db", "push"]
            shell_needed = sys.platform == "win32"
            res = subprocess.run(cmd, cwd=BACKEND_DIR, shell=shell_needed)
            if res.returncode == 0:
                print_success("Database schema synchronized successfully with Supabase!")
                return True
            else:
                print_error(f"Prisma DB push failed with exit code {res.returncode}.")
                return False
        except Exception as e:
            print_error(f"Error executing prisma db push: {e}")
            return False

    @staticmethod
    def launch_studio():
        """Launches Prisma Studio Web UI on port 5555."""
        print_header("Launching Prisma Studio", "Database Visualizer on http://localhost:5555")
        print_info("Opening Prisma Studio in your web browser...")
        print_info("Press [Ctrl+C] to stop Prisma Studio.\n")

        try:
            cmd = ["npx", "prisma", "studio", "--port", "5555"]
            shell_needed = sys.platform == "win32"
            p = subprocess.Popen(cmd, cwd=BACKEND_DIR, shell=shell_needed)
            time_waited = 0
            webbrowser.open("http://localhost:5555")
            p.wait()
        except KeyboardInterrupt:
            print_warning("\nStopping Prisma Studio...")
            if 'p' in locals():
                p.terminate()
                p.wait()
            print_success("Prisma Studio stopped.")
        except Exception as e:
            print_error(f"Error launching Prisma Studio: {e}")

    @staticmethod
    def generate_client() -> bool:
        """Generates Prisma Client TypeScript bindings."""
        print_header("Generating Prisma Client", "npx prisma generate")
        try:
            cmd = ["npx", "prisma", "generate"]
            shell_needed = sys.platform == "win32"
            res = subprocess.run(cmd, cwd=BACKEND_DIR, shell=shell_needed)
            if res.returncode == 0:
                print_success("Prisma Client generated successfully!")
                return True
            return False
        except Exception as e:
            print_error(f"Failed to generate Prisma client: {e}")
            return False

def db_menu():
    """Interactive Database & Supabase Menu."""
    while True:
        print_header("Database & Supabase Management Menu")
        print_menu_item("1", "Synchronize Schema with Supabase", "Run prisma db push to apply migrations")
        print_menu_item("2", "Launch Prisma Studio Web UI", "Browse & edit Supabase tables on http://localhost:5555")
        print_menu_item("3", "Generate Prisma Client", "Regenerate TypeScript Prisma bindings")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            DatabaseManager.push_schema()
            pause()
        elif choice == "2":
            DatabaseManager.launch_studio()
            pause()
        elif choice == "3":
            DatabaseManager.generate_client()
            pause()
        elif choice == "0":
            break
