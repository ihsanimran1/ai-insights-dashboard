const puppeteer = require('puppeteer-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();

puppeteer.use(stealth);

(async () => {
    const originalUrl = process.argv[2];

    if (!originalUrl) {
        console.error("❌ No URL provided. Usage: node fetch_page_puppeteer.js <URL>");
        process.exit(1);
    }

    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ]
    });

    const page = await browser.newPage();

    try {
        console.log(`🌐 Fetching article with Puppeteer Stealth: ${originalUrl}`);
        await page.goto(originalUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });

        // Remove any paywall overlays
        await page.evaluate(() => {
            const paywall = document.querySelector('.paywall, .overlay, .modal, .subscribe-banner');
            if (paywall) paywall.remove();
        });

        // Extract article content
        const textContent = await page.evaluate(() => {
            const article = document.querySelector('article') || document.body;
            return article.innerText;
        });

        if (!textContent || textContent.trim().length < 50) {
            console.error("⚠️ Article content too short or missing.");
        } else {
            console.log(textContent);
        }

    } catch (error) {
        console.error("❌ Error fetching page:", error);
    } finally {
        await browser.close();
    }
})();
// Usage: node fetch_page_puppeteer.js <URL>
// Example: node fetch_page_puppeteer.js https://example.com/article
// This script uses Puppeteer with stealth mode to fetch the article content from a given URL.
// It handles paywalls and extracts the main article text, logging it to the console.
// If the content is too short or missing, it logs a warning message.
// Make sure to have Puppeteer and puppeteer-extra installed:
// npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth
    
