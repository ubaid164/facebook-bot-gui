import os
import tkinter as tk
from tkinter import messagebox
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

dummy_titles = ["Brand New Headphones", "Gaming Mouse", "LED Desk Lamp", "Wireless Keyboard", "Stylish Backpack"]
dummy_descriptions = ["Works perfectly. Brand new.", "Used only once.", "In great condition!", "Best price online.", "Quick sale!"]
dummy_prices = [20, 30, 15, 50, 10]
dummy_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]


def set_marketplace_location(driver):
    try:
        print("[INFO] Setting location...")
        driver.get("https://web.facebook.com/marketplace/106109396086591")
        time.sleep(5)

        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.5)

        location_input = driver.find_element(By.CLASS_NAME, "xod5an3")
        location_input.click()
        location_input.send_keys(Keys.CONTROL + "a")
        location_input.send_keys(Keys.DELETE)
        time.sleep(1)
        location_input.send_keys("USA")
        time.sleep(2)
        location_input.send_keys(Keys.RETURN)
        print("[INFO] Location set to USA")
    except Exception as e:
        print("[ERROR setting location]:", e)


def create_listing(driver, city):
    try:
        title = random.choice(dummy_titles)
        description = random.choice(dummy_descriptions)
        price = str(random.choice(dummy_prices))

        title_input = driver.find_element(By.XPATH, '//input[@aria-label="Title"]')
        title_input.send_keys(title)

        price_input = driver.find_element(By.XPATH, '//input[@aria-label="Price"]')
        price_input.send_keys(price)

        desc_input = driver.find_element(By.XPATH, '//textarea[@aria-label="Description"]')
        desc_input.send_keys(description)

        time.sleep(1)
    except Exception as e:
        print("[ERROR creating listing]:", e)


def automate_listings(profile_path):
    options = uc.ChromeOptions()
    options.user_data_dir = profile_path
    driver = uc.Chrome(options=options)

    try:
        print("[INFO] Logging into Facebook and opening Marketplace...")
        driver.get("https://web.facebook.com/marketplace/")
        time.sleep(6)

        # Optional: Set location
        set_marketplace_location(driver)

        print("[INFO] Opening 15 tabs for new listings...")
        listing_url = "https://web.facebook.com/marketplace/create/item"
        for _ in range(15):
            driver.execute_script(f"window.open('{listing_url}');")
            time.sleep(0.2)

        # Wait a little for tabs to initialize
        time.sleep(5)

        # Prepare city loop for testing
        cities_cycle = (dummy_cities * 3)[:15]

        print("[INFO] Starting to create listings on each tab...")
        for i, handle in enumerate(driver.window_handles[1:]):  # Skip first tab (main tab)
            driver.switch_to.window(handle)
            time.sleep(5)

            try:
                title = random.choice(dummy_titles)
                description = random.choice(dummy_descriptions)
                price = str(random.choice(dummy_prices))

                # Fill title
                title_input = driver.find_element(By.XPATH, '//input[@aria-label="Title"]')
                title_input.clear()
                title_input.send_keys(title)

                # Fill price
                price_input = driver.find_element(By.XPATH, '//input[@aria-label="Price"]')
                price_input.clear()
                price_input.send_keys(price)

                # Fill description
                desc_input = driver.find_element(By.XPATH, '//textarea[@aria-label="Description"]')
                desc_input.clear()
                desc_input.send_keys(description)

                # Tags or category — optional if needed
                # You can try to locate the category dropdown and select a category if required

                print(f"[{i+1}/15] Listing filled: {title}")

                # Simulate "Save as Draft"
                # Usually Facebook saves draft automatically after filling or you can click a button if visible
                time.sleep(3)

            except Exception as e:
                print(f"[ERROR on tab {i+1}]:", e)

            # Close the filled tab
            driver.close()

        # Switch back to the main tab
        driver.switch_to.window(driver.window_handles[0])
        driver.get("https://web.facebook.com/marketplace/you/listings")
        print("[INFO] All drafts created. Listings page opened.")
        time.sleep(5)

    except Exception as e:
        print("[ERROR in automate_listings]:", e)
        print("[INFO] Now opening selling page to finalize drafts...")
        driver.get("https://web.facebook.com/marketplace/you/selling")
        time.sleep(6)

        print("[INFO] Extracting draft listing links...")
        draft_links = []

        # Scroll a few times to load drafts
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(1)

        # Find listing links
        elems = driver.find_elements(By.XPATH, "//a[contains(@href, '/marketplace/item/')]")
        for elem in elems:
            href = elem.get_attribute("href")
            if href and href not in draft_links:
                draft_links.append(href)

        print(f"[INFO] Found {len(draft_links)} draft listings. Opening them now...")

        for url in draft_links[:15]:  # Limit to 15 if needed
            driver.execute_script(f"window.open('{url}');")
            time.sleep(0.2)

        time.sleep(5)

        # Finalize listings in each tab
        for i, handle in enumerate(driver.window_handles[1:]):
            driver.switch_to.window(handle)
            try:
                time.sleep(6)
                print(f"[INFO] Updating listing {i+1}...")

                # Scroll to location section
                driver.execute_script("window.scrollBy(0, 1500);")
                time.sleep(2)

                # Try finding location input
                location_input = driver.find_element(By.XPATH, "//input[@aria-label='Location']")
                location_input.send_keys(Keys.CONTROL + "a")
                location_input.send_keys(Keys.DELETE)
                time.sleep(1)
                location_input.send_keys("USA")
                time.sleep(2)
                location_input.send_keys(Keys.RETURN)
                print("[INFO] Location updated.")

                # Click Publish button (may vary by version)
                publish_btn = driver.find_element(By.XPATH, "//div[@aria-label='Publish']")
                publish_btn.click()
                print("[INFO] Listing published.")

                time.sleep(5)
            except Exception as e:
                print(f"[ERROR on finalizing tab {i+1}]:", e)

            driver.close()

        # Return to main tab
        driver.switch_to.window(driver.window_handles[0])
        print("[✅] All listings finalized and published.")


def load_profiles():
    if not os.path.exists(PROFILE_REGISTRY_FILE):
        return {}
    with open(PROFILE_REGISTRY_FILE, "r") as f:
        return json.load(f)


def save_profiles(profiles):
    os.makedirs(BASE_PROFILE_PATH, exist_ok=True)
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

    # Run in a thread to avoid freezing UI
    threading.Thread(target=automate_listings, args=(profile_path,)).start()


def build_gui():
    root = tk.Tk()
    root.title("Facebook Marketplace Bot")
    root.geometry("600x600")

    title = tk.Label(root, text="FB Marketplace Profile Manager", font=("Arial", 16))
    title.pack(pady=10)

    add_btn = tk.Button(root, text="+ Add New FB Profile", command=create_new_profile, bg="#007BFF", fg="white", height=2)
    add_btn.pack(pady=10)

    saved_label = tk.Label(root, text="Saved Profiles:", font=("Arial", 12))
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
                text=f"{info['name']} → Post 15 Listings",
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

    refresh_btn = tk.Button(root, text="🔄 Refresh Profiles", command=refresh_profiles)
    refresh_btn.pack(pady=10)

    refresh_profiles()
    root.mainloop()


if __name__ == "__main__":
    build_gui()
