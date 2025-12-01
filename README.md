# 🍊 orange-test-watcher

A simple yet effective Python bot designed to monitor the availability of hard-to-get smartphones on the Orange.pl online store.

When the product becomes available (i.e., the "Add to Cart" button appears), the bot immediately sends a notification to your Discord channel via Webhook.

## 🚀 Features

* **Positive Logic:** It actively searches for the "Add to Cart" button rather than just checking if the "Out of Stock" label is missing. This minimizes false positives.
* **Headless Browser:** Uses Selenium and Chrome in headless mode to correctly render dynamic pages (JavaScript).
* **Anti-Bot Evasion:** Simulates a real user browser (User-Agent) to avoid being blocked by the store.
* **Cloud Ready (Serverless):** Configured to run for free on **GitHub Actions** (scheduled cron jobs).
* **Discord Alerts:** Sends professional-looking Embed cards with the direct link and timestamp.

## ⚙️ Configuration (GitHub Actions)

This is the easiest method – the bot runs "by itself" in the GitHub cloud; you don't need to keep your computer on.

1.  **Fork or Copy this repository.**
2.  Go to **Settings** -> **Secrets and variables** -> **Actions**.
3.  Add a new secrets (**New repository secret**):
    * Name: `PRODUCT_URL`
    * Value: `Your_Product_Link_Here`
    * Name: `DISCORD_WEBHOOK_URL`
    * Value: `Your_Discord_Webhook_Link_Here`
4.  Go to the **Actions** tab and ensure the workflow is enabled.
5.  The bot will check stock availability by default every **15 minutes** (defined in `.github/workflows/scraper.yml`).

## 💻 Local Usage (Run on your PC)

If you prefer to run the bot locally (e.g., to check more frequently):

1.  Clone the repository:
    ```bash
    git clone [https://github.com/m-wieloch/orange-test-watcher.git](https://github.com/m-wieloch/orange-test-watcher.git)
    cd orange-test-watcher
    ```
2.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set the environment variable with your Product (or hardcode it in the script for testing):
    * Windows (CMD): `set PRODUCT_URL=https://www.orange.pl/esklep/...`
    * Linux/Mac: `export PRODUCT_URL=https://www.orange.pl/esklep/...`
4.  Set the environment variable with your Discord Webhook (or hardcode it in the script for testing):
    * Windows (CMD): `set DISCORD_WEBHOOK_URL=https://discord...`
    * Linux/Mac: `export DISCORD_WEBHOOK_URL=https://discord...`
5.  Run the bot:
    ```bash
    python main.py
    ```