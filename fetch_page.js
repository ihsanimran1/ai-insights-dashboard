// const puppeteer = require('puppeteer');
// const puppeteerExtra = require('puppeteer-extra');
// const stealth = require('puppeteer-extra-plugin-stealth')();

// puppeteerExtra.use(stealth);

// (async () => {
//     const originalUrl = process.argv[2];

//     if (!originalUrl) {
//         console.error("❌ No URL provided. Usage: node fetch_page.js <URL>");
//         process.exit(1);
//     }

//     const hardPaywallSites = [
//         "bloomberg.com",
//         "wsj.com",
//         "ft.com",
//         "nytimes.com"
//     ];

//     let textContent = "";

//     // Decide whether to use archive.ph
//     const needsArchive = hardPaywallSites.some(domain => originalUrl.includes(domain));

//     if (needsArchive) {
//         // 🌐 Use regular Puppeteer for archive.ph
//         const archiveUrl = `https://archive.ph/?run=1&url=${encodeURIComponent(originalUrl)}`;
//         console.log(`🌐 Forcing archive.ph snapshot: ${archiveUrl}`);

//         const browser = await puppeteer.launch({
//             headless: true,
//             args: [
//                 '--no-sandbox',
//                 '--disable-setuid-sandbox'
//             ]
//         });
//         const page = await browser.newPage();

//         try {
//             await page.goto(archiveUrl, { waitUntil: 'domcontentloaded', timeout: 180000 });

//             const possibleSelectors = [
//                 '#maincontent', '.ARTICLE', '.article-body', 'article', 'body'
//             ];

//             let foundContent = false;
//             for (let selector of possibleSelectors) {
//                 try {
//                     await page.waitForSelector(selector, { timeout: 10000 });
//                     textContent = await page.$eval(selector, el => el.innerText);
//                     foundContent = true;
//                     break;
//                 } catch (err) {
//                     console.log(`⚠️ Selector not found: ${selector}`);
//                 }
//             }

//             if (!foundContent) {
//                 throw new Error("❌ Could not find article content on archive.ph.");
//             }

//             console.log(textContent);
//         } catch (archiveError) {
//             console.error("❌ Archive.ph failed:", archiveError);
//         } finally {
//             await browser.close();
//         }
//     } else {
//         // 🥷 Use Puppeteer Stealth for all other sites
//         console.log(`🌐 Using Puppeteer Stealth for: ${originalUrl}`);

//         const browser = await puppeteerExtra.launch({
//             headless: true,
//             args: [
//                 '--no-sandbox',
//                 '--disable-setuid-sandbox'
//             ]
//         });
//         const page = await browser.newPage();

//         try {
//             await page.goto(originalUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });

//             // Remove any paywall overlays
//             await page.evaluate(() => {
//                 const paywall = document.querySelector('.paywall, .overlay, .modal');
//                 if (paywall) paywall.remove();
//             });

//             textContent = await page.evaluate(() => {
//                 const article = document.querySelector('article') || document.body;
//                 return article.innerText;
//             });

//             console.log(textContent);
//         } catch (error) {
//             console.error("❌ Error fetching page:", error);
//         } finally {
//             await browser.close();
//         }
//     }
// })();




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






// const puppeteer = require('puppeteer-extra');
// const stealth = require('puppeteer-extra-plugin-stealth')();

// puppeteer.use(stealth);

// (async () => {
//     const url = process.argv[2];

//     if (!url) {
//         console.error("❌ No URL provided. Usage: node fetch_page.js <URL>");
//         process.exit(1);
//     }

//     const browser = await puppeteer.launch({
//         executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', // Use real Chrome
//         headless: true,
//         args: [
//             '--no-sandbox',
//             '--disable-setuid-sandbox',
//             '--disable-http2', // ✅ Force HTTP/1.1
//             '--disable-blink-features=AutomationControlled'
//         ]
//     });

//     const page = await browser.newPage();

//     // Set headers to mimic a real browser
//     await page.setExtraHTTPHeaders({
//         'Accept-Language': 'en-US,en;q=0.9',
//         'Upgrade-Insecure-Requests': '1'
//     });

//     try {
//         console.log(`🌐 Navigating to: ${url}`);
//         await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

//         // Remove paywall overlays
//         await page.evaluate(() => {
//             const paywall = document.querySelector('.paywall, .modal, .overlay');
//             if (paywall) paywall.remove();
//         });

//         // Extract text
//         const textContent = await page.evaluate(() => {
//             const article = document.querySelector('article');
//             return article ? article.innerText : document.body.innerText;
//         });

//         console.log(textContent);
//     } catch (error) {
//         console.error('❌ Error fetching page:', error);
//     } finally {
//         await browser.close();
//     }
// })();






// const puppeteer = require('puppeteer-extra');
// const stealth = require('puppeteer-extra-plugin-stealth')();

// puppeteer.use(stealth);

// (async () => {
//     const url = process.argv[2];

//     if (!url) {
//         console.error("❌ No URL provided. Usage: node fetch_page.js <URL>");
//         process.exit(1);
//     }

//     const browser = await puppeteer.launch({
//         headless: true,
//         args: [
//             '--no-sandbox',
//             '--disable-setuid-sandbox'
//         ]
//     });

//     const page = await browser.newPage();

//     try {
//         console.log(`🌐 Navigating to: ${url}`);
//         await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

//         // Scroll slowly to load dynamic content
//         for (let i = 0; i < 10; i++) {
//             await page.evaluate(() => window.scrollBy(0, 500));
//             await new Promise(r => setTimeout(r, 300 + Math.random() * 300));
//         }

//         // Extract visible article text
//         const textContent = await page.evaluate(() => {
//             const article = document.querySelector('article');
//             return article ? article.innerText : document.body.innerText;
//         });

//         console.log(textContent);
//     } catch (error) {
//         console.error('❌ Error fetching page:', error);
//     } finally {
//         await browser.close();
//     }
// })();


// const playwright = require('playwright');

// (async () => {
//     const url = process.argv[2];
//     if (!url) {
//         console.error("❌ No URL provided.");
//         process.exit(1);
//     }

//     const browser = await playwright.chromium.launch({
//         headless: true,
//         args: [
//             '--no-sandbox',
//             '--disable-setuid-sandbox',
//             '--disable-blink-features=AutomationControlled'
//         ]
//     });

//     const context = await browser.newContext({
//         userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
//         viewport: { width: 1280, height: 800 },
//         javaScriptEnabled: true
//     });

//     const page = await context.newPage();

//     try {
//         console.log(`🌐 Navigating to: ${url}`);
//         await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });

//         // Wait for body or article
//         await page.waitForSelector('body', { timeout: 10000 });

//         // Scroll slowly to trigger lazy loading
//         for (let i = 0; i < 5; i++) {
//             await page.evaluate(() => window.scrollBy(0, window.innerHeight));
//             await page.waitForTimeout(1000);
//         }

//         // Extract article text
//         const textContent = await page.evaluate(() => {
//             const article = document.querySelector('article');
//             return article ? article.innerText : document.body.innerText;
//         });

//         console.log(textContent);
//     } catch (error) {
//         console.error('❌ Error fetching page:', error);
//     } finally {
//         await browser.close();
//     }
// })();
