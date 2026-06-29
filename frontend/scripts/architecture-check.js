import fs from 'fs';
import path from 'path';

function walkDir(dir, callback) {
  if (!fs.existsSync(dir)) return;
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? walkDir(dirPath, callback) : callback(dirPath);
  });
}

let violations = 0;

// Test: Runtime modules shouldn't import React
walkDir(path.resolve('./src/core/runtime/modules'), (filepath) => {
    const content = fs.readFileSync(filepath, 'utf8');
    if (content.includes("from 'react'") || content.includes('from "react"')) {
        console.error(`Violation: Runtime module imports React: ${filepath}`);
        violations++;
    }
});

// Test: Dashboard shouldn't import Runtime Kernel or internals
walkDir(path.resolve('./src/dashboard'), (filepath) => {
    const content = fs.readFileSync(filepath, 'utf8');
    if (content.includes("/runtime/kernel") || content.includes("/runtime/modules")) {
        console.error(`Violation: Dashboard imports runtime internals: ${filepath}`);
        violations++;
    }
});

// Test: Managers (modules) shouldn't import other managers
walkDir(path.resolve('./src/core/runtime/modules'), (filepath) => {
    const content = fs.readFileSync(filepath, 'utf8');
    const moduleName = path.basename(filepath, '.ts');
    
    // Quick naive check
    if (moduleName !== 'RuntimeModule') {
        const otherModules = ['StateModule', 'SessionModule', 'EventRecorder'].filter(m => m !== moduleName);
        for (const other of otherModules) {
            if (content.includes(other)) {
                console.error(`Violation: Module ${moduleName} imports another module (${other})`);
                violations++;
            }
        }
    }
});

if (violations > 0) {
    console.error(`Architecture check failed with ${violations} violations.`);
    process.exit(1);
} else {
    console.log("Architecture check passed.");
}
