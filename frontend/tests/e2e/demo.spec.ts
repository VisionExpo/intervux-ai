import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Golden Demo Determinism', () => {
  
  test('Runs the software_engineer scenario identically every time', async ({ page }) => {
    // 1. Navigate to the application
    await page.goto('/');

    // 2. Wait for the landing page to load
    await expect(page.getByText('Intervux AI')).toBeVisible();

    // 3. Initiate the Demo
    // (Assuming a simple demo start button for now, or direct routing)
    const demoButton = page.getByRole('button', { name: /start demo/i });
    if (await demoButton.isVisible()) {
        await demoButton.click();
    }

    // 4. Wait for the engine to complete the full scenario 
    // We target a specific unique element rendered by CompletionWorkspace
    const completionMarker = page.getByText('Interview Complete');
    await expect(completionMarker).toBeVisible({ timeout: 60000 }); // Wait up to 60s for full demo execution

    // 5. Ensure the completion workspace is fully rendered (animations settled)
    await page.waitForTimeout(1000); 

    // 6. Visual Regression: Assert the snapshot matches the Golden Master
    // This confirms the UI projection parity.
    await expect(page).toHaveScreenshot('golden-demo-completion.png', {
      maxDiffPixels: 100 // Allow tiny subpixel rendering diffs across CI envs
    });

    // 7. Extract the exported replay JSON from window object (assuming exporter attaches it for tests)
    const exportedReplay = await page.evaluate(() => {
        // Mock retrieval - in a real implementation the Exporter would attach this to window.__REPLAY_EXPORT__
        return (window as any).__REPLAY_EXPORT__ || null;
    });

    // We can also assert backend state determinism if needed:
    // expect(exportedReplay.timeline.length).toBeGreaterThan(0);
  });
});
