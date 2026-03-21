# EthicsMosaic Download Report — 2026-03-21

## Final Results

| Metric | Value |
|--------|-------|
| Total URLs | 791 |
| Successful | 643 (81.3%) |
| Failed | 148 |
| PDFs downloaded | 297 |
| HTML downloaded | 346 |
| Files on disk | 298 PDF + 346 HTML = 644 |

## Error Breakdown

| Error Type | Count | Description |
|-----------|-------|-------------|
| dead_link | 74 | HTTP 404 — URL no longer exists |
| blocked | 51 | HTTP 403 — bot protection |
| http_error | 13 | HTTP 302/307/401/500/503 |
| connection_error | 8 | SSL/DNS/TLS failures |
| timeout | 2 | Server did not respond in time |

## Methodology

- **Wave 1:** 8 parallel agents, 1.5s politeness delay, 30s timeout
- **Wave 2:** 2 retry agents (timeout retry + blocked retry), 2s delay, 30s timeout
- **PDF validation:** %PDF- magic byte check, 500-byte minimum size
- **HTML upgrade:** Embedded PDF link extraction from HTML pages
- **Safety:** Invalid downloads moved to RECYCLE-BIN/, never deleted

## Bot-Blocked URLs (51) — Manual Browser Download Recommended

| # | Organization | URL |
|---|-------------|-----|
| 5 | American Veterinary Medical Association (AVMA) | https://www.avma.org/resources-tools/avma-policies/principles-veterinary-medical-ethics-avma |
| 15 | International Society of Arboriculture (ISA) | https://www.isa-arbor.com/Credentials/ISA-Ethics-and-Integrity/Code-of-Ethics |
| 17 | American Fisheries Society (AFS) | https://fisheries.org/about/governance/standards-of-professional-conduct/ |
| 36 | American Institute of Professional Geologists (AIP | https://aipg.org/page/Ethics |
| 46 | Institute of Electrical and Electronics Engineers  | https://www.ieee.org/about/corporate/governance/p7-8 |
| 74 | National Electrical Contractors Association (NECA) | https://www.necanet.org/ |
| 196 | Retail Council of Canada (RCC) | https://www.retailcouncil.org/responsible-sourcing-2/ |
| 203 | Air Line Pilots Association (ALPA) | https://www.alpa.org/about/code-of-ethics |
| 223 | SAG-AFTRA (Screen Actors Guild-American Federation | https://www.sagaftra.org/contracts-industry-resources/workplace-harassment-prevention/four-pillars-change-initiative/code |
| 237 | Association for Computing Machinery (ACM) | https://www.acm.org/code-of-ethics |
| 241 | International Federation of Library Associations a | https://www.ifla.org/publications/ifla-code-of-ethics-for-librarians-and-other-information-workers-full-version/ |
| 263 | Securities and Exchange Commission (SEC) | https://www.sec.gov/about/ethics |
| 315 | BOMA International | https://www.boma.org/BOMA/About/BOMA_Code_of_Ethics.aspx |
| 327 | American Bar Association (ABA) | https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/ |
| 335 | American Psychological Association (APA) | https://www.apa.org/ethics/code |
| 340 | Project Management Institute (PMI) | https://www.pmi.org/about/ethics |
| 347 | AIGA (The Professional Association for Design) | https://www.aiga.org/resources/aiga-standards-of-professional-practice |
| 352 | National Association of Tax Professionals (NATP) | https://www.natptax.com/governance/standards-of-professional-conduct/ |
| 395 | American Occupational Therapy Association (AOTA) | https://research.aota.org/ajot/article/doi/10.5014/ajot.2025.79S302/28485/AOTA-2025-Occupational-Therapy-Code-of-Ethics |
| 427 | The Joint Commission | https://www.jointcommission.org/en-us/standards |
| 432 | American Academy of Pediatrics (AAP) | https://publications.aap.org/collection/686/Ethics-Bioethics |
| 434 | SAG-AFTRA (Screen Actors Guild - American Federati | https://www.sagaftra.org/sag-aftra-code-conduct |
| 463 | National Association of Professional Pet Sitters ( | https://petsitters.org/page/AboutUs_Tab |
| 497 | American Association of Code Enforcement (AACE) | https://www.aace1.org/page/codeofethics |
| 500 | Organisation for Economic Co-operation and Develop | https://www.oecd.org/gov/ethics/recommendation-public-integrity/ |
| 509 | Chartered Management Institute (CMI) | https://www.managers.org.uk/about-cmi/governance/policies/code-of-conduct/ |
| 513 | U.S. Securities and Exchange Commission (SEC) | https://www.sec.gov/rules-regulations/2003/03/disclosure-required-sections-406-407-sarbanes-oxley-act-2002 |
| 519 | Association for Talent Development (ATD) | https://www.td.org/about/vision-mission-code-of-ethics |
| 552 | IEEE Computer Society / ACM (Joint) | https://www.acm.org/code-of-ethics/software-engineering-code |
| 554 | Data Science Association | https://www.datascienceassn.org/code-of-conduct.html |
| 560 | SIAM (Society for Industrial and Applied Mathemati | https://www.siam.org/about-us/ |
| 565 | National Society of Professional Surveyors (NSPS) | https://nsps.us.com/page/CreedandCanons |
| 572 | AMPP (Association for Materials Protection and Per | https://store.ampp.org/ethics-for-the-corrosion-professional |
| 589 | American Physical Society (APS) | https://www.aps.org/about/governance/statements/ethics |
| 590 | American Physical Society (APS) | https://www.aps.org/about/governance/policies-procedures/code-of-conduct |
| 591 | American Geophysical Union (AGU) | https://www.agu.org/learn-about-agu/about-agu/ethics |
| 622 | American Bar Association (ABA) | https://www.americanbar.org/groups/professional_responsibility/publications/model_code_of_judicial_conduct/ |
| 629 | American Bar Association (ABA) / American Arbitrat | https://www.americanbar.org/groups/dispute_resolution/resources/tools/ethics/ |
| 633 | American Land Title Association (ALTA) | https://njlta.org/page/AmericanLandTitle |
| 637 | NALS — National Association for Legal Support Prof | https://www.nals.org/page/NALSCodeofEthics |
| 650 | SAG-AFTRA | https://www.sagaftra.org/contracts-industry-resources/agents-managers/managers/code-ethics-conduct |
| 661 | International Confederation of Midwives (ICM) | https://internationalmidwives.org/resources/international-code-of-ethics-for-midwives/ |
| 663 | National Association of EMS Physicians (NAEMSP) | https://www.tandfonline.com/doi/full/10.1080/10903127.2020.1808747 |
| 668 | National Certification Commission for Acupuncture  | https://www.nccaom.org/about-nccaom/ |
| 695 | International Foundation for Protection Officers ( | https://ifpo.org/ |
| 707 | International Association of Pet Cemeteries and Cr | https://www.iaopc.com/page/code-of-ethics |
| 748 | The Minerals, Metals & Materials Society (TMS) | https://www.tms.org/About |
| 749 | American Society for Quality (ASQ) | https://asq.org/about-asq/code-of-ethics |
| 754 | Refrigerating Engineers and Technicians Associatio | https://reta.com/page/aboutreta |
| 775 | Nautilus International / RMT / UK Chamber of Shipp | https://www.ukchamberofshipping.com/latest/code-conduct-merchant-navy/ |
| 789 | U.S. Space Force | https://www.spaceforce.mil/News/Article/2782534/cso-unveils-guardian-ideal-space-force-values-at-afa/ |

## Dead Links (74) — URL Needs Updating or Content Removed

| # | Organization | URL |
|---|-------------|-----|
| 18 | The Wildlife Society (TWS) | https://wildlife.org/wp-content/uploads/2024/06/20240324_Code_of_Ethics.pdf |
| 38 | Certified Mine Safety Professional (CMSP) | https://www.smecmsp.org/index.cfm/codeofconduct/ |
| 61 | Chartered Institute of Building (CIOB) | https://www.ciob.org/ethics-respect-people |
| 142 | American Institute of Steel Construction (AISC) | https://www.aisc.org/about-us/code-of-conduct/ |
| 239 | Association of Information Technology Professional | https://aitp-ncfl.org/home/about-2/aitp-code-of-ethics/ |
| 246 | Federal Reserve Banks | https://www.federalreserve.gov/aboutthefed/files/code-of-conduct.pdf |
| 247 | Bank for International Settlements (BIS) | https://www.bis.org/about/code_of_conduct.htm |
| 248 | American Bankers Association (ABA) | https://www.aba.com/about-us/code-of-ethics |
| 249 | Independent Community Bankers of America (ICBA) | https://www.icba.org/about/governance/code-of-ethics |
| 250 | Mortgage Bankers Association (MBA) | https://www.mba.org/about-mba/code-of-conduct |
| 251 | National Association of Mortgage Brokers (NAMB) | https://www.namb.org/code-of-ethics |
| 254 | ACA International | https://www.acainternational.org/about/code-of-ethics |
| 256 | Loan Syndications and Trading Association (LSTA) | https://www.lsta.org/content/code-of-conduct/ |
| 257 | Secured Finance Network (SFNet) | https://www.sfnet.com/about/code-of-ethics |
| 258 | International Factoring Association (IFA) | https://www.factoring.org/code-of-ethics |
| 259 | Conference of State Bank Supervisors (CSBS) | https://www.csbs.org/code-ethics |
| 260 | CFA Institute | https://www.cfainstitute.org/ethics-standards/ethics/code-of-ethics-standards-of-professional-conduct |
| 265 | Financial Planning Association (FPA) | https://www.financialplanningassociation.org/ethics |
| 266 | National Association of Personal Financial Advisor | https://www.napfa.org/financial-planning/fiduciary-oath |
| 267 | Chartered Alternative Investment Analyst Associati | https://caia.org/code-of-conduct |
| 268 | Global Association of Risk Professionals (GARP) | https://www.garp.org/code-conduct |
| 271 | Investment Adviser Association (IAA) | https://www.investmentadviser.org/standards-of-practice/ |
| 272 | CFA Institute | https://www.cfainstitute.org/ethics-standards/ethics/standards-practice-handbook |
| 273 | Chartered Institute for Securities & Investment (C | https://www.cisi.org/cisiweb2/cisi-website/membership/code-of-conduct |
| 274 | Investment Company Institute (ICI) | https://www.ici.org/policy/governance |
| 276 | Commodity Futures Trading Commission (CFTC) | https://www.cftc.gov/About/Governance/Ethics |
| 277 | Investments & Wealth Institute (formerly IMCA) | https://investmentsandwealth.org/about/code-of-professional-responsibility |
| 280 | Alternative Investment Management Association (AIM | https://www.aima.org/sound-practices/hedge-fund-governance.html |
| 283 | The Institutes (CPCU) | https://www.theinstitutes.org/guide/cpcu-code-professional-conduct |
| 284 | National Association of Insurance and Financial Ad | https://www.naifa.org/about/code-of-ethics |
| 286 | Casualty Actuarial Society (CAS) | https://www.casact.org/professionalism/code-professional-ethics |
| 290 | NABIP (formerly NAHU) | https://nabip.org/who-we-are/code-of-ethics |
| 291 | Insurance Institute of Canada (IIC) | https://www.insuranceinstitute.ca/en/professional-development/code-of-ethics |
| 292 | International Association of Insurance Supervisors | https://www.iaisweb.org/activities-topics/standards-and-guidance/insurance-core-principles/ |
| 293 | National Association of Mutual Insurance Companies | https://www.namic.org/about/code-of-conduct |
| 294 | American College of Trust and Estate Counsel (ACTE | https://www.actec.org/resources/standards-of-professional-responsibility/ |
| 295 | Institute of Management Accountants (IMA) | https://www.imanet.org/advocacy/ima-statement-of-ethical-professional-practice |
| 304 | NAR | https://www.nar.realtor/about-nar/governing-documents/the-realtor-pledge |
| 309 | CCIM Institute | https://www.ccim.com/about-ccim/code-of-ethics/ |
| 311 | National Apartment Association (NAA) | https://www.naahq.org/about/code-of-ethics |
| 312 | Counselors of Real Estate (CRE) | https://cre.org/about-cre/code-of-ethics/ |
| 313 | ICSC (Innovating Commerce Serving Communities) | https://www.icsc.com/about/code-of-professional-standards |
| 314 | International Facility Management Association (IFM | https://www.ifma.org/about/about-ifma/code-of-ethics/ |
| 316 | Real Estate Board of New York (REBNY) | https://www.rebny.com/about-rebny/code-of-ethics/ |
| 324 | Licensing International (formerly LIMA) | https://www.licensinginternational.org/about/code-of-business-practices/ |
| 325 | International Trademark Association (INTA) | https://www.inta.org/about/code-of-conduct/ |
| 326 | International Franchise Association (IFA) | https://www.franchise.org/code-of-ethics |
| 360 | American Association of Professional Landmen (AAPL | https://www.landman.org/about/governance/code-of-ethics-and-standards-of-practice |
| 414 | American Podiatric Medical Association (APMA) | https://www.apma.org/files/Code%20of%20Ethics_FINAL_1669749709677_2.pdf |
| 437 | National Collegiate Athletic Association (NCAA) | https://www.ncaa.org/sports/2016/1/26/ethics.aspx |
| 438 | North American Society for Sport Management (NASSM | https://nassm.org/node/111 |
| 439 | United States Olympic & Paralympic Committee (USOP | https://www.usopc.org/code-of-conduct |
| 451 | Hospitality Financial and Technology Professionals | https://www.hftp.org/about/code-of-ethics/ |
| 454 | Association of Nutrition & Foodservice Professiona | https://www.anfponline.org/about-anfp/code-of-ethics |
| 457 | Electronic Technicians Association International ( | https://www.eta-i.org/ethics.html |
| 458 | National Association of Home Builders (NAHB) | https://www.nahb.org/about/code-of-ethics |
| 462 | International Cemetery, Cremation and Funeral Asso | https://www.iccfa.com/about/code-of-ethics/ |
| 469 | Council on Foundations | https://cof.org/content/principles-and-practices |
| 473 | National Domestic Workers Alliance (NDWA) | https://www.domesticworkers.org/bill-of-rights/ |
| 480 | National League of Cities (NLC) | https://www.nlc.org/resource/code-of-ethics/ |
| 490 | National Association of State Workforce Agencies ( | https://www.naswa.org/about/mission |
| 492 | International Public Management Association for Hu | https://www.ipma-hr.org/about/code-of-ethics |
| 495 | Institute of Environmental Management and Assessme | https://www.iema.net/membership/code-of-practice |
| 496 | National Association of Housing and Redevelopment  | https://www.nahro.org/about/code-of-professional-conduct-and-ethics/ |
| 564 | American Society of Landscape Architects (ASLA) | https://www.asla.org/ContentDetail.aspx?id=4276 |
| 615 | Association for Multicultural Counseling and Devel | https://www.counseling.org/resources/competencies/multicultural-and-social-justice-counseling-competencies |
| 687 | National Volunteer Fire Council (NVFC) | https://www.nvfc.org/wp-content/uploads/2017/05/NVFC-Member-Code-of-Conduct.pdf |
| 701 | United States Bartenders' Guild (USBG) | https://www.usbg.org/about1/usbg-policies/member-code-of-conduct2 |
| 712 | Professional Beauty Association (PBA) | http://probeauty.org/docs/pledge/code_of_ethics_salon_spa.pdf |
| 723 | American Society of Travel Advisors (ASTA) | https://www.asta.org/about/content.cfm?ItemNumber=745 |
| 727 | National Auctioneers Association (NAA) | https://auctioneers.org/NAA/About%20NAA/Code-of-Ethics/NAA/About-NAA/Governance-And-Financials/Code-of-Ethics.aspx |
| 736 | Society for Range Management (SRM) | https://rangelands.org/about-3/ |
| 741 | United Brotherhood of Carpenters and Joiners (UBC) | https://albertacarpenters.com/home/members/bylaws-trade-rules-agreements/ubc-in-alberta-code-of-conduct/ |
| 757 | Aviation Code of Conduct Permanent Board | https://www.secureav.com/AMTMCC-v1.0.htm |

## Other Failures (23)

| # | Organization | Error | URL |
|---|-------------|-------|-----|
| 47 | Institute of Electrical and Electronics  | pdf_failed:not_a_pdf html_fallback: | https://www.ieee.org/content/dam/ieee-org/ieee/web/org/about/ieee |
| 72 | International Union of Operating Enginee | http_302 | https://www.iuoe.org/ |
| 158 | The Toy Association | http_500 | https://www.toyassociation.org/ta/about-us/member-code-of-conduct |
| 174 | National Independent Automobile Dealers  | url_error_timed out | https://niada.com/ |
| 221 | Association of Couriers and Messageries  | url_error_[SSL: CERTIFICATE_VERIFY_ | https://www.acmq.net/en/about/ |
| 233 | American Society of News Editors (ASNE) | url_error_[SSL: CERTIFICATE_VERIFY_ | https://accountablejournalism.org/ethics-codes/american-society-o |
| 234 | CTIA - The Wireless Association | url_error_[SSL: CERTIFICATE_VERIFY_ | https://www.ctia.org/the-wireless-industry/industry-commitments/c |
| 244 | Special Libraries Association (SLA) | url_error_[SSL: CERTIFICATE_VERIFY_ | https://sla.org/page/sla-professional-ethics-guidelines/ |
| 301 | DCIIA | url_error_timed out | https://www.dciia.org/ |
| 363 | Ethics & Compliance Initiative (ECI) | url_error_[Errno 8] nodename nor se | https://www.ethics.org/ |
| 455 | National Institute for Automotive Servic | url_error_[SSL: CERTIFICATE_VERIFY_ | https://www.ase.com |
| 489 | National District Attorneys Association  | pdf_failed:curl_error_56 html_fallb | https://ndaa.org/wp-content/uploads/National-Prosecution-Standard |
| 504 | U.S. Department of Defense (DoD) | pdf_failed:curl_error_56 html_fallb | https://dodsoco.ogc.osd.mil/Portals/102/Documents/Issuances/JER%2 |
| 507 | Intelligence Community (IC) | pdf_failed:curl_error_56 html_fallb | https://www.dni.gov/files/documents/CLPO/Principles_of_Profession |
| 580 | Ecological Society of America (ESA) | http_307 | https://esa.org/about/code-of-ethics/ |
| 610 | International Association of Marriage an | http_503 | https://www.iamfconline.org/public/department3.cfm |
| 660 | American Academy of Physician Associates | http_401 | https://www.aapa.org/career-central/practice-tools/ethical-guidel |
| 730 | American Payroll Association (APA / Payr | url_error_[Errno 8] nodename nor se | https://denverapa.org/content.php?page=APA_Code_of_Ethics |
| 738 | International Association of Bridge, Str | http_401 | https://www.ironworkers.org/who-we-are/ironworkers'-standards-of- |
| 780 | U.S. Department of Defense | pdf_failed:curl_error_56 html_fallb | https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodd/55 |
| 783 | U.S. Navy | url_error_[SSL: CERTIFICATE_VERIFY_ | https://www.history.navy.mil/browse-by-topic/heritage/customs-and |
| 785 | U.S. Air Force | pdf_failed:curl_error_56 html_fallb | https://static.e-publishing.af.mil/production/1/af_cc/publication |
| 791 | U.S. Department of Defense | pdf_failed:curl_error_56 html_fallb | https://ogc.osd.mil/Portals/99/Law%20of%20War/Practice%20Document |