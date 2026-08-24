"""
Hydroponics Platform — Terminal Banner & Styling Engine
Provides ANSI color formatting, ASCII art banners, and styled terminal helpers.
"""

import os
import sys

# Force UTF-8 stdout encoding on Windows if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ANSI Colors & Styles
class Colors:
    RESET       = "\033[0m"
    BOLD        = "\033[1m"
    DIM         = "\033[2m"
    UNDERLINE   = "\033[4m"

    # Foreground Colors
    BLACK       = "\033[30m"
    RED         = "\033[31m"
    GREEN       = "\033[32m"
    YELLOW      = "\033[33m"
    BLUE        = "\033[34m"
    MAGENTA     = "\033[35m"
    CYAN        = "\033[36m"
    WHITE       = "\033[37m"

    # Bright Foreground
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

# Enable ANSI colors on Windows terminal
if sys.platform == "win32":
    os.system("color")

def clear_screen():
    os.system("cls" if sys.platform == "win32" else "clear")

def print_header(title: str, subtitle: str = ""):
    border = "=" * 72
    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}+{border}+{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}|  {title.center(68)}  |{Colors.RESET}")
    if subtitle:
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}|  {Colors.DIM}{subtitle.center(68)}{Colors.RESET}{Colors.BRIGHT_GREEN}{Colors.BOLD}  |{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}+{border}+{Colors.RESET}\n")

def print_section(title: str):
    line = "-" * (68 - len(title))
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}--- {title} {line}{Colors.RESET}\n")

def print_menu_item(key: str, label: str, description: str = ""):
    key_formatted = f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}[{key}]{Colors.RESET}"
    label_formatted = f"{Colors.BRIGHT_WHITE}{label}{Colors.RESET}"
    if description:
        desc_formatted = f"{Colors.DIM}- {description}{Colors.RESET}"
        print(f"  {key_formatted:<14} {label_formatted:<32} {desc_formatted}")
    else:
        print(f"  {key_formatted:<14} {label_formatted}")

def print_success(msg: str):
    print(f"  {Colors.BRIGHT_GREEN}{Colors.BOLD}[OK]{Colors.RESET} {msg}")

def print_error(msg: str):
    print(f"  {Colors.BRIGHT_RED}{Colors.BOLD}[ERROR]{Colors.RESET} {msg}")

def print_warning(msg: str):
    print(f"  {Colors.BRIGHT_YELLOW}{Colors.BOLD}[WARN]{Colors.RESET} {msg}")

def print_info(msg: str):
    print(f"  {Colors.BRIGHT_CYAN}{Colors.BOLD}[INFO]{Colors.RESET} {msg}")

def prompt_choice(prompt_text: str = "Select an option", default: str = "") -> str:
    default_str = f" [{default}]" if default else ""
    try:
        val = input(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}>> {prompt_text}{default_str}:{Colors.RESET} ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print()
        return "0"

def pause():
    try:
        input(f"\n{Colors.DIM}Press [Enter] to continue...{Colors.RESET}")
    except (KeyboardInterrupt, EOFError):
        pass
