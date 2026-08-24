"""
Hydroponics Platform — Sensor Calibration Wizard
Interactive step-by-step calibration utilities for Analog pH and TDS probes.
"""

import os
import re
import sys
import time
from typing import Optional

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_H_PATH = os.path.join(ROOT_DIR, "firmware", "esp32_chem", "src", "config", "config.h")

class CalibrationWizard:
    @staticmethod
    def run_ph_calibration_wizard():
        """Interactive 2-Point pH Sensor Calibration Wizard."""
        print_header("Analog pH Sensor Calibration Wizard", "Calculates Neutral Voltage & Nernst Slope")

        print(f"{Colors.BRIGHT_WHITE}This wizard will calculate the exact calibration constants for your analog pH sensor.{Colors.RESET}")
        print(f"You will need: {Colors.BOLD}1. pH 7.00 Buffer Solution{Colors.RESET} and {Colors.BOLD}2. pH 4.00 (or 9.18) Buffer Solution{Colors.RESET}.\n")

        # Step 1: Neutral Calibration
        print_section("Step 1: Neutral Calibration (pH 7.00)")
        print("1. Rinse probe thoroughly with distilled/RO water.")
        print("2. Submerge pH glass bulb in standard pH 7.00 buffer solution.")
        print("3. Swirl gently for 15 seconds and let the reading settle.")
        
        v_neutral_str = prompt_choice("Enter the measured ADC voltage in pH 7.00 (or press Enter for default)", default="1.65")
        try:
            v_neutral = float(v_neutral_str)
        except ValueError:
            v_neutral = 1.65
        print_success(f"Neutral Reference Voltage locked at: {v_neutral:.3f} V")

        # Step 2: Acid/Alkaline Point Calibration
        print_section("Step 2: Reference Buffer Calibration (pH 4.00 or 9.18)")
        buffer_type = prompt_choice("Select secondary buffer [1] pH 4.00 (Standard) or [2] pH 9.18", default="1")
        target_ph = 4.00 if buffer_type == "1" else 9.18

        print(f"\n1. Rinse probe thoroughly with distilled water again.")
        print(f"2. Submerge pH probe in pH {target_ph:.2f} buffer solution.")
        print("3. Swirl gently and wait for voltage reading to stabilize.")

        v_ref_str = prompt_choice(f"Enter the measured ADC voltage in pH {target_ph:.2f}", default="2.19" if target_ph == 4.00 else "1.25")
        try:
            v_ref = float(v_ref_str)
        except ValueError:
            v_ref = 2.19 if target_ph == 4.00 else 1.25

        # Calculate Slope
        delta_v = abs(v_neutral - v_ref)
        delta_ph = abs(7.00 - target_ph)
        slope = delta_v / delta_ph

        print_section("Calibration Results")
        print(f"  {Colors.BOLD}Neutral Voltage (V_neutral):{Colors.RESET} {Colors.BRIGHT_GREEN}{v_neutral:.3f} V{Colors.RESET}")
        print(f"  {Colors.BOLD}Electrode Sensitivity Slope:{Colors.RESET} {Colors.BRIGHT_GREEN}{slope:.3f} V/pH{Colors.RESET} ({slope*1000:.1f} mV/pH)")
        print(f"  {Colors.BOLD}Mathematical Formula:{Colors.RESET} pH = 7.00 + ({v_neutral:.3f} - V_adc) / {slope:.3f}")

        # Update config.h
        if os.path.exists(CONFIG_H_PATH):
            apply = prompt_choice("Write these calibration constants to firmware/esp32_chem config.h? [y/n]", default="y")
            if apply.lower().startswith("y"):
                CalibrationWizard._apply_ph_config(v_neutral, slope)

    @staticmethod
    def _apply_ph_config(v_neutral: float, slope: float):
        """Updates PH_CALIBRATION_NEUTRAL_V and PH_CALIBRATION_SLOPE in config.h."""
        try:
            with open(CONFIG_H_PATH, "r", encoding="utf-8") as f:
                content = f.read()

            content = re.sub(
                r"#define\s+PH_CALIBRATION_NEUTRAL_V\s+[\d\.]+f?",
                f"#define PH_CALIBRATION_NEUTRAL_V {v_neutral:.2f}f",
                content
            )
            content = re.sub(
                r"#define\s+PH_CALIBRATION_SLOPE\s+[\d\.]+f?",
                f"#define PH_CALIBRATION_SLOPE    {slope:.2f}f",
                content
            )

            with open(CONFIG_H_PATH, "w", encoding="utf-8") as f:
                f.write(content)

            print_success(f"Updated {CONFIG_H_PATH} successfully!")
        except Exception as e:
            print_error(f"Failed to update config.h: {e}")

    @staticmethod
    def run_tds_calibration_wizard():
        """Interactive TDS Probe Calibration Wizard."""
        print_header("Analog TDS Sensor Calibration", "Nutrient Solution ppm Calibration")
        print("1. Submerge probe in standard 1413 µS/cm (707 ppm) calibration solution.")
        print("2. Verify temperature of solution is ~25°C.")
        print("3. Check reading on TFT Display #2.")
        pause()

def calibration_menu():
    """Interactive Calibration Menu."""
    while True:
        print_header("Sensor Calibration Wizards")
        print_menu_item("1", "Analog pH 2-Point Calibration Wizard", "Step-by-step pH 7.0 and pH 4.0 buffer calibration")
        print_menu_item("2", "Analog TDS Nutrient Calibration", "Calibration guidelines for standard 1413 µS/cm solution")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            CalibrationWizard.run_ph_calibration_wizard()
            pause()
        elif choice == "2":
            CalibrationWizard.run_tds_calibration_wizard()
            pause()
        elif choice == "0":
            break
