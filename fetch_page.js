const puppeteer = require('puppeteer-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();

puppeteer.use(stealth);

(async () => {
    const originalUrl = process.argv[2];

    if (!originalUrl) {
        console.error("❌ No URL provided. Usage: node fetch_page.js <URL>");
        process.exit(1);
    }

    let archiveUrl = `https://archive.ph/?run=1&url=${encodeURIComponent(originalUrl)}`;

    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ]
    });

    const page = await browser.newPage();

    try {
        console.log(`🌐 Forcing archive.ph to snapshot: ${archiveUrl}`);
        await page.goto(archiveUrl, { waitUntil: 'domcontentloaded', timeout: 180000 }); // Allow 3 min for archiving

        // Wait for any possible article container
        const possibleSelectors = [
            '#maincontent',          // Normal
            '.ARTICLE',              // Some layouts
            '.article-body',         // Others
            'article',               // Default fallback
            'body'                   // Absolute fallback
        ];

        let foundContent = false;
        let textContent = "";

        for (let selector of possibleSelectors) {
            try {
                await page.waitForSelector(selector, { timeout: 10000 });
                textContent = await page.$eval(selector, el => el.innerText);
                foundContent = true;
                break;
            } catch (err) {
                console.log(`⚠️ Selector not found: ${selector}`);
            }
        }

        if (!foundContent) {
            throw new Error("❌ Could not find article content on archive.ph.");
        }

        console.log(textContent);
    } catch (archiveError) {
        console.error("❌ Archive.ph failed:", archiveError);
    } finally {
        await browser.close();
    }
})();
// This script uses Puppeteer to force archive.ph to snapshot a given URL and extract the article content.
// It handles various selectors to find the main article content and logs it to the console.
// If the content is not found, it will log an error message.