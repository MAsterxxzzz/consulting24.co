# Bing Webmaster Tools audit and improvement plan — consulting24.co

Audit date: 28 September 2026 (data through 25–26 September). Sources: Bing Webmaster Tools internal reports pulled in full (Search Performance keyword/page/device/country tables for 3 months, previous 3 months and 30 days; 24-month daily trend; AI Performance; Backlinks; Site Explorer per folder and per status; Sitemaps; IndexNow; Site Scan of 21 Sep), live HTTP checks and a scan of the 700 English landing pages in this repo. Previous audit: `scripts/BING_INDEX_MASTERPLAN.md` (21 Sep 2026).

## 0. Summary

Bing traffic tripled after the June rebuild, then stalled: 58 clicks from 5.7K impressions in the last three months (previous three months: 17 clicks from 1.4K). Clicks have been flat at 15–21 per month since July while impressions keep growing, so the problem is now conversion of impressions into clicks and the choice of URL Bing shows, not indexing. Indexing is healthy: 1,945 of ~2,000 known URLs indexed, 0 errors, and the 1,929 zh/es/ar pages were indexed within a week of launch.

Four things explain the flat clicks:

1. **266 of 700 English landing pages carry a garbled H1** (a title prefix was pasted in front of the old heading, e.g. "MiCA License Crypto License: Complete Guide for 2026" or "Crypto Fund License in Romania (2026): Cost & Setup Romania: Your Guide to…"). These pages receive 42% of all landing-page impressions (494 of 1,176) and their zh/es/ar translations inherited the same garbage. Bing weights the H1/title match heavily and shows the H1 as the snippet title when the `<title>` is generic.
2. **The Blogger mirror still wins.** 117 blog.consulting24.co URLs earned 690 impressions and 22 clicks (38% of all clicks); their www twins earned 90 impressions and 3 clicks. Only 21 of the 117 www twins have any impressions at all.
3. **The Panama product has no Bing landing page.** The homepage (Panama offer) got 3 impressions and 1 click in three months; `/panama-crypto-license/` meta-refreshes to `/` and is the only Site Scan error. Panama demand (139 impressions, 40 queries) lands on Blogger and www blog posts instead.
4. **Money-page titles are still generic.** MiCA, MSB, VASP, VARA, CASP and Stablecoin all use "X License (2026 Guide) - Consulting24"; /mica-license/ has 139 impressions and 1 click.

Phase 0 of the 21 Sep plan (owner clicks) was not done: `http://www.consulting24.co/` still answers 200 and Bing recorded http versions of /casp-license and /vasp-license as canonical sources on 20 Sep; `pages-sitemap.xml` (2023, 404) is still registered; six live pages are still held as 404 from the August outage. Phase 1 code (IndexNow delta, sitemap index, lastmod) works: IndexNow went from ~1,100/day to 200/200/26/1/1 on 23–27 Sep.

## 1. Where Bing stands (28 Sep 2026)

| Metric | 3M (28 Jun–25 Sep) | Previous 3M | 30D |
|---|---|---|---|
| Clicks | 58 | 17 | 15 |
| Impressions (all verticals) | 5,691 | 1,448 | 1,840 |
| CTR | 1.02% | 1.17% | 0.82% |
| Impressions in web keyword table | 2,422 (43%) | 387 | 677 |
| Web CTR | 2.39% | 4.39% | 2.22% |
| Keywords / pages with impressions | 916 / 378 | 275 / 96 | 325 / 194 |

- The ~3,270 impressions outside the keyword table are Copilot/Chat groundings; they produce citations but no measurable clicks. Country "ww" (unattributed, mostly Copilot) delivered 32 of the 58 clicks; US 3,594 impressions but 9 clicks.
- Desktop 5,043 impressions / 53 clicks; mobile 648 / 5.
- Monthly clicks: Jun 9, Jul 21, Aug 21, Sep 15 (25 days). Daily impressions rose from ~61/day in August to ~94/day after 14 Sep without a click response.
- 304 keywords sit at position 1–3.5 (970 impressions, 27 clicks, 2.8% CTR); 600 at 4–10 (1,435 impressions, 31 clicks). Only 34 keywords have ≥10 impressions (560 impressions, 23%); 39% of impressions come from 8+ word Copilot-style questions.

### Index (Site Explorer, last 6 months)

| Folder | URLs known | Indexed | Warning / Excluded | Clicks | Impressions |
|---|---|---|---|---|---|
| consulting24.co (all) | 2.0K | 1,945 | 40 / 20 | 51 | 1.8K |
| /zh | 468 | 468 | 0 | – | 8 |
| /es | 433 | 433 | 0 | – | 3 |
| /ar | 75 | 75 | 0 | – | 2 |
| /blog | 338 | 332 | 2 / 4 | 10 | 318 |
| /post (legacy Wix) | 57 | 31 | 23 / 3 | 5 | 62 |
| /news | 4 | 4 | 0 | – | 13 |
| blog.consulting24.co | 387 | 372 | 3 / 13 | 20 | 644 |
| ru.consulting24.co | 1 | 0 | 1 (404) | – | – |

- Sitemaps: `sitemap.xml` index = 4.2K URLs discovered, Success, crawled 26 Sep; Blogger sitemap 329; `pages-sitemap.xml` (2023, 99 URLs, live 404) still registered; Blogger atom feed 25.
- IndexNow lifetime 219.3K. Daily: 21 Sep 2,309 (translation launch), 23 Sep 200, 24 Sep 200, 25 Sep 26, 26 Sep 1, 27 Sep 1.
- Dead links (13) include live pages Bing has not recrawled since the August outage: /slovakia-crypto-license (last crawl 23 Aug, 3 impressions), /estonia-company-registration (21 Aug, live since 23 Sep), /crypto-payment-institution-license-hong-kong (24 Aug), /crypto-exchange-license-isle-of-man (20 Aug), /nominee-director-fee (22 Aug, 9 impressions, now a stub), /dubai-vara-license (stub). /crypto-stablecoin-license-philippines has never been crawled. True 404s: /home, /crypto-licenses, /crypto-license-switzerland, /crypto-license-cyprus, /estonia-online-company, /estonia-e-residency-bank-accounts.
- "URLs redirecting" (~40) are slash-less variants of live pages (GitHub Pages 301s them to the trailing slash); the slashed versions are indexed, so this is noise.
- Canonical-source list shows `http://www.consulting24.co/casp-license` and `/vasp-license` (Is Https: false), discovered 20 Sep. The http duplicate site is still being crawled.
- Site Scan (21 Sep, 745 pages): 1 error (meta description missing on `/panama-crypto-license/`), 11 warnings: 7 images without alt, 3 titles over 70 chars (`/luxury-chauffeur-service-dubai/hi/`, two /news/ posts; locally four news titles are 76–102 chars), 1 meta refresh (the same Panama stub). Recommendations: none.

### Pages and content

Top pages by web impressions (3M): /mica-license/ 139 (1 click), /usa-crypto-license/ 99 (3), /singapore-crypto-license/ 79 (1), Blogger south-africa-crypto-license 68 (3), Blogger costa-rica banking rails 60 (0), /mauritius-crypto-license/ 43 (0), /germany-crypto-license/ 37 (1), /msb-license/ 35 (0), /crypto-otc-desk-license-dubai/ 32 (0), /canada-crypto-license/ 32 (1), /poland-crypto-license/ 31 (0), /costa-rica-crypto-license/ 28 (0).

Impression split (web, 3M): English landing pages 1,176 (26 clicks), Blogger 690 (22), www /blog/ 355 (10), zh/es/ar 12 (0).

Demand clusters by impressions: banking and payment rails 420, MiCA 175, OTC desks 153, Panama 139, USA 138, tax 115, El Salvador 109, Mauritius 108, Seychelles 107, Poland 105, VASP 96, BVI 94, Hong Kong 92, funds 92, Costa Rica 85, Cayman 82, Dubai 82, crypto casinos 77, Bahrain 77. Intent: cost/price/fee 460, requirements/how-to 448, year-qualified 476.

Month-over-month (30D vs previous 30D) losers: Blogger costa-rica banking 60→0, /costa-rica-crypto-license/ 26→0, /crypto-otc-desk-license/ 21→0, /crypto-gambling-license-switzerland/ 18→0, /msb-license/ 15→0. Gainers: /crypto-otc-desk-license-dubai/ 1→24, /poland-crypto-license/ 6→24, Blogger south-africa 23→45.

### AI Performance (Copilot, 3M)

3,303 citations, 962 distinct cited pages over 90 days (~10.7 cited pages/day). Top grounding queries: "msb license" 250 citations (33% share), "mica license" 239 (9%), "vara license" 128 (35%), "licenses required for stablecoin infrastructure providers" 121 (10%), "license to offer crypto yield services to customers" 104 (20%), a "BH Digital AML KYC" cluster ~166, "crypto license providers low setup cost" 52 (25%). Most-cited pages: /mica-license/ 374, /msb-license/ 284, /usa-crypto-license/ 218, /blog/aml-kyc-requirements-for-a-bahrain-crypto-company/ 159, /vara-license/ 144, /crypto-stablecoin-license-usa/ 137, Blogger VASP page 98, Blogger Canada page 86.

### Backlinks

112 referring domains, 779 pages, 36 anchors. darkschemedirectory.com 226, "consulting24.co" 182 (these are Blogger's own internal links to its /p/ pages), conquerclub.com 151: 72% of all links from three sources. About ten domains are topical or legitimate (bitcointalk, hackernoon, cbinsights, globalriskcommunity, publish0x, bitcoinisle, licencemap, ssb.ee, inforegister.ee, linkedin, x.com). 593 of 783 links point at the homepage; only 9 distinct targets. Bing's keyword tool shows tiny volumes for the head terms (e.g. "mica license" 62 broad impressions per quarter, mostly DE/GB/ES), so prioritise by the site's own impressions, not by tool volume.

## 2. Status of the 21 Sep plan

| Item | Status |
|---|---|
| IndexNow delta-only | Done and working (200/200/26/1/1 per day) |
| Sitemap index + template-insensitive lastmod | Done |
| Enforce HTTPS on Consulting24est | Not done; http root 200, http canonical sources seen 20 Sep |
| Delete pages-sitemap.xml in Bing | Not done |
| Request indexing for Appendix B/C | Not done; 6 live pages still held as 404 |
| Remove ru DNS record | Not done (Bing warning) |
| Redirect 16 dead Wix slugs (Appendix A) | Not done (none in config/redirects.json; /crypto-license-switzerland etc. still 404) |
| Blogger teasers / noindex | Not done; Blogger copies still full text with self-canonical |
| Title rewrites (Phase 2) | Partial: OTC desk page done; MiCA/MSB/VASP/VARA/CASP/Stablecoin still generic |
| Clarity, Bing Places, PubHub | Not done (PubHub integration returns 204) |
| PRs #29–#32 (header, tables, hub cards, IndexNow-after-deploy) | Open, unmerged since 24–26 Sep |

## 3. Phase 0 — this week, owner clicks (no code)

- [ ] GitHub → Consulting24est/consulting24.co → Settings → Pages → **Enforce HTTPS**. Verify with `curl -sI http://www.consulting24.co/` → 301.
- [ ] Reply "merge" for PRs #32, #31, #30, #29 on MAsterxxzzz/consulting24.co, then `git push c24est main` and `python3 scripts/indexnow.py flush --wait 900`.
- [ ] Bing → Sitemaps → delete `https://www.consulting24.co/pages-sitemap.xml`.
- [ ] Bing → URL Inspection → Request indexing (10/day quota) for: /slovakia-crypto-license/, /estonia-company-registration/, /bvi-company-registration/, /crypto-licensing-consultation/, /crypto-payment-institution-license-hong-kong/, /crypto-exchange-license-isle-of-man/, /crypto-stablecoin-license-philippines/, /nominee-director-fee/, /dubai-vara-license/, /jurisdictions/.
- [ ] DNS → remove the `ru` CNAME (or 301 it to www).
- [ ] Bing → Settings → Users: add mardo@consulting24.co as owner so alerts stop going only to info@aiangels.io.

## 4. Phase 1 — next two weeks (code)

1. **H1 repair sweep** (`scripts/fix_h1.py`, one-off + QC guard). For the 266 pages whose H1 matches `License Crypto License|Cost & Setup [A-Z]|Requirements: Your Complete|License License`, set the H1 to the `<title>` stem (strip " - Consulting24" / " | Consulting24" / " | C24"), keep the keyword check in `generate.py` satisfied, and change the prefixing rule in `scripts/generate.py` (around line 422) so it never prepends a keyword to an H1 that already contains a colon-separated title. Re-run `translate_run.sh` afterwards: the 798 zh/es/ar twins re-translate because the content digest changes (estimated cost under USD 6 at the September rate). Add the pattern to `qc_audit.py` so it cannot come back.
2. **Titles for the ten money pages** (≤65 chars, query phrase first, cost/timeline anchor, year):

| Page | Current title | Proposed |
|---|---|---|
| /mica-license/ | MiCA License (2026 Guide) - Consulting24 | MiCA License 2026: Cost, Capital Tiers, Timeline & EU Passport |
| /msb-license/ | MSB License (2026 Guide) - Consulting24 | MSB License 2026: Cost, Timeline & Requirements (USA & Canada) |
| /vasp-license/ | VASP License (2026 Guide) - Consulting24 | VASP License 2026: Cost, Requirements & Best Jurisdictions |
| /casp-license/ | CASP License (2026 Guide) - Consulting24 | CASP License 2026: MiCA Authorisation Cost, Capital & Timeline |
| /vara-license/ | VARA License (2026 Guide) - Consulting24 | VARA License Dubai 2026: Cost, Timeline & Requirements |
| /stablecoin-license/ | Stablecoin License (2026 Guide) - Consulting24 | Stablecoin Issuer License 2026: MiCA EMT/ART, Cost & Timeline |
| /mauritius-crypto-license/ | Mauritius Crypto License: FSC VAITOS 2026 Guide | Mauritius Crypto License 2026: VAITOS Cost, Capital & Timeline |
| /singapore-crypto-license/ | Singapore Crypto License: MAS DPT Licence Guide 2026 | Singapore Crypto License 2026: MAS DPT Cost, Capital & Timeline |
| /usa-crypto-license/ | USA Crypto License: State-by-State Licensing Guide 2026 | USA Crypto License 2026: Fastest & Cheapest States, Costs |
| /hong-kong-crypto-license/ | Hong Kong Crypto License: SFC VATP Guide 2026 \| Consulting24 | Hong Kong Crypto License 2026: SFC VATP Fees, Capital & Timeline |
| /costa-rica-crypto-license/ | Costa Rica Crypto License: No Dedicated Regime, Panama | Costa Rica Crypto License 2026: Rules, Banking & Casino Setup |
| /poland-crypto-license/ | Poland Crypto License 2026: MiCA CASP via KNF \| Consulting24 | Poland Crypto License 2026: KNF CASP Cost, Capital & Timeline |
| /cayman-islands-crypto-license/ | Cayman Islands Crypto License: 0% Tax, CIMA Regulated 2026 | Cayman Islands VASP License 2026: Cost, Presence Rules & Timeline |
| /seychelles-crypto-license/ | Seychelles Crypto License 2026 \| Low-Cost VASP Registration | Seychelles VASP License 2026: Cost, Requirements & Banking |
| /bvi-crypto-license/ | BVI Crypto License: VASP Registration 2026 \| Consulting24 | BVI Crypto License 2026: VASP Act Cost, Fund & Exchange Setup |

   Keep `pricing.md`, `llms.txt` and `chat.js` prices in sync where a title quotes a figure.
3. **Restore a real `/panama-crypto-license/` page** (self-canonical, EUR 6,000 new company + EUR 8,000 ready-made blocks, FAQ, links from the homepage, /jurisdictions/ and /cheapest-crypto-license/). Keep the homepage Panama-focused. This clears the Site Scan error and warning and gives Bing a slug that matches "panama crypto license" queries. Point the Blogger page `/p/crypto-license-in-panama-cost.html` (114 internal links) at it with a teaser.
4. **Blogger: teasers, not copies.** Change `scripts/gen_blogger_posts.py` so new posts publish the first ~300 words plus "Read the full guide on consulting24.co" linking the www twin; then use the Blogger API session to rewrite existing posts in batches of 25 per week, starting with the 117 URLs that have impressions (list in Bing → Search Performance → Pages, filter blog.). Do not noindex them yet: the www twins have almost no impressions, so removing Blogger first would lose the 22 clicks. Re-check monthly; once a www twin outranks its Blogger copy, set the copy to noindex.
5. **Redirect debris**: add Appendix A slugs from the 21 Sep plan plus /home, /crypto-licenses, /estonia-online-company, /estonia-e-residency-bank-accounts to `config/redirects.json` (targets: matching jurisdiction page or /estonia-company-registration/). Register /panama-crypto-license removal once step 3 ships.
6. **Site Scan warnings**: cap news titles at 65 chars in `scripts/news.py` (four live titles are 76–102 chars), shorten the chauffeur /hi/ title, add alt text to the 7 flagged images (export the list from Site Scan → Download all).
7. **Trailing-slash hygiene check** in `linkcheck.py`: fail the build on any internal `href="/slug"` without a trailing slash so the "URLs redirecting" bucket stops growing.
8. **Microsoft Clarity** in the template (engagement signal Bing uses; free heatmaps).

## 5. Phase 2 — weeks 3–6 (clicks, AI and authority)

1. **Answer-first blocks on the cited pages.** Copilot cites /msb-license/, /mica-license/, /vara-license/, /crypto-stablecoin-license-usa/ and /usa-crypto-license/ thousands of times but they earn single-digit clicks. Put a two-line direct answer (cost, capital, timeline) plus the WhatsApp CTA above the fold, and the same figures in the meta description.
2. **Pages for demand with no dedicated URL**: a `/crypto-banking/` hub for "crypto bank account / payment rails" queries (420 impressions across Panama, Seychelles, BVI, Bahrain, Costa Rica, Poland; today only www blog posts and Blogger copies answer them); a `/crypto-yield-staking-services-license/` page ("license to offer crypto yield services", 104 citations, 20% share); an "OTC desk cost by country" table on /crypto-otc-desk-license/ (Poland, Singapore, El Salvador, Seychelles queries with INR/USD cost intent); "cheapest / fastest US state" section on /usa-crypto-license/.
3. **Inlinks for www blog twins**: extend `scripts/blog_inlinks.py` so each jurisdiction hub links its guides (≥5 inlinks per post); today 268 of 333 posts have ≤2.
4. **Backlinks**: three sources are 72% of links and only ~10 domains are topical. Work the 3,300-domain list toward crypto/fintech/legal sites; target 25 topical referring domains by year end; vary targets beyond the homepage (593 of 783 links hit `/`).
5. **Bing Places** for Dubai and Panama offices; **PubHub** for the news desk once titles are fixed and there is one dated item per day.
6. **Translations**: 976 zh/es/ar pages indexed in a week with 13 impressions; no action beyond the H1 re-translation. Check in November whether /ar grows past 75 known URLs; if not, submit `sitemap-ar.xml` on its own in Bing → Sitemaps.

## 6. KPIs — 90 days (to 28 Dec 2026)

| KPI | Now | Target |
|---|---|---|
| Clicks, trailing 3M | 58 | 200 |
| Web CTR, trailing 3M | 2.4% | 4% |
| English landing pages with garbled H1 | 266 | 0 |
| Money pages with generic "(2026 Guide)" titles | 8 | 0 |
| Blogger URLs out-earning their www twin | 117 | <30 |
| Live pages Bing holds as 404 | 6 | 0 |
| http URLs crawled as canonical source | 2 | 0 |
| Panama landing page impressions (3M) | 3 | 100 |
| Site Scan errors + warnings | 12 | 0 |
| Topical referring domains | ~10 | 25 |
| Copilot citations, trailing 3M | 3,303 | ≥3,300 with a measurable click share |

Weekly (10 min): Search Performance clicks and web CTR, Site Explorer dead-link list, IndexNow/day. Monthly: re-run Site Scan, Blogger vs www twin impressions, backlink domain count.

## Appendix — how the data was pulled

Bing's internal endpoints (`/webmasters/api/searchperf/keyword/stats`, `/page/stats`, `/device/stats`, `/country/stats`, `/traffic/datestats`, `/aiperformance/*`, `/backlinks/pages`, `/backlinks/anchors`) accept POST bodies of `{SiteUrl, DateRange:{BeginTimeStamp,EndTimeStamp}, Pagination:{PageNum,PageSize≤500}, SortParameters:{SortField:"Impressions",SortOrder:"Desc"}}` with the CSRF token from `/webmasters/auth/token`; `traffic/datestats` needs `Filter:"All"`. Keyword and page tables cover the Web vertical only. Raw pull kept in the session scratchpad as `bwt_dump.json`.
