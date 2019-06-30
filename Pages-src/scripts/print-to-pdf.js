#!/usr/bin/env node

// https://stackoverflow.com/questions/44575628/alter-the-default-header-footer-when-printing-to-pdf/51431779#51431779
const CDP = require('chrome-remote-interface');
const fs = require('fs');

const port = process.argv[2];
const url = process.argv[3];
const pdfFilePath = process.argv[4];

(async function() {
        const protocol = await CDP({port: port});

        // Extract the DevTools protocol domains we need and enable them.
        // See API docs: https://chromedevtools.github.io/devtools-protocol/
        const {Page} = protocol;
        await Page.enable();

        Page.loadEventFired(function () {
                console.log("Waiting 25ms just to be sure.")
                setTimeout(function () {
                        // https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF
                        console.log("Printing...")
                        Page.printToPDF({
                                displayHeaderFooter: true,
                                headerTemplate: '<div></div>',
                                footerTemplate: '<div class="text center"><span class="pageNumber"></span></div>',
                                // footerTemplate: '<div class="text center"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
                        }).then((base64EncodedPdf) => {
                                fs.writeFileSync(pdfFilePath, Buffer.from(base64EncodedPdf.data, 'base64'), 'utf8');
                                console.log("Done")
                                protocol.close();
                        });
                }, 25);
        });

        Page.navigate({url: url});
})();