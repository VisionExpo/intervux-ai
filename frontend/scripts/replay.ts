import fs from 'fs';
import path from 'path';
import { RuntimeKernel } from '../src/core/runtime/kernel/RuntimeKernel';
import { ReplayVerifierCore } from '../src/core/runtime/replay/ReplayVerifierCore';
import { DemoSessionReplay } from '../src/core/runtime/replay/ReplayTypes';

// Provide a global crypto polyfill for Node.js if needed (for Web Crypto API)
if (typeof crypto === 'undefined') {
    global.crypto = require('crypto').webcrypto;
}

async function runReplay(filePath: string) {
    console.log(`[Replay CI] Loading replay file: ${filePath}`);
    const rawData = fs.readFileSync(path.resolve(process.cwd(), filePath), 'utf-8');
    const session: DemoSessionReplay = JSON.parse(rawData);

    console.log(`[Replay CI] Initializing headless RuntimeKernel...`);
    const kernel = new RuntimeKernel({});
    await kernel.start();

    const verifier = new ReplayVerifierCore(kernel, session);

    console.log(`[Replay CI] Running deterministic verification for scenario: ${session.scenario}`);
    
    try {
        await verifier.verify();
        console.log(`\n✅ [PASS] Replay Verification successful. Timeline perfectly determinisic.`);
        process.exit(0);
    } catch (error: any) {
        console.error(`\n❌ [FAIL] Replay Verification failed!`);
        if (error.name === 'ReplayMismatchError') {
            console.error(error.message);
        } else {
            console.error(error);
        }
        process.exit(1);
    }
}

const replayFile = process.argv[2];
if (!replayFile) {
    console.error("Usage: ts-node scripts/replay.ts <path-to-replay-json>");
    process.exit(1);
}

runReplay(replayFile);
