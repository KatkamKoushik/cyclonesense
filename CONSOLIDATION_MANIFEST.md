# Consolidation Manifest: `cyclonesense` & `cyclone-sense`

**Canonical Repository**: `https://github.com/KatkamKoushik/cyclonesense` (`origin`)  
**Source Repository**: `https://github.com/KatkamKoushik/cyclone-sense` (`cyclone-sense`)  
**Source Commit SHAs Audited**:
- `eff82bb3c8e026213988f0423ec3cc9ee901482f`: *"feat(sankalp): add impact intelligence prototype, verified ML metrics, and truth-in-advertising labels"*
- `fb155aaf49b04993bd6dda5214dd8ea111f80412`: *"feat(deploy): configure Vercel multi-service project and add root/dashboard requirements for Streamlit Cloud"*  
**Base Ancestor Commit**: `7ebf8d018eb78d6e27d33c763a4ae30e12e97f7d`  
**Consolidation Type**: Fast-Forward Direct Linear Heritage Merge  
**Generated Date**: 2026-10-12  

---

## File-Level Consolidation Manifest

| # | Source Path | Destination Path | Source SHA | Classification | Size | Verification Method | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `backend/app/adapters/sentinel.py` | `backend/app/adapters/sentinel.py` | `eff82bb` | `UNIQUE_SOURCE` | 9.8 KB (276 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 2 | `backend/app/api/routes_impact.py` | `backend/app/api/routes_impact.py` | `eff82bb` | `UNIQUE_SOURCE` | 17.6 KB (516 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 3 | `backend/app/ml/vlm_provider.py` | `backend/app/ml/vlm_provider.py` | `eff82bb` | `UNIQUE_SOURCE` | 10.4 KB (293 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 4 | `backend/app/scientific/before_after_matcher.py` | `backend/app/scientific/before_after_matcher.py` | `eff82bb` | `UNIQUE_SOURCE` | 8.3 KB (219 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 5 | `backend/app/scientific/change_detector.py` | `backend/app/scientific/change_detector.py` | `eff82bb` | `UNIQUE_SOURCE` | 12.1 KB (306 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 6 | `backend/app/scientific/georeferencing.py` | `backend/app/scientific/georeferencing.py` | `eff82bb` | `UNIQUE_SOURCE` | 18.2 KB (492 lines) | `pytest backend/tests/test_geospatial_pairing.py` | Migrated |
| 7 | `backend/app/scientific/impact_fusion.py` | `backend/app/scientific/impact_fusion.py` | `eff82bb` | `UNIQUE_SOURCE` | 5.2 KB (135 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 8 | `backend/app/scientific/impact_query_engine.py` | `backend/app/scientific/impact_query_engine.py` | `eff82bb` | `UNIQUE_SOURCE` | 2.4 KB (57 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 9 | `backend/app/scientific/optical_processor.py` | `backend/app/scientific/optical_processor.py` | `eff82bb` | `UNIQUE_SOURCE` | 7.6 KB (190 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 10 | `backend/app/scientific/pairing.py` | `backend/app/scientific/pairing.py` | `eff82bb` | `UNIQUE_SOURCE` | 8.1 KB (211 lines) | `pytest backend/tests/test_geospatial_pairing.py` | Migrated |
| 11 | `backend/app/scientific/sar_processor.py` | `backend/app/scientific/sar_processor.py` | `eff82bb` | `UNIQUE_SOURCE` | 5.8 KB (147 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 12 | `backend/app/scientific/satellite_observation.py` | `backend/app/scientific/satellite_observation.py` | `eff82bb` | `UNIQUE_SOURCE` | 4.6 KB (126 lines) | `pytest backend/tests/test_geospatial_pairing.py` | Migrated |
| 13 | `backend/app/services/scheduler.py` | `backend/app/services/scheduler.py` | `eff82bb` | `UNIQUE_SOURCE` | 7.2 KB (185 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 14 | `backend/data/raw/impact/S1A_IW_GRDH_20190426T122845_Puri_pre.nc` | `backend/data/raw/impact/S1A_IW_GRDH_20190426T122845_Puri_pre.nc` | `eff82bb` | `UNIQUE_SOURCE` | 104.8 KB | `python backend/scripts/run_impact_demo.py` | Migrated |
| 15 | `backend/data/raw/impact/S1A_IW_GRDH_20190508T122846_Puri_post.nc` | `backend/data/raw/impact/S1A_IW_GRDH_20190508T122846_Puri_post.nc` | `eff82bb` | `UNIQUE_SOURCE` | 104.1 KB | `python backend/scripts/run_impact_demo.py` | Migrated |
| 16 | `backend/data/raw/impact/S2A_MSIL2A_20190422T045701_Puri_pre.nc` | `backend/data/raw/impact/S2A_MSIL2A_20190422T045701_Puri_pre.nc` | `eff82bb` | `UNIQUE_SOURCE` | 125.7 KB | `python backend/scripts/run_impact_demo.py` | Migrated |
| 17 | `backend/data/raw/impact/S2B_MSIL2A_20190507T050709_Puri_post.nc` | `backend/data/raw/impact/S2B_MSIL2A_20190507T050709_Puri_post.nc` | `eff82bb` | `UNIQUE_SOURCE` | 98.1 KB | `python backend/scripts/run_impact_demo.py` | Migrated |
| 18 | `backend/main.py` | `backend/main.py` | `fb155aa` | `UNIQUE_SOURCE` | 468 bytes (18 lines) | `python backend/main.py` | Migrated |
| 19 | `backend/scripts/evaluate_models.py` | `backend/scripts/evaluate_models.py` | `eff82bb` | `UNIQUE_SOURCE` | 7.9 KB (187 lines) | `python backend/scripts/evaluate_models.py` | Migrated |
| 20 | `backend/scripts/generate_impact_reference_products.py` | `backend/scripts/generate_impact_reference_products.py` | `eff82bb` | `UNIQUE_SOURCE` | 8.8 KB (236 lines) | Script execution | Migrated |
| 21 | `backend/scripts/run_impact_demo.py` | `backend/scripts/run_impact_demo.py` | `eff82bb` | `UNIQUE_SOURCE` | 9.7 KB (239 lines) | `python backend/scripts/run_impact_demo.py` | Migrated |
| 22 | `backend/scripts/run_real_cyclone_demo.py` | `backend/scripts/run_real_cyclone_demo.py` | `eff82bb` | `UNIQUE_SOURCE` | 9.9 KB (240 lines) | `python backend/scripts/run_real_cyclone_demo.py` | Migrated |
| 23 | `backend/tests/test_geospatial_pairing.py` | `backend/tests/test_geospatial_pairing.py` | `eff82bb` | `UNIQUE_SOURCE` | 9.2 KB (240 lines) | `pytest backend/tests/test_geospatial_pairing.py` | Migrated |
| 24 | `backend/tests/test_impact_intelligence.py` | `backend/tests/test_impact_intelligence.py` | `eff82bb` | `UNIQUE_SOURCE` | 13.1 KB (324 lines) | `pytest backend/tests/test_impact_intelligence.py` | Migrated |
| 25 | `dashboard/requirements.txt` | `dashboard/requirements.txt` | `fb155aa` | `UNIQUE_SOURCE` | 387 bytes (20 lines) | Dependency check | Migrated |
| 26 | `docs/impact-intelligence.md` | `docs/impact-intelligence.md` | `eff82bb` | `UNIQUE_SOURCE` | 13.4 KB (277 lines) | Documentation review | Migrated |
| 27 | `frontend/src/app/impact/page.tsx` | `frontend/src/app/impact/page.tsx` | `eff82bb` | `UNIQUE_SOURCE` | 41.2 KB (928 lines) | `npm run build` in frontend | Migrated |
| 28 | `requirements.txt` | `requirements.txt` | `fb155aa` | `UNIQUE_SOURCE` | 988 bytes (42 lines) | Dependency check | Migrated |
| 29 | `vercel.json` | `vercel.json` | `fb155aa` | `UNIQUE_SOURCE` | 567 bytes (35 lines) | Schema inspection | Migrated |
| 30 | `backend/app/adapters/nasa.py` | `backend/app/adapters/nasa.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 5.8 KB (+28 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 31 | `backend/app/api/routes_ingest.py` | `backend/app/api/routes_ingest.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 15.6 KB (+8 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 32 | `backend/app/api/routes_storms.py` | `backend/app/api/routes_storms.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 16.4 KB (+278 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 33 | `backend/app/api/routes_system.py` | `backend/app/api/routes_system.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 9.9 KB (+24 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 34 | `backend/app/config.py` | `backend/app/config.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 1.8 KB (+1 line) | `pytest backend/tests/test_api.py` | Migrated |
| 35 | `backend/app/db/models.py` | `backend/app/db/models.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 9.2 KB (+87 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 36 | `backend/app/main.py` | `backend/app/main.py` | `fb155aa` | `DUPLICATE_BETTER_SOURCE` | 2.5 KB (+30 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 37 | `backend/app/ml/dataset.py` | `backend/app/ml/dataset.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 18.9 KB (+49 lines) | `pytest backend/tests/test_ml_dataset.py` | Migrated |
| 38 | `backend/app/scientific/storm_extractor.py` | `backend/app/scientific/storm_extractor.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 6.8 KB (+27 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 39 | `backend/pytest.ini` | `backend/pytest.ini` | `fb155aa` | `DUPLICATE_BETTER_SOURCE` | 134 bytes (+1 line) | `pytest backend/tests` | Migrated |
| 40 | `backend/requirements.txt` | `backend/requirements.txt` | `fb155aa` | `DUPLICATE_BETTER_SOURCE` | 642 bytes (+3 lines) | Dependency check | Migrated |
| 41 | `backend/tests/test_api.py` | `backend/tests/test_api.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 14.8 KB (+28 lines) | `pytest backend/tests/test_api.py` | Migrated |
| 42 | `dashboard/app.py` | `dashboard/app.py` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 24.2 KB (+283 lines) | Dashboard test | Migrated |
| 43 | `docs/experiments/experiment_results.json` | `docs/experiments/experiment_results.json` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 10.8 KB (Reconciled) | `python backend/scripts/evaluate_models.py` | Migrated |
| 44 | `frontend/src/app/explorer/page.tsx` | `frontend/src/app/explorer/page.tsx` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 28.5 KB (+505 lines) | `npm run build` in frontend | Migrated |
| 45 | `frontend/src/app/page.tsx` | `frontend/src/app/page.tsx` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 50.7 KB (+202 lines) | `npm run build` in frontend | Migrated |
| 46 | `frontend/src/components/AppShell.tsx` | `frontend/src/components/AppShell.tsx` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 5.2 KB (+1 line) | `npm run build` in frontend | Migrated |
| 47 | `frontend/src/lib/api.ts` | `frontend/src/lib/api.ts` | `fb155aa` | `DUPLICATE_BETTER_SOURCE` | 17.6 KB (+404 lines) | `npm test` in frontend | Migrated |
| 48 | `frontend/src/tests/api_client.test.ts` | `frontend/src/tests/api_client.test.ts` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 3.4 KB (+7 lines) | `npm test` in frontend | Migrated |
| 49 | `.env.example` | `.env.example` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 2.1 KB (+1 line) | Env inspection | Migrated |
| 50 | `README.md` | `README.md` | `eff82bb` | `DUPLICATE_BETTER_SOURCE` | 18.2 KB (Updated) | Markdown inspection | Migrated |
| 51 | `backend/data/raw/test_satellite_granule.nc` | `backend/data/raw/test_satellite_granule.nc` | `eff82bb` | `IDENTICAL` | 50.1 KB | `pytest backend/tests` | Retained |

---

## Migration Verification Summary
- **Total Tracked Files in Canonical (`cyclonesense`)**: **146 files**
- **Unique Modules Migrated**: **29 files**
- **Existing Modules Improved & Reconciled**: **22 files**
- **Net Lines of Code / Docs Added**: **+8,115 lines**
- **Total PyTest Test Suite Execution**: **55 passed / 0 failed**
- **Frontend Test Suite Execution**: **6 passed / 0 failed**
- **Frontend Next.js 16 Production Build**: **13 routes prerendered successfully (0 errors)**
