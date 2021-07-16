#!/usr/bin/env node

const puppeteer = require('puppeteer');
const axios = require('axios').default;

const port = process.argv[2];
const url = process.argv[3];
const pdfFilePath = process.argv[4];

(async () => {
    // Connect to it using puppeteer.connect().
    const resp = await axios.get(`http://localhost:${port}/json/version`);
    const { webSocketDebuggerUrl } = resp.data;
    const browser = await puppeteer.connect({ browserWSEndpoint: webSocketDebuggerUrl });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.evaluate(() => {
        Array.from(document.getElementsByTagName("a"))
            .filter((el) => { return el.href.startsWith(document.location["origin"]) })
            .filter((el) => { return !el.href.startsWith(document.location["href"]) })
            .forEach((el) => { el.href = el.href.replace(document.location["origin"], "https://tttapa.github.io") })
    });
    await page.pdf({
        path: pdfFilePath, preferCSSPageSize: true,
        displayHeaderFooter: true,
        // headerTemplate: '<div class="text center"><span class="title" style="border-bottom: 1px solid #ccc;"></span></div>',
        headerTemplate: '<div class="text center"></div>',
        footerTemplate: '<div class="text center"><span class="pageNumber"></span></div>'
    });
    browser.disconnect();
})().catch(e => { console.error(e); throw e });