import { test, expect } from '@playwright/test';

test.describe('CycloneSense Scientific Web Application E2E', () => {

  test('1. Overview Dashboard loads with scientific metadata and active navigation', async ({ page }) => {
    await page.goto('/');

    // Verify Title and Meta
    await expect(page).toHaveTitle(/CycloneSense/);

    // Verify App Shell Navigation
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    await expect(page.getByRole('link', { name: /Overview Dashboard/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Impact Intelligence/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Model Benchmarks/i })).toBeVisible();
  });

  test('2. Navigation to Model Benchmarks displays operational baselines & quarantine', async ({ page }) => {
    await page.goto('/models');

    // Page title and headers
    await expect(page.getByRole('heading', { name: /Model Registry|Benchmarks/i })).toBeVisible();

    // Verify presence of Operational Baselines section (Persistence, Climatology, CLIPER)
    const pageText = await page.textContent('body');
    expect(pageText).toMatch(/Baseline|Persistence|Climatology|CLIPER/i);
  });

  test('3. Impact Intelligence Studio renders optical and SAR sensor controls', async ({ page }) => {
    await page.goto('/impact');

    // Impact Studio Header
    await expect(page.getByRole('heading', { name: /Impact Intelligence/i })).toBeVisible();

    // Verify sensor modality controls or biophysical indicators
    const content = await page.textContent('body');
    expect(content).toMatch(/Optical|SAR|Sentinel|NDVI|NDWI/i);
  });

  test('4. Explainability & Grad-CAM Lab renders attribution controls', async ({ page }) => {
    await page.goto('/explainability');

    // Check header
    await expect(page.getByRole('heading', { name: /Explainability|Grad-CAM/i })).toBeVisible();

    // Check Eyewall energy or Grad-CAM descriptions
    const content = await page.textContent('body');
    expect(content).toMatch(/Grad-CAM|Eyewall|Attribution|Sensitivity/i);
  });

  test('5. Satellite Data Viewer renders CF metadata inspector layout', async ({ page }) => {
    await page.goto('/data-viewer');

    await expect(page.getByRole('heading', { name: /Scientific Earth Observation|Satellite Viewer/i })).toBeVisible();
    const content = await page.textContent('body');
    expect(content).toMatch(/NetCDF|Granule|Band|Coordinate/i);
  });

  test('6. Cyclone Explorer loads storm track and trajectory interface', async ({ page }) => {
    await page.goto('/explorer');

    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    const content = await page.textContent('body');
    expect(content).toMatch(/IBTrACS|Storm|Track|North Indian Ocean/i);
  });

  test('7. Provenance Audit renders cryptographic lineage layout', async ({ page }) => {
    await page.goto('/provenance');

    await expect(page.getByRole('heading', { level: 1, name: /Cryptographic Provenance/i })).toBeVisible();
    const content = await page.textContent('body');
    expect(content).toMatch(/W3C PROV|SHA-256|Cryptographic|Lineage/i);
  });

  test('8. Dark Mode theme and accessibility classes are enforced', async ({ page }) => {
    await page.goto('/');

    const html = page.locator('html');
    await expect(html).toHaveClass(/dark/);

    const body = page.locator('body');
    await expect(body).toHaveClass(/bg-\[#070b12\]/);
  });

});
