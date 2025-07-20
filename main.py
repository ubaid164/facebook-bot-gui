# main.py
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import json
from uuid import uuid4
import threading

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

BASE_PROFILE_PATH = os.path.join(os.getcwd(), "profiles")
PROFILE_REGISTRY_FILE = os.path.join(BASE_PROFILE_PATH, "profiles.json")

# Dummy data for now
dummy_titles = ["Brand New Headphones", "Gaming Mouse", "LED Desk Lamp", "Wireless Keyboard", "Stylish Backpack"]
dummy_descriptions = ["Works perfectly. Brand new.", "Used only once.", "In great condition!", "Best price online.", "Quick sale!"]
dummy_prices = [20, 30, 15, 50, 10]
dummy_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]


def set_marketplace_location(driver):
    try:
        driver.get("https://www.facebook.com/marketplace")
        time.sleep(5)
        # Simulated location change: in real case, you'd click and type location field
        print("[INFO] Set Marketplace location to USA")
        # Add actual interaction with FB's location element here if needed
    except Exception as e:
        print("[ERROR setting location]:", e)


def create_listing(driver, city):
    try:
        driver.get("https://www.facebook.com/marketplace/create/item")
        time.sleep(5)

        title = random.choice(dummy_titles)
        description = random.choice(dummy_descriptions)
        price = str(random.choice(dummy_prices))

        # Enter Title
        title_input = driver.find_element(By.XPATH, '//input[@aria-label="Title"]')
        title_input.send_keys(title)

        # Enter Price
        price_input = driver.find_element(By.XPATH, '//input[@aria-label="Price"]')
        price_input.send_keys(price)

        # Enter Description
        desc_input = driver.find_element(By.XPATH, '//textarea[@aria-label="Description"]')
        desc_input.send_keys(description)

        # Here you would locate and update the location field using `city`
        # (depends on Facebook's HTML structure)

        # Click Next or Save to Draft (simulate using TABs and Enter)
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB * 10 + Keys.ENTER)
        time.sleep(3)

    except Exception as e:
        print("[ERROR creating listing]:", e)


def automate_listings(profile_path):
    options = uc.ChromeOptions()
    options.user_data_dir = profile_path
    driver = uc.Chrome(options=options)

    set_marketplace_location(driver)

    # Open 15 Tabs
    listing_urls = ["https://www.facebook.com/marketplace/create/item"] * 15
    for url in listing_urls:
        driver.execute_script(f"window.open('{url}');")
        time.sleep(1)

    time.sleep(5)

    # Switch to each tab, fill ad, save draft
    cities_cycle = dummy_cities * 3
    for i, handle in enumerate(driver.window_handles[1:]):
        driver.switch_to.window(handle)
        create_listing(driver, cities_cycle[i])
        driver.close()

    driver.switch_to.window(driver.window_handles[0])

    # Go to drafts and simulate publishing
    try:
        driver.get("https://www.facebook.com/marketplace/you/listings")
        time.sleep(5)
        print("[INFO] Opened listings page to simulate location update and publishing.")
        # Here you would automate clicking drafts, updating city, and publishing
    except Exception as e:
        print("[ERROR opening listings page]:", e)


def load_profiles():
    if not os.path.exists(PROFILE_REGISTRY_FILE):
        return {}
    with open(PROFILE_REGISTRY_FILE, "r") as f:
        return json.load(f)


def save_profiles(profiles):
    with open(PROFILE_REGISTRY_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def create_new_profile():
    profiles = load_profiles()
    new_id = str(uuid4())[:8]
    profile_path = os.path.join(BASE_PROFILE_PATH, new_id)
    os.makedirs(profile_path, exist_ok=True)
    profiles[new_id] = {"path": profile_path, "name": f"FB_Profile_{new_id}"}
    save_profiles(profiles)
    launch_chrome_with_profile(profile_path)


def delete_profile(profile_id):
    profiles = load_profiles()
    profile_path = profiles[profile_id]["path"]
    try:
        if os.path.exists(profile_path):
            for root, dirs, files in os.walk(profile_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(profile_path)
        del profiles[profile_id]
        save_profiles(profiles)
        messagebox.showinfo("Success", "Profile deleted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete profile: {str(e)}")


def launch_chrome_with_profile(profile_path):
    options = uc.ChromeOptions()
    options.user_data_dir = profile_path
    driver = uc.Chrome(options=options)
    driver.get("https://www.facebook.com/")
    return driver


def reopen_saved_profile(profile_id):
    profiles = load_profiles()
    profile_path = profiles[profile_id]["path"]
    threading.Thread(target=automate_listings, args=(profile_path,)).start()


def build_gui():
    root = tk.Tk()
    root.title("Facebook Chrome Profile Launcher")
    root.geometry("600x600")

    title = tk.Label(root, text="Facebook Bot Profile Manager", font=("Arial", 16))
    title.pack(pady=10)

    add_btn = tk.Button(root, text="+ Add Facebook ID (Manual Login)", command=create_new_profile, bg="#007BFF", fg="white", height=2)
    add_btn.pack(pady=10)

    saved_label = tk.Label(root, text="Saved Chrome Profiles:", font=("Arial", 12))
    saved_label.pack(pady=10)

    profiles_frame = tk.Frame(root)
    profiles_frame.pack()

    def refresh_profiles():
        for widget in profiles_frame.winfo_children():
            widget.destroy()

        profiles = load_profiles()
        for profile_id, info in profiles.items():
            frame = tk.Frame(profiles_frame)
            frame.pack(pady=5, fill="x")

            btn = tk.Button(
                frame,
                text=f"{info['name']} → Create 15 Listings",
                command=lambda pid=profile_id: reopen_saved_profile(pid),
                width=40,
                bg="#28a745",
                fg="white"
            )
            btn.pack(side="left", padx=5)

            del_btn = tk.Button(
                frame,
                text="🗑 Delete",
                command=lambda pid=profile_id: delete_profile(pid),
                bg="#dc3545",
                fg="white"
            )
            del_btn.pack(side="left", padx=5)

    refresh_btn = tk.Button(root, text="🔄 Refresh Profile List", command=refresh_profiles)
    refresh_btn.pack(pady=10)

    refresh_profiles()
    root.mainloop()


if __name__ == "__main__":
    build_gui()
