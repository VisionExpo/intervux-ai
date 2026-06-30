const fs = require('fs');
const path = require('path');

const dirs = [
    'frontend/tests/unit',
    'frontend/tests/integration',
    'frontend/tests/contracts',
    'frontend/tests/runtime',
    'frontend/tests/architecture',
    'playwright/journeys',
    'playwright/recovery',
    'playwright/regression',
    'playwright/observability'
];

dirs.forEach(d => {
    fs.mkdirSync(path.join('c:\\\\Vishal\\\\intervux-ai', d), { recursive: true });
    // create a simple README to preserve folder in git
    fs.writeFileSync(path.join('c:\\\\Vishal\\\\intervux-ai', d, '.gitkeep'), '');
});

console.log("Testing pyramid folders created.");
