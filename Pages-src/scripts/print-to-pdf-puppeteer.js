#!/usr/bin/env node

const puppeteer = require('puppeteer');

const dev_ws = process.argv[2];
const url = process.argv[3];
const pdfFilePath = process.argv[4];

(async () => {
    const browser = await puppeteer.connect({ 'browserWSEndpoint': dev_ws });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.pdf({
        path: pdfFilePath, preferCSSPageSize: true,
        displayHeaderFooter: true,
        // headerTemplate: '<div class="text center"><span class="title" style="border-bottom: 1px solid #ccc;"></span></div>',
        headerTemplate: '<div class="text center"></div>',
        footerTemplate: '<div class="text center"><span class="pageNumber"></span></div>'
    });
    browser.disconnect();
})().catch(e => { console.error(e); throw e });