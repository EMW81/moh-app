# Design Brief — Medal of Honor · Stories Browser
For Claude Design. Goal: a complete visual design mockup of this product. Everything
below is real content and real constraints; design with the actual data, not lorem ipsum.

## 1. What this is
A browser for Medal of Honor stories. Users filter ~3,536 official citations (pilot:
50) by 32 thematic categories in 4 groups, by conflict, branch, battle, and by fate
(survived / fell), plus text search — then read the full official citation. The
official cmohs.org database can't combine filters; discovery-by-theme is our entire
reason to exist. Ships as ONE static HTML file (no backend, no build step).

## 2. Audience & register
Primary: Darrin & Eric (creators) hunting for stories they haven't heard. Secondary:
veterans' families, teachers, speakers preparing remarks. The register is REVERENT
BUT ALIVE — a reading room, not a database admin panel; a memorial's dignity without
a memorial's stiffness. Absolutely no gamification language, no engagement-bait
patterns. These are records of people at the worst and greatest moments of their
lives; several users will be reading about their own relatives.

## 3. Surfaces to mock (the deliverable)
Design every one of these, desktop AND mobile (390px):
1. Main browse view — card grid + filter system, default state (50 stories)
2. Filter menu OPEN — the category menu specifically (32 options grouped under 4
   headers, each option with a live result count)
3. Actively filtered state — 2-3 filters stacked, active-filter chips visible,
   count bar updated, a saved-views row
4. Story detail view — full citation (see real lengths below), metadata, fate,
   place, links out
5. Map view — pins for filtered stories (approximate locations; Leaflet)
6. Empty state — filters matched nothing
7. Dark mode — at minimum the main browse view
8. Print sheet — one story printed by a teacher (this is a real use case)

## 4. Real content (design with these — includes edge cases)
Six real records follow, chosen deliberately: the SHORTEST citation in the set
(111 chars — Civil War-era brevity), long ones (up to 1,800 chars here; the longest
in the full set is Roy Benavidez at 4,587 chars), an apostrophe surname (O'Kane), a
"Dr." title (Mary Walker, the only woman), a fallen 19-year-old (McGinnis), and a
grenade-survivor (Carpenter). A card design must survive ALL of these; a detail view
must make a 4,600-character citation a pleasure to read.

```json
[
 {
  "id": "mary-e-walker",
  "name": "Walker, Dr., Mary E.",
  "rank": "Contract Acting Assistant Surgeon (civilian)",
  "branch": "U.S. Army",
  "unit": "",
  "conflict": "U.S. Civil War",
  "battle": null,
  "year": null,
  "action_date": null,
  "action_place": "Bull Run, VA 20109, USA",
  "coords": {
   "lat": 38,
   "lng": -77
  },
  "survived": true,
  "accredited_to": "Louisville, Ky.",
  "born": " Oswego County, N.Y.",
  "citation": "Battle of Bull Run, July 21, 1861; Patent Office Hospital, Washington, D.C., October 1861; Chattanooga, Tenn., following Battle of Chickomauga, September 1863; Prisoner of War, April 10, 1864-August 12, 1864, Richmond, Va.; Battle of Atlanta, September 1864\n\nWhereas it appears from official reports that Dr. Mary E. Walker, a graduate of medicine, \"has rendered valuable service to the Government, and her efforts have been earnest and untiring in a variety of ways,\" and that she was assigned to duty and served as an assistant surgeon in charge of female prisoners at Louisville, Ky., upon the recommendation of Major-Generals Sherman and Thomas, and faithfully served as contract surgeon in the service of the United States, and has devoted herself with much patriotic zeal to the sick and wounded soldiers, both in the field and hospitals, to the detriment of her own health, and has also endured hardships as a prisoner of war four months in a Southern prison while acting as contract surgeon; and Whereas by reason of her not being a commissioned officer in the military service, a brevet or honorary rank cannot, under existing laws, be conferred upon her; and\nWhereas in the opinion of the President an honorable recognition of her services and sufferings should be made:\nIt is ordered, That a testimonial thereof shall be hereby made and given to the said Dr. Mary E. Walker, and that the usual medal of honor for meritorious services be given her.\n\nGiven under my hand in the city of Washington, D.C., this 11th day of November, A.D. 1865.\n\nAndrew Johnson,\nPresident\n\n(Medal rescinded 1917 along with 910 others, restored by President Carter 10 June 1977.)",
  "category_hints": "Trailblazer; only female recipient; Healer",
  "categories": [
   "The Trailblazer / The First",
   "The Healer Under Fire",
   "Unbroken in Captivity",
   "Belated Justice / The Long Vindication"
  ],
  "photo_url": null,
  "cmohs_link": "http://www.cmohs.org/recipient-detail/1428/walker-dr-mary-e.php"
 },
 {
  "id": "charles-windolph",
  "name": "Windolph, Charles",
  "rank": "Private",
  "branch": "U.S. Army",
  "unit": "Company H, 7th U.S. Cavalry",
  "conflict": "Indian Campaigns",
  "battle": "Little Bighorn",
  "year": null,
  "action_date": null,
  "action_place": "Little Big Horn Bridge, Lodge Grass, MT 59050, USA",
  "coords": {
   "lat": 45,
   "lng": -107
  },
  "survived": true,
  "accredited_to": "Brooklyn, N.Y.",
  "born": " Germany",
  "citation": "With 3 comrades, during the entire engagement, courageously held a position that secured water for the command.",
  "category_hints": "Last Stand survivor - Reno Hill",
  "categories": [
   "The Last Stand",
   "Brotherhood / No One Left Behind"
  ],
  "photo_url": null,
  "cmohs_link": "http://www.cmohs.org/recipient-detail/1953/windolph-charles.php"
 },
 {
  "id": "douglas-albert-munro",
  "name": "Munro, Douglas Albert",
  "rank": "Signalman First Class",
  "branch": "U.S. Coast Guard",
  "unit": "",
  "conflict": "World War II",
  "battle": "Guadalcanal",
  "year": null,
  "action_date": null,
  "action_place": "Guadalcanal, Solomon Islands",
  "coords": {
   "lat": -9,
   "lng": 160
  },
  "survived": false,
  "accredited_to": "Washington",
  "born": " Vancouver, British Columbia",
  "citation": "For extraordinary heroism and conspicuous gallantry m action above and beyond the call of duty as Petty Officer in Charge of a group of 24 Higgins boats, engaged in the evacuation of a battalion of marines trapped by enemy Japanese forces at Point Cruz Guadalcanal, on 27 September 1942. After making preliminary plans for the evacuation of nearly 500 beleaguered marines, Munro, under constant strafing by enemy machineguns on the island, and at great risk of his life, daringly led 5 of his small craft toward the shore. As he closed the beach, he signaled the others to land, and then in order to draw the enemy's fire and protect the heavily loaded boats, he valiantly placed his craft with its 2 small guns as a shield between the beachhead and the Japanese. When the perilous task of evacuation was nearly completed, Munro was instantly killed by enemy fire, but his crew, 2 of whom were wounded, carried on until the last boat had loaded and cleared the beach. By his outstanding leadership, expert planning, and dauntless devotion to duty, he and his courageous comrades undoubtedly saved the lives of many who otherwise would have perished. He gallantly gave his life for his country.",
  "category_hints": "The Sea; Greater Love; only Coast Guard recipient",
  "categories": [
   "The Sea",
   "Greater Love",
   "The Rescue & Lifesaver",
   "The Fallen / Ultimate Sacrifice"
  ],
  "photo_url": null,
  "cmohs_link": "http://www.cmohs.org/recipient-detail/2905/munro-douglas-albert.php"
 },
 {
  "id": "richard-hetherington-okane",
  "name": "O'Kane, Richard Hetherington",
  "rank": "Commander",
  "branch": "U.S. Navy",
  "unit": "",
  "conflict": "World War II",
  "battle": null,
  "year": null,
  "action_date": null,
  "action_place": "Philippine Islands, Philippines",
  "coords": {
   "lat": 13,
   "lng": 122
  },
  "survived": true,
  "accredited_to": "New Hampshire",
  "born": " Dover, N.H.",
  "citation": "For conspicuous gallantry and intrepidity at the risk of his life above and beyond the call of duty as commanding officer of the U.S.S. Tang operating against 2 enemy Japanese convoys on 23 and 24 October 1944, during her fifth and last war patrol. Boldly maneuvering on the surface into the midst of a heavily escorted convoy, Comdr. O'Kane stood in the fusillade of bullets and shells from all directions to launch smashing hits on 3 tankers, coolly swung his ship to fire at a freighter and, in a split-second decision, shot out of the path of an onrushing transport, missing it by inches. Boxed in by blazing tankers, a freighter, transport, and several destroyers, he blasted 2 of the targets with his remaining torpedoes and, with pyrotechnics bursting on all sides, cleared the area. Twenty-four hours later, he again made contact with a heavily escorted convoy steaming to support the Leyte campaign with reinforcements and supplies and with crated planes piled high on each unit. In defiance of the enemy's relentless fire, he closed the concentration of ship and in quick succession sent 2 torpedoes each into the first and second transports and an adjacent tanker, finding his mark with each torpedo in a series of violent explosions at less than l,000-yard range. With ships bearing down from all sides, he charged the enemy at high speed, exploding the tanker in a burst of flame, smashing the transport dead in the water, and blasting the destroyer with a mighty roar which rocked the Tang from stem to stern. Expending his last 2 torpedoes into the remnants of a once powerful convoy before his own ship went down, Comdr. O'Kane, aided by his gallant command, achieved an illustrious record of heroism in combat, enhancing the finest traditions of the U.S. Naval Service.",
  "category_hints": "The Sea; Unbroken in Captivity - USS Tang",
  "categories": [
   "The Sea",
   "Unbroken in Captivity",
   "The Career Warrior"
  ],
  "photo_url": null,
  "cmohs_link": "http://www.cmohs.org/recipient-detail/2925/o-kane-richard-hetherington.php"
 },
 {
  "id": "ross-a-mcginnis",
  "name": "Mcginnis, Ross A.",
  "rank": "Private First Class",
  "branch": "U.S. Army",
  "unit": "Company C, 1st Battalion, 1st Infantry Division",
  "conflict": "War on Terrorism (Iraq)",
  "battle": null,
  "year": null,
  "action_date": null,
  "action_place": "Baghdad, Iraq",
  "coords": {
   "lat": 33,
   "lng": 44
  },
  "survived": false,
  "accredited_to": "June 14, 2004 in Pittsburgh, Pa.",
  "born": "June 14, 1987 in Meadville, Pa.",
  "citation": "For conspicuous gallantry and intrepidity at the risk of his life above and beyond the call of duty:\nPrivate First Class Ross A. McGinnis distinguished himself by acts of gallantry and intrepidity above and beyond the call of duty while serving as an M2 .50-caliber Machine Gunner, 1st Platoon, C Company, 1st Battalion, 26th Infantry Regiment, in connection with combat operations against an armed enemy in Adhamiyah, Northeast Baghdad, Iraq, on 4 December 2006.\n\nThat afternoon his platoon was conducting combat control operations in an effort to reduce and control sectarian violence in the area. While Private McGinnis was manning the M2 .50-caliber Machine Gun, a fragmentation grenade thrown by an insurgent fell through the gunner's hatch into the vehicle. Reacting quickly, he yelled \"grenade,\" allowing all four members of his crew to prepare for the grenade's blast. Then, rather than leaping from the gunner's hatch to safety, Private McGinnis made the courageous decision to protect his crew. In a selfless act of bravery, in which he was mortally wounded, Private McGinnis covered the live grenade, pinning it between his body and the vehicle and absorbing most of the explosion.\n\nPrivate McGinnis' gallant action directly saved four men from certain serious injury or death. Private First Class McGinnis' extraordinary heroism and selflessness at the cost of his own life, above and beyond the call of duty, are in keeping with the highest traditions of the military service and reflect great credit upon himself, his unit, and the United States Army.",
  "category_hints": "Body on the Grenade; The Boy - age 19",
  "categories": [
   "The Body on the Grenade",
   "The Boy (Too Young for This)",
   "Greater Love",
   "The Fallen / Ultimate Sacrifice"
  ],
  "photo_url": null,
  "cmohs_link": "http://www.cmohs.org/recipient-detail/3459/mcginnis-ross-a.php"
 },
 {
  "id": "william-kyle-carpenter",
  "name": "Carpenter, William Kyle",
  "rank": "Lance Corporal",
  "branch": "U.S. Marine Corps",
  "unit": "Company F, 2d Battalion, 9th Marines",
  "conflict": "War on Terrorism (Afghanistan)",
  "battle": null,
  "year": null,
  "action_date": null,
  "action_place": "Helmand, Afghanistan",
  "coords": {
   "lat": 31,
   "lng": 63
  },
  "survived": true,
  "accredited_to": "South Carolina",
  "born": "17 October, 1989, Flowood, MS",
  "citation": "For conspicuous gallantry and intrepidity at the risk of his life above and beyond the call of duty while serving as an Automatic Rifleman with Company F, 2d Battalion, 9th Marines, Regimental Combat Team 1, 1st Marine Division (Forward), 1 Marine Expeditionary Force (Forward), in Helmand Province, Afghanistan in support of Operation Enduring Freedom on 21 November 2010.  Lance Corporal Carpenter was a member of a platoon-sized coalition force, comprised of two reinforced Marine squads partnered with an Afghan National Army squad.  The platoon had established Patrol Base Dakota two days earlier in a small village in the Marjah District in order to disrupt enemy activity and provide security for the local Afghan population.  Lance Corporal Carpenter and a fellow Marine were manning a rooftop security position on the perimeter of Patrol Base Dakota when the enemy initiated a daylight attack with hand grenades, one of which landed inside their sandbagged position.  Without hesitation, and with complete disregard for his own safety, Lance Corporal Carpenter moved toward the grenade in an attempt to shield his fellow Marine from the deadly blast.  When the grenade detonated, his body absorbed the brunt of the blast, severely wounding him, but saving the life of his fellow Marine.  By his undaunted courage, bold fighting spirit, and unwavering devotion to duty in the face of almost certain death, Lance Corporal Carpenter reflected great credit upon himself and upheld the highest traditions of the Marine Corps and the United States Naval Service.",
  "category_hints": "Body on the Grenade - survived; Wounded Warrior; Epic Second Act",
  "categories": [
   "The Body on the Grenade",
   "Miraculous / Left for Dead",
   "The Wounded Warrior",
   "The Epic Second Act"
  ],
  "photo_url": null,
  "cmohs_link": "http://www.cmohs.org/recipient-detail/3511/carpenter-william-kyle.php"
 }
]
```

## 5. The 32 categories (exact names; counts from the real pilot data)
Four groups. Group identity should be visible in the UI (the current build assigns
each group an accent color used for thin bars/chips only, never fills — keep or
replace, but groups must be distinguishable):
- THE DEED (what earned it): The Assault (4) · The Last Stand (9) · The Body on the
  Grenade (2) · The Rescue & Lifesaver (8) · The Healer Under Fire (5) · The Colors
  (3) · One Against Many (8) · The Raid (2) · Wings (4) · The Sea (4) · Unbroken in
  Captivity (8) · The Rallying Point (4)
- THE PERSON (who they were): The Reluctant Warrior (2) · The New American /
  Immigrant's Debt (3) · The Trailblazer / The First (6) · The Boy (Too Young for
  This) (2) · The Career Warrior (5) · The Citizen-Soldier (1) · The Twice-Honored (2)
- THE SPIRIT (why it moves us): Religious / Faith-Driven (3) · Miraculous / Left for
  Dead (2) · Greater Love (9) · Redemption / The Second Birth (0 in pilot) ·
  Brotherhood / No One Left Behind (10) · Duty & Country (3) · The Cost of War /
  Lament (1)
- THE AFTERMATH (life beyond the medal): The Fallen / Ultimate Sacrifice (17) ·
  The Quiet Return (1) · Belated Justice / The Long Vindication (11) · The Forgotten
  Hero / Fall From Grace (1) · The Wounded Warrior (3) · The Epic Second Act (4)
Stories carry 1-4 categories each. Category names are Darrin's and must not be renamed.

## 6. Other filter dimensions (real values)
- Conflicts (12 in pilot, ~26 at full scale): U.S. Civil War (5) · Indian Campaigns
  (2) · Spanish-American War (1) · Boxer Rebellion (1) · Vera Cruz (1) · WWI (5) ·
  WWII (13) · Korean War (4) · Vietnam War (7) · Somalia (2) · Iraq (2) ·
  Afghanistan (7)
- Branches: U.S. Army (32) · U.S. Marine Corps (10) · U.S. Navy (6) · U.S. Coast
  Guard (1) · U.S. Air Force (1)
- Battles: 27 named, from Andrews' Raid and Gettysburg to Iwo Jima, Chosin
  Reservoir, Ia Drang, Mogadishu, COP Keating
- Fate: Survived (33) / Fell (17) — currently a gold star ★ marks the fallen (the
  Gold Star convention). Judge this: keep, refine, or replace with something better,
  but fate must be visible at card level without being morbid.
- Search: live, highlights matches inside citations.
- Count bar: always visible — "N of 50 stories shown · X survived · Y fell · year span."
- Saved views: named filter presets (e.g. "Marines · WWII · Fallen").

## 7. Hard constraints (not up for debate)
- Single HTML file; system-available or CDN fonts only; Leaflet is the only JS dep.
- Every color must resolve to a CSS custom-property token, with light/dark/auto
  themes and print styles. Deliver tokens, not just pictures.
- Mobile-first; must feel right at 390px. Must scale to 3,536 cards later
  (photo-less today; portrait photos likely added later — cards should anticipate
  an optional portrait without redesign).
- Citations render VERBATIM and in full in the detail view. Never truncated there,
  never editorialized.
- Accessibility floor: visible keyboard focus, honest contrast, reduced-motion.

## 8. Current v1 (exists; overthrow freely)
A working v1 uses: cool paper-white bg, Palatino-stack serif for display + citations,
bronze/gold + ribbon-blue accents (the medal + its ribbon), group accent colors
(gold/blue/violet/green), left accent bar on cards keyed to the story's primary
group, gold star for the fallen, double-rule masthead "Stories of Valor." Treat this
as a first draft, not a direction to match. The one thing v1 hasn't solved well:
32 categories is a LOT of chips — card-level category display risks chip soup. A
better idea for showing a story's themes at a glance would be the most valuable
single contribution of this design pass.

## 9. Deliverables checklist
1. Full mockup set per §3 (desktop + mobile)
2. Design tokens: complete palette (light + dark) as named CSS custom properties,
   type scale + families, spacing/radius/shadow scale
3. The category-visibility solution (§8) shown at card, filter-menu, and detail levels
4. A one-paragraph rationale connecting the visual language to the subject
Hand results back as images + a tokens block the implementing agent can paste in.
