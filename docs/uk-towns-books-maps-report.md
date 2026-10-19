# Linking UK towns to published books and maps

*Research report, 19 October 2026*

## Summary

You can build a per-town list of books and maps from openly available data. The key design choice is to give each town a stable identifier first, then attach books and maps to it in different ways:

- **Town identifiers:** use an ONS Built-up Area code (`BUA22CD`) or a Wikidata QID as the primary key. The ONS polygon gives the town's footprint. Wikidata links the town to the library and gazetteer IDs that everything else uses.
- **Books:** link through **authorised library subject headings**, such as LCSH/FAST "Bath (England)" or "Newport (Wales)", not through bare place names. Then harvest from the British National Bibliography (BNB), Jisc Library Hub Discover, Open Library, Project Gutenberg and Wikidata.
- **Maps:** link **spatially**. Intersect the town polygon with map footprints: NLS Ordnance Survey sheet indexes, Allmaps or other georeferenced maps, and catalogue records with MARC 034 coordinates. Old Maps Online is the quickest manual route.

The pipeline in section 4 can be built entirely from CC0 or OGL sources. WorldCat, Digimap and some NLS and Jisc data have licence restrictions; see section 3.

### How this was researched

An AI research agent searched the web. Its sandbox could not open most source sites directly, so findings come from search results that quote official pages, plus prior knowledge.

- **[V]** means the agent confirmed the claim from an official or recent source.
- **[U]** means the claim is unverified and should be checked before you rely on it. Exact API parameters and Wikidata property numbers are mostly [U].

---

## 1. Data sources

### A. Gazetteers and town identifiers (the spine)

| Source | What it gives | Access | Licence / cost | How it links to a town | URL |
|---|---|---|---|---|---|
| ONS Index of Place Names (IPN), July 2024 [V] | Over 100,000 localities in GB, each with its local authority and county | Bulk CSV from the ONS Open Geography Portal | Probably OGL [U] | Canonical names, with the parent district and county that separate same-name places | https://open-geography-portalx-ons.hub.arcgis.com/datasets/ons::index-of-place-names-july-2024-in-gb |
| ONS Built-up Areas (BUA), Dec 2022 [V] | Town polygons, with `BUA22CD`, name, and lookups to LAD, county and region | Shapefile, GeoJSON, CSV, ArcGIS service | OGL (contains OS data) | **Best town polygon**; `BUA22CD` is a good primary key | https://www.data.gov.uk/dataset/46fff29c-7836-4082-9495-99e87476d402/built-up-areas-december-2022-boundaries-gb-bgg |
| OS Open Names [V] | About 44k settlements, each with a point, district, county and bounding box [U] | CSV/GML download; OS Names API | OGL v3, free | Geocoding; separating duplicate names | https://docs.os.uk/os-apis/accessing-os-apis/os-names-api |
| GeoNames [V] | Gazetteer with alternate and historic names | TSV dumps; web service | CC BY 4.0 | Many library authorities (FAST, LC) link to GeoNames IDs | https://download.geonames.org/export/dump/ |
| Wikidata | Town QIDs with coordinates, aliases and external IDs: GeoNames, GSS code, FAST, LCNAF, Vision of Britain, Commons category (property numbers [U]) | SPARQL; JSON dumps | CC0 | **The hub** that joins ONS, OS, GeoNames and library authorities | https://query.wikidata.org/ |
| Vision of Britain / GB Historical GIS [V] | Historic places and administrative units with stable IDs | Website; most downloads withdrawn | Boundaries need a commercial licence; non-commercial use on request | Historic units and name variants | https://www.visionofbritain.org.uk/data |
| GB1900 gazetteer [V] | About 2.55M names transcribed from the OS six-inch maps of 1888–1914, with coordinates | Zip download | CC BY-SA (raw dump CC0) | Historic name variants located on the period map | https://maps.nls.uk/projects/os1900/help |

### B. Books

| Source | What it gives | Access | Licence / cost | How it links to a town | URL |
|---|---|---|---|---|---|
| British National Bibliography (BNB) [V] | UK publications since 1950, with subject headings and place of publication | Moving to the "Share Family" beta (bl.natbib-lod.org). Old SPARQL and dumps withdrawn; new API and dumps planned | Historically CC0; current licence [U] | Geographic subject headings (MARC 651), imprint place (260/264) | https://www.bl.uk/more/collection-metadata-services/ |
| Jisc Library Hub Discover [V] | Union catalogue of 100+ UK academic, national and special libraries. Strong on local history | Web; API/SRU at https://discover.libraryhub.jisc.ac.uk/support/api/ (details [U]) | Free to search; MARC reuse non-commercial | Subject and place search | https://discover.libraryhub.jisc.ac.uk/ |
| OCLC FAST [V] | About 160k geographic headings with coordinates and links to GeoNames, LCSH and Wikipedia | RDF download; lookup service | ODC-By | **Key bridge**: FAST geographic ID → GeoNames/Wikidata → town | https://fast.oclc.org/ |
| WorldCat Search API v2 [V] | Largest bibliographic database, with FAST subjects | REST/JSON | **Needs OCLC subscriptions** | FAST geographic subject queries | https://www.oclc.org/developer/api/oclc-apis/worldcat-search-api.en.html |
| Library of Congress id.loc.gov | LCSH and name authorities; many carry coordinates (MARC 034) and GeoNames links | Linked data; bulk downloads [U] | Public domain [U] | Authorised qualified names, e.g. "Newport (Wales)" | https://id.loc.gov/ |
| Open Library | Works with `subject_places` | `search.json?q=place_key:...`; monthly dumps [U] | CC0 [U] | Place-subject strings (noisy) | https://openlibrary.org/search/howto |
| Google Books API | Volume metadata | REST, free key | Free | Low precision; use only to enrich records | https://developers.google.com/books/docs/v1/using |
| Wikidata (books) [V] | Narrative location (P840), main subject (P921), place of publication (P291) | SPARQL | CC0 | Direct QID → QID. Most precise, but low coverage | https://www.wikidata.org/wiki/Wikidata:WikiProject_Books |
| HathiTrust [V] | Hathifiles (bulk TSV) and MARC via OAI | Bulk downloads | Mostly CC0; OCLC-derived records restricted | Finding digitised copies (join on OCLC number or ISBN) | https://www.hathitrust.org/hathifiles |
| Internet Archive | Digitised books, including many 19th-century local histories | Advanced search and scrape APIs | Metadata free | Free-text subject field (noisy) | https://archive.org/advancedsearch.php |
| Project Gutenberg [V] | Catalogue with LCSH subjects | `pg_catalog.csv.gz`, RDF, Gutendex API | Public domain | LCSH geographic subjects | https://www.gutenberg.org/ebooks/offline_catalogs |
| Literary Atlas of Wales [V] | 558 novels, each with a key location | Web atlas; dataset availability [U] | [U] | Coordinates per novel | https://www.literaryatlas.wales/ |
| Local studies collections | Council library and archive catalogues | Mostly web only | Varies | Usually cover a single town or county | — |

### C. Maps

| Source | What it gives | Access | Licence / cost | How it links to a town | URL |
|---|---|---|---|---|---|
| National Library of Scotland Maps [V] | Seamless georeferenced OS 6-inch, 25-inch and 1-inch layers for GB, sheet scans, and "Find by place" sheet indexes | Tiles via MapTiler (free non-commercial tier); viewer pages; some datasets | Images often CC-BY; tiles under MapTiler terms | **Intersect sheet-index polygons with the town polygon.** Public GeoJSON of sheet indexes unconfirmed [U]; ask geo@nls.uk | https://maps.nls.uk/ , https://maps.nls.uk/guides/datasets |
| Old Maps Online [V] | Aggregates 500k+ maps from BL, NLS, Rumsey and others; searchable by location and date | Web UI; API [U] | Free | Built-in footprint-to-place ranking. **Easiest manual route** | https://www.oldmapsonline.org/ |
| British Library maps and Georeferencer [V] | King George III Topographical Collection (K.Top, about 40k items, 1500–1824); crowd-georeferenced footprints | Flickr; BL catalogue (MARC 034) | Out of copyright | Bounding-box intersection | https://www.bl.uk/ |
| Allmaps [V] | Open georeference annotations for IIIF maps, including NLS maps | JSON annotations; daily dump [U] | Open [U] | Footprint polygon intersection | https://allmaps.org/ |
| Digimap (EDINA) [V] | Historic OS County Series 1846–1969 and modern OS mapping | Institutional login | **UK HE/FE subscription only** | Location search in the UI | https://digimap.edina.ac.uk/ |
| OS OpenData (OpenMap Local, Zoomstack) [V] | Current vector and raster mapping | OS Data Hub downloads | OGL, free | Clip to the town polygon (the modern map layer) | https://docs.os.uk/os-downloads/products/maps-and-imagery-portfolio/os-openmap-local |
| David Rumsey Map Collection | About 150k maps [U], many georeferenced | IIIF; GeoBlacklight bounding boxes | Mostly CC BY-NC-SA [U] | Bounding-box intersection | https://www.davidrumsey.com/ |
| Vision of Britain maps | Historic OS 1-inch, Land Utilisation and boundary maps | Web only | Non-commercial | Same place IDs as its gazetteer | https://www.visionofbritain.org.uk/ |
| Library Hub / Bodleian / Cambridge map catalogues | Catalogued map holdings, some with 034 coordinates and 255 scale | As in the books table; Digital Bodleian IIIF [U] | Varies | 651 heading or 034 bounding box | — |
| Wikimedia Commons [V] | Old maps by category; Template:Map with bounding boxes | MediaWiki API | Mostly PD or CC | Commons category (Wikidata P373) or bounding box | https://commons.wikimedia.org/wiki/Commons:Wikimaps/Template |
| Historic Environment Records / Heritage Gateway | HER entries, which often cite maps and local histories | Web search | Varies | By county | https://www.heritagegateway.org.uk/ |

---

## 2. Gotchas

1. **Ambiguous names.** Several towns share names, e.g. Newport (Wales, Isle of Wight, Shropshire, Essex, Pembrokeshire), Richmond and Boston. Never match the bare string. Match the qualified authority heading, then its ID, then the Wikidata QID.
2. **Historic names and counties.** LCSH qualifiers have changed over time ("Bath (Avon)" became "Bath (England)"), so use the variant labels as well. OS County Series sheet numbers run **per historic county**, so use the NLS sheet indexes rather than sheet numbers.
3. **Town vs. built-up area.** BUA polygons can merge or split towns differently from local usage. Keep a crosswalk between BUA codes, IPN entries and QIDs.
4. **Different relations.** A book can be *about* a town (subject heading), *set in* it (Wikidata P840), or *published in* it (imprint place). Imprint place is noisy for London, Oxford and Edinburgh. Store the relation type with each link.
5. **Map scale.** Small-scale county or national maps intersect every town. Filter by scale, or by how much of the map's footprint the town covers.
6. **Licences.** WorldCat, Jisc MARC records, NLS tiles, Digimap, GB1900 (share-alike) and Vision of Britain boundaries all restrict public redistribution. Wikidata, ONS, OS OpenData, Gutenberg and HathiTrust's own data are open.
7. **BNB is in transition.** Check the new platform, or ask metadata@bl.uk.
8. **Duplicates.** Deduplicate on ISBN, OCLC number, or normalised title + author + year, and group editions into works.
9. **Free-text false positives.** "Reading" and "Bath" also match ordinary words. Use free-text sources only after authority-based matching.

---

## 3. Choosing sources by intended use

| Use | Recommended sources |
|---|---|
| Public or commercial product | ONS, OS OpenData, Wikidata, GeoNames, FAST (with attribution), LC, Gutenberg, Open Library, HathiTrust (non-OCLC records), Allmaps, Commons |
| Personal or academic research | All of the above, plus Library Hub, NLS tiles and sheet indexes, Old Maps Online, Digimap (if you are at a UK university), Vision of Britain |
| Quick manual lookup for one town | Old Maps Online, NLS "Find by place", Library Hub Discover subject search, Wikipedia/Wikidata |

---

## 4. Recommended pipeline

1. **Build the town spine.** Load ONS BUA 2022 polygons (or the IPN) as the master list and join to OS Open Names. Match each town to Wikidata on coordinates inside the polygon, label and GSS code. From Wikidata pull GeoNames, FAST and LC IDs, Vision of Britain IDs, the Commons category and aliases. Add historic name variants from GeoNames, LC/FAST and GB1900.
2. **Build a heading crosswalk.** Record each town's authorised LCSH/FAST geographic heading and its variants. For towns with no ID, query FAST or id.loc.gov by label and county, and confirm by coordinates (within the polygon or about 2 km). This step resolves ambiguous names like Newport.
3. **Harvest books.**
   - Wikidata SPARQL for works linked to the town's QID through P840, P921 and P291.
   - BNB and Library Hub, querying by authorised heading. Keep the subdivisions (History, Description and travel, Fiction, Maps).
   - Open Library `place_key:` and Gutenberg subjects, filtered against the heading list.
   - Optionally, WorldCat by FAST ID if you have a subscription.
   - HathiTrust and Internet Archive for digitised copies.

   For each link, store the relation type, the source and a confidence score.
4. **Harvest maps.**
   - Intersect the town polygon with NLS OS sheet indexes (6-inch and 25-inch, 1st and 2nd editions).
   - Intersect with Allmaps and Rumsey/GeoBlacklight footprints.
   - Use catalogue map records that have 034 coordinates or a matching 651 heading.
   - Use Commons maps via the town's category.
   - Generate a per-town Old Maps Online search link.
   - Clip OS OpenMap Local for a modern map.
   - Drop small-scale maps where the town covers less than 1% of the footprint, unless the map is a town plan.
5. **Output per town:** books (grouped into works, with relation type) and maps (series, sheet, date, scale, link). Include source and licence columns so you can filter for reuse.

A possible data model:

```
town(town_id PK, bua22cd, wikidata_qid, name, county, geom, ...)
town_heading(town_id FK, scheme [LCSH|FAST|...], heading, authority_id, is_variant)
book(book_id PK, title, author, year, isbn, oclc, source, licence)
town_book(town_id FK, book_id FK, relation [about|set_in|published_in], source, confidence)
map(map_id PK, title, series, sheet, date, scale, footprint_geom, url, source, licence)
town_map(town_id FK, map_id FK, overlap_ratio, source)
```

---

## 5. Open questions to verify

These could not be checked from the research sandbox and should be confirmed from a machine with normal web access:

- Jisc Library Hub Discover API and SRU syntax.
- BNB's current SPARQL, dump availability and licence on the Share Family platform.
- Whether NLS publishes OS sheet-index polygons as GeoJSON downloads.
- Whether Old Maps Online has a public bounding-box API.
- Where the Allmaps bulk dataset is, and its licence.
- Exact Wikidata property numbers: GeoNames P1566, GSS code P836, FAST P2163, LCNAF P244, Vision of Britain P3615/P3616, Commons category P373.

## Suggested next step

Prototype the pipeline for 3–5 towns, including at least one ambiguous name such as Newport. Use only Wikidata, ONS BUA, FAST and Open Library for books, and the NLS sheet index plus Old Maps Online links for maps. This will test the identifier crosswalk before you invest in the full harvest.
