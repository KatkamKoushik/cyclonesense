# CycloneSense — Data, Model & Attribution Policy

This document establishes the official licensing, attribution, provenance, and data fidelity policies for all software, Earth Observation (EO) satellite datasets, best-track archives, neural model checkpoints, and synthetic/proxy calibration fixtures in the **CycloneSense** repository.

---

## 1. Governance & Licensing Framework

CycloneSense enforces a multi-tiered licensing structure aligned with open scientific research, authoritative meteorological data access standards, and open-source software best practices:

| Component | Asset Type | Governing License / Policy | Terms & Permissions |
| :--- | :--- | :--- | :--- |
| **Source Code** | Backend (FastAPI), Frontend (Next.js), CLI tools, tests | [MIT License](LICENSE) | Permissive: free commercial & non-commercial use, modification, distribution with attribution |
| **Model Weights** | PyTorch checkpoints (`.pt`) and architecture metadata | [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) | Free sharing & adaptation with mandatory attribution to CycloneSense |
| **NOAA Satellite Data** | GOES-16/18 ABI Level 2 NetCDF granules | [U.S. Public Domain (17 U.S.C. § 105)](https://www.noaa.gov/information-technology/open-data-dissemination) | Unrestricted open access via NOAA Open Data Dissemination (NODD) |
| **NOAA Best-Track Data** | IBTrACS v04r01 North Indian Ocean archive | [U.S. Public Domain (17 U.S.C. § 105)](https://www.ncei.noaa.gov/products/international-best-track-archive) | Unrestricted scientific open access via NOAA NCEI |
| **Copernicus Satellite Data** | Sentinel-1 SAR & Sentinel-2 MSI granules | [Copernicus Open Access Policy](https://sentinel.esa.int/web/sentinel/sentinel-data-access) | Free, full, and open access; mandatory Copernicus attribution notice |
| **NASA Earthdata CMR** | Metadata & granules via NASA CMR | [NASA Open Data Policy](https://www.earthdata.nasa.gov/engage/open-data-policy) | Free, open, and unrestricted public access |
| **ISRO MOSDAC Data** | INSAT-3D/3DR Imager & Sounder feeds | [ISRO Open Archival Policy](https://www.mosdac.gov.in) | Open research/academic access; user registration required |
| **Proxy / Synthetic Data** | Parameterized vortex grids & test fixtures | [CC0 1.0 Universal (Public Domain Dedication)](https://creativecommons.org/publicdomain/zero/1.0/) | Clearly labelled test fixtures; dedicated to public domain |

---

## 2. Satellite Earth Observation Data & Lineage

### 2.1 NOAA GOES-R Series ABI Data
- **Platform:** Geostationary Operational Environmental Satellites (GOES-16 / GOES-East, GOES-18 / GOES-West).
- **Instrument:** Advanced Baseline Imager (ABI).
- **Products Used:** Level 2 Cloud and Moisture Imagery (ABI-L2-CMIPC) in native NetCDF4 format.
  - Band 1 Visible ($0.47\ \mu\text{m}$)
  - Band 13 Clean Infrared ($10.35\ \mu\text{m}$)
  - Band 8 Water Vapor ($6.2\ \mu\text{m}$)
- **Dissemination:** NOAA Open Data Dissemination (NODD) program on Amazon Web Services (AWS) Open Data (`s3://noaa-goes16/`, `s3://noaa-goes18/`).
- **Attribution & Terms:** Works of the United States Government are not subject to domestic copyright protection pursuant to Title 17, Section 105 of the United States Code.
- **Reference:** Schmit, T. J., et al. (2017). "A closer look at the ABI on the GOES-R series." *Bulletin of the American Meteorological Society*, 98(4), 681–698.

### 2.2 NOAA NCEI IBTrACS Best-Track Archive
- **Platform:** International Best Track Archive for Climate Stewardship (IBTrACS) version v04r01.
- **Archive Ingested:** North Indian Ocean basin archive (`IBTrACS.NI.v04r01.nc`).
- **Provider:** NOAA National Centers for Environmental Information (NCEI) and World Meteorological Organization (WMO) Regional Specialized Meteorological Centres (RSMC New Delhi / IMD, JTWC).
- **Attribution & Terms:** U.S. Government work. Free and open international research access.
- **Citation:** Knapp, K. R., et al. (2010). "The International Best Track Archive for Climate Stewardship (IBTrACS)." *Bulletin of the American Meteorological Society*, 91(3), 363–376. DOI: 10.1175/2009BAMS2755.1.

### 2.3 Copernicus Sentinel-1 and Sentinel-2 Data
- **Platforms:** Sentinel-1 C-Band Synthetic Aperture Radar (C-SAR) and Sentinel-2 MultiSpectral Instrument (MSI).
- **Products Used:** Sentinel-1 Level-1 Ground Range Detected High-Resolution (GRDH) and Sentinel-2 Level-2A Bottom-Of-Atmosphere (BOA) Reflectance.
- **Provider:** European Space Agency (ESA) & European Commission via the Copernicus Data Space Ecosystem (CDSE).
- **Attribution Notice:**
  > *"Contains modified Copernicus Sentinel data [2019], processed by CycloneSense."*
- **Terms:** Governed by the European Commission's open access regulation (EU Regulation No 1159/2013).

### 2.4 NASA Earthdata Common Metadata Repository (CMR)
- **Provider:** NASA Earth Science Data and Information System (ESDIS).
- **Terms:** Unrestricted, full, and open data access in accordance with the NASA Open Data Policy.

### 2.5 ISRO MOSDAC
- **Provider:** Meteorological and Oceanographic Satellite Data Archival Centre (MOSDAC), Space Applications Centre, Indian Space Research Organisation (ISRO).
- **Terms:** Available for research and operational meteorology. Users must provide their own registered credentials (`MOSDAC_USERNAME`, `MOSDAC_PASSWORD`) via local `.env` configuration.

---

## 3. Pretrained Neural Network Checkpoints & Weights

All model weights located in [`backend/models/checkpoints/`](backend/models/checkpoints/) were developed and trained as part of the CycloneSense research initiative:

| Checkpoint File | Architecture | Primary Modality | SHA-256 Digest | License |
| :--- | :--- | :--- | :--- | :--- |
| `cyclone_fusion_v1.0.0.pt` | Multimodal Fusion (ResCNN + MLP) | 2-Ch IR/WV ($128\times128$) + 8 Covariates | `365b50788b6e9a247d85a7c1a95526eb89aeecb97e2db39f26cbb25fbc396b16` | CC BY 4.0 |
| `cyclone_image_v1.0.0.pt` | 4-Stage Convolutional Neural Net | 2-Ch IR/WV ($128\times128$) | `4ff0c48bb11c1d8487fe83e40be5c94fa25d3fa9ae50b4ba79da04e578c7c134` | CC BY 4.0 |
| `cyclone_env_v1.0.0.pt` | LayerNorm Multi-Layer Perceptron | 8 Environmental/Kinematic Covariates | `9c8e103989c72e2d93eef3a31cbe572e4526df6ef2d4243ef0e2ee9d9e6eb0b8` | CC BY 4.0 |

Each checkpoint is accompanied by an immutable JSON metadata descriptor (`*_metadata.json`) certifying its architecture parameters, normalization constants, and training split provenance.

---

## 4. Truth-in-Advertising: Proxy & Synthetic Data Labelling

To uphold absolute scientific rigor and avoid any misrepresentation of test fixtures as authentic spaceborne observations, CycloneSense explicitly catalogues every tracked data artifact:

| Local Repository Path | Data Type | Scientific Classification | Purpose & Provenance |
| :--- | :--- | :--- | :--- |
| `backend/data/raw/OR_ABI-L2-CMIPC-M6C01_...nc` | NetCDF4 (13.39 MB) | **AUTHENTIC SPACEBORNE** | Real NOAA GOES-16 ABI Band 1 Visible CONUS granule (Hurricane Helene, 2024-09-26T18:01:17Z). Ingested from NOAA AWS S3. |
| `backend/data/raw/OR_ABI-L2-CMIPC-M6C13_...nc` | NetCDF4 (3.59 MB) | **AUTHENTIC SPACEBORNE** | Real NOAA GOES-16 ABI Band 13 Clean Infrared granule. Ingested from NOAA AWS S3. |
| `backend/data/raw/IBTrACS.NI.v04r01.nc` | NetCDF4 (2.95 MB) | **AUTHENTIC BEST-TRACK** | Official NOAA NCEI historical best-track archive for North Indian Ocean cyclones (1972–2026). |
| `backend/data/raw/impact/S1A_..._Puri_pre.nc` | NetCDF4 (104.8 KB) | **AUTHENTIC SPACEBORNE SUBSET** | Real Copernicus Sentinel-1A SAR C-band pre-landfall radar granule (Cyclone Fani, 2019-04-26, Puri, Odisha). |
| `backend/data/raw/impact/S1A_..._Puri_post.nc` | NetCDF4 (104.1 KB) | **AUTHENTIC SPACEBORNE SUBSET** | Real Copernicus Sentinel-1A SAR C-band post-landfall radar granule (Cyclone Fani, 2019-05-08, Puri, Odisha). |
| `backend/data/raw/impact/S2A_..._Puri_pre.nc` | NetCDF4 (125.7 KB) | **AUTHENTIC SPACEBORNE SUBSET** | Real Copernicus Sentinel-2A MSI L2A pre-landfall optical granule (Cyclone Fani, 2019-04-22, Puri, Odisha). |
| `backend/data/raw/impact/S2B_..._Puri_post.nc` | NetCDF4 (98.1 KB) | **AUTHENTIC SPACEBORNE SUBSET** | Real Copernicus Sentinel-2B MSI L2A post-landfall optical granule (Cyclone Fani, 2019-05-07, Puri, Odisha). |
| `backend/data/raw/reference_cyclone_grid.nc` | NetCDF4 (130.0 KB) | **SYNTHETIC / CALIBRATED PROXY** | Numerically synthesized CF-1.8 NetCDF grid parameterizing Holland/Rankine vortex physics. Used for deterministic offline tests when live feeds are unavailable. |
| `backend/data/raw/reference_satellite_grid.nc` | NetCDF4 (130.0 KB) | **SYNTHETIC / CALIBRATED PROXY** | Numerically synthesized 2-channel IR/WV grid for sensor calibration and coordinate transformation testing. |
| `backend/data/raw/test_satellite_granule.nc` | NetCDF4 (50.1 KB) | **SYNTHETIC UNIT TEST FIXTURE** | Minimal NetCDF test fixture generated by test suite for physical bounds ($T_B$) and DQF flag validation. |

### 4.1 Operational Truth-in-Advertising Rules:
1. **API Responses:** Any endpoint serving predictions or grids derived from synthetic/proxy fixtures explicitly marks the payload with `"is_synthetic": true` and `"data_fidelity": "SYNTHETIC_PROXY"`.
2. **Dashboard UI:** The frontend indicators display distinctive badge labels (`AUTHENTIC SPACEBORNE` vs. `CALIBRATED PROXY`) whenever viewing satellite products or model outputs.
3. **No Fabricated Telemetry:** Historical best-track metrics (pressure, wind speed, coordinate trajectories) are always retrieved directly from authentic NOAA IBTrACS NetCDF files.

### 4.2 Machine Learning Dataset Pipelines & Target-Input Separation:
- **`TropicalCycloneDataset` (Proxy Experiment Pipeline):**
  This dataset is an analytical proxy pipeline where 2-channel radiative rasters are synthesized directly from storm coordinates and ground truth wind speed ($T_B = g(\text{wind})$). Because the raster's physical structure is analytically coupled to the target label, neural models evaluated on this dataset learn to invert the generator's formula. The resulting test metrics (MAE ~1.7 kts, $r = 0.999$) reflect synthetic formula inversion and must NOT be interpreted as evidence of operational spaceborne predictive performance.
- **`PairedSatelliteCycloneDataset` (Authentic Spaceborne Pipeline):**
  This dataset enforces strict target-input separation by consuming authentic spaceborne satellite NetCDF granules (e.g. NOAA GOES-16 ABI Band 1/13) paired with IBTrACS best-track observations via closed-form trigonometric coordinate georeferencing, with zero raster fabrication.

---

## 5. Responsible AI & Advisory Notice

- **Research & Decision Support Prototype:** CycloneSense is an academic and exploratory research platform developed to investigate multimodal deep learning, biophysical change detection, and explainable AI in tropical cyclonology.
- **Not an Official Meteorological Warning System:** Model predictions and automated impact assessments generated by this system do **not** constitute official government weather forecasts, tropical cyclone advisories, or evacuation orders.
- **Authoritative Issuing Authorities:** Official life-safety cyclone warnings are issued exclusively by recognized Regional Specialized Meteorological Centres (RSMCs), Tropical Cyclone Warning Centres (TCWCs), and national meteorological agencies:
  - **India & North Indian Ocean:** [India Meteorological Department (IMD)](https://mausam.imd.gov.in)
  - **Atlantic & Eastern Pacific:** [National Hurricane Center (NOAA / NHC)](https://www.nhc.noaa.gov)
  - **Western Pacific & Global Military:** [Joint Typhoon Warning Center (JTWC)](https://www.metoc.navy.mil/jtwc/)
