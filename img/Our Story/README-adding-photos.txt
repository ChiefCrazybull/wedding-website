HOW TO ADD NEW PHOTOS TO THE "OUR STORY" MAP (States / Countries / Mexico)
============================================================================

This covers adding photos to the three galleries under img/Our Story/:
  - img/Our Story/States/      (US states picker)
  - img/Our Story/Countries/   (countries picker)
  - img/Our Story/Mexico/      (Mexico trips grid)
all of which are driven by data arrays in our-story.html.

Each of these three folders has a "New" subfolder (States/New,
Countries/New, Mexico/New) - drop freshly-taken photos there first, then
process and move them into the parent folder following the steps below.
The "New" folder itself should stay empty/untracked otherwise.

0. THE EASY WAY: photo-manager.bat
--------------------------------
   Double-click photo-manager.bat in this folder. It opens a small page in
   your browser where you pick Countries / Mexico / States, then the trip,
   and see that trip's photos in their display order. You can drag cards to
   reorder them, click the X to remove one, and drop new photos in to add
   them. Nothing on disk changes until you press Save, which shows you the
   exact list of renames first.

   Saving does everything the rest of this file describes by hand:
     - resizes and compresses new photos as in section 4, saving them .jpg
     - renumbers the whole trip to the scheme in sections 2 / 2a / 3
     - archives each new photo's untouched original in img_backup, and
       renames the existing originals there to stay in step
     - rewrites that entry's images: [...] array in our-story.html (section 5)
   Deleted photos are not erased - they move to
   img_backup/Our Story/<folder>/_deleted/ so you can get them back.

   It also creates brand-new entries. Each picker screen has a
   "+ New state / country / Mexico trip" button that asks for what that kind
   needs, then drops you on the normal photo screen:
     - State:   name in English and Spanish, a filename prefix, and its flag
                picked from a thumbnail grid of img/Our Story/States/Flags
                (or an emoji flag instead, for a territory with no PNG).
     - Country: name in English and Spanish. The flag emoji is filled in
                from the name automatically; you can override it.
     - Mexico:  numbered for you (the next trip after the highest existing
                one), so you only write the caption in both languages.
                There is an "insert" button for the dividing dot.
   Nothing is written until you add at least one photo and press Create, so
   there is never a half-made entry with an empty carousel. Creating also
   bumps the matching "and counting" badge (see section 5b), which is easy to
   forget by hand.

   Sections 6-8 below describe the same thing done manually, and are still
   worth reading to understand what the tool writes.

   Each card shows the photo's size and the date/time it was taken (read
   from the original in img_backup, since the site copies have no EXIF).

   Every gallery cell is landscape 4:3, so the tool highlights any photo that
   is not (portrait, square, too wide) - on the card, and as a count on the
   gallery and entry pickers. "Crop to 4:3" on a card opens an editor with a
   locked 4:3 box to move and resize. It crops from the full-size original in
   img_backup when that is the same shot, so the result is still 1400x1050.
   On Save the cropped photo replaces the site copy and the uncropped site
   copy is discarded (not moved to _deleted); the camera original in
   img_backup is left as it is. Any photo can be re-framed with the small
   scissors button, and "Undo crop" reverts before you save.

   The Commit button next to Save commits and pushes what you have saved.
   It is only enabled once there are saved changes and nothing unsaved on
   the page. It first shows exactly what will go up and lets you edit the
   commit message. It only ever commits our-story.html and the three gallery
   folders (not their New/ folders); any other changes in the repo are left
   for you to commit by hand. If GitHub has changes this computer does not
   have yet, the commit stays local and the button turns into Push - pull in
   GitHub Desktop, then press Push.

   There is an "Our Story Photos" shortcut on the desktop that runs
   photo-manager.bat, using _tool/photo-manager.ico as its icon.

   The tool lives in _tool/ (plain Python, no installs needed). The rest of
   this file documents the rules it follows, and is what to read if you are
   doing it by hand.

1. FILE FORMAT: must be .jpg
--------------------------------
   All photos in these folders are .jpg (lowercase extension). If a new
   photo comes off a phone/camera as .jpeg, .png, .heic, etc., convert/
   rename it to .jpg before adding it to the folder.

2. NAMING STRUCTURE - States and Countries
--------------------------------
   Files are named after the state/country, with no suffix on the first
   photo and an incrementing number starting at 2 for each additional photo:

       Connecticut.jpg, Connecticut2.jpg, Connecticut3.jpg, Connecticut4.jpg
       Florida.jpg, Florida2.jpg, ... Florida22.jpg
       Albania.jpg, Albania2.jpg, ... Albania7.jpg
       "Vatican City.jpg", "Vatican City2.jpg", ... "Vatican City10.jpg"

   - Numbers must be contiguous (no gaps) starting from 2. There is never a
     "1" - position 1 is the bare name. (Ireland used to have Ireland1.jpg
     alongside Ireland.jpg; it was renumbered in September 2026. As of then
     every state, country and trip follows this convention with no
     exceptions, so a stray number is a mistake, not precedent.)
   - If you insert a new photo in the middle of the sequence, renumber the
     existing files after it so there are no gaps or duplicates. If you're
     adding multiple new photos via a New folder and want to place them at
     specific spots, see section 2a for the exact renumbering rule.
   - Match the state/country name exactly as it appears in the other files
     for that place (including spacing, e.g. "New York13.jpg" or
     "Vatican City3.jpg").

2a. INSERTING NEW PHOTOS AT SPECIFIC POSITIONS (merging via the New folder)
--------------------------------
   When you drop new photos into a New folder, you can choose exactly
   where each one lands in the final order by naming it with the position
   number you want (position 1 has no number suffix, per section 2/3 -
   e.g. "Canada.jpg" is position 1).

   The existing photos then get renumbered to fill in the gaps around
   your new photos, keeping their own original relative order. Think of
   it as walking through final positions 1, 2, 3, ... in order:
     - If one of the new photos claims that position number, it goes there.
     - Otherwise, the next not-yet-placed EXISTING photo (in its original
       order) slides into that position.
   This means existing photos fill every gap left over - both between the
   new photos and after the last new photo - in their original order.

   Example: existing Canada.jpg, Canada2.jpg, Canada3.jpg, Canada4.jpg,
   Canada5.jpg (5 photos, positions 1-5). You drop four new photos in
   Countries/New named Canada.jpg, Canada2.jpg, Canada5.jpg, Canada7.jpg
   (claiming positions 1, 2, 5, 7). Final order:
     position 1 -> new Canada.jpg
     position 2 -> new Canada2.jpg
     position 3 -> old Canada.jpg   (renamed Canada3.jpg - 1st open gap)
     position 4 -> old Canada2.jpg  (renamed Canada4.jpg - 2nd open gap)
     position 5 -> new Canada5.jpg
     position 6 -> old Canada3.jpg  (renamed Canada6.jpg - 3rd open gap)
     position 7 -> new Canada7.jpg
     position 8 -> old Canada4.jpg  (renamed Canada8.jpg - continues after
                                      the last new photo)
     position 9 -> old Canada5.jpg  (renamed Canada9.jpg)

   This applies to States and Countries (name + number, per section 2) and
   to Mexico trips (filePrefix + underscore number, per section 3) - same
   gap-filling logic, just using that folder's naming format.

   As always, once the files are renamed/moved, update the images: [...]
   array in our-story.html to match the final order (see section 5).

3. NAMING STRUCTURE - Mexico
--------------------------------
   Mexico is organized by TRIP, not by place. Each trip has a filePrefix
   of "trip" + trip number, with no suffix on the first photo and an
   underscore + incrementing number starting at 2 for the rest:

       trip1.jpg, trip1_2.jpg
       trip6.jpg, trip6_2.jpg, ... trip6_15.jpg
       trip8.jpg, trip8_2.jpg, ... trip8_13.jpg

   Every trip follows this exactly - the second photo is always _2, never _1.
   (trip3 used to have trip3_1.jpg; it was renumbered in September 2026 so
   the whole folder is consistent. Don't reintroduce a _1.)

   - Adding photos to an EXISTING trip: continue the underscore numbering
     contiguously from the last photo in that trip (e.g. next photo after
     trip8_13.jpg is trip8_14.jpg).
   - Adding a NEW trip: use the next trip number after the highest existing
     one (currently trip8, so a new trip would be trip9, trip9_2, etc.).
     A new trip also needs a new entry added to the MEXICO_TRIPS array in
     our-story.html (see step 5) with a name/subtitle/date, not just files
     dropped in the folder.

4. SIZING / COMPRESSION PRINCIPLE
--------------------------------
   Existing photos across these folders average roughly 250-300 KB each
   (most fall between ~150 KB and ~400 KB), at typical resolutions of
   1400x1050 or 1200x900 (the large majority), occasionally other sizes.

   When adding a new photo:
   - Keep the original resolution if it's already close to 1400x1050 or
     1200x900 (no need to upscale/downscale unless it's dramatically off).
   - Compress with JPEG quality in the 80-90 range (adjust down in steps
     of ~5 until the file size lands in the ~200-300 KB ballpark). The
     goal is visual consistency and reasonable page-load size, not an
     exact byte-for-byte match.
   - Avoid photos under ~90 KB (visibly over-compressed) or over ~450 KB
     (unnecessarily large for a thumbnail-sized gallery image).

5. AFTER ADDING THE FILES
--------------------------------
   - States/Countries: update the images: [...] array for that state/
     country in our-story.html (search for its name) to include the new
     filename(s), in order.
   - Mexico: update the images: [...] array for that trip inside
     MEXICO_TRIPS in our-story.html, or add a whole new trip object (with
     name, nameEs, subtitle, subtitleEs, filePrefix, images) for a new trip.
   The picker/grid only shows images listed in these arrays - dropping a
   file into the folder alone does nothing.

5a. KEEP THE ARRAY IN DISPLAY ORDER, NOT JUST THE RIGHT FILENAMES
--------------------------------
   Carousels sort by the trailing number in the filename, so normally the
   array's own order does not matter. There is one exception, and it is easy
   to trip over.

   For COUNTRIES the sort strips the country's `name` off the front of the
   filename before reading the number (sortImages / trailingNum in
   our-story.html). For four countries the name does not match the files:

       name "United States"           -> files US.jpg, US2.jpg, ...
       name "United Kingdom"          -> files UK.jpg, UK2.jpg, ...
       name "Dominican Republic"      -> files DR.jpg, DR2.jpg, ...
       name "Bosnia &amp; Herzegovina" -> files "Bosnia and Herzegovina*.jpg"

   The strip fails, every photo gets sort number 0, and the carousel falls
   back to the order the array happens to be written in. Those four are
   correct today only because their arrays are already in order.

   So for these four, the array order IS the display order - reordering the
   files without reordering the array does nothing, and vice versa. States
   and Mexico are immune (they sort by filePrefix, which always matches).
   photo-manager.bat always rewrites the array in positional order, so using
   the tool keeps this right automatically.

   Note this is filename/array plumbing only: image order is identical in
   English and Spanish. The sort reads `name` / `filePrefix`, never `nameEs`
   - the only thing nameEs affects is where a state or country sits in the
   alphabetical list (see section 9).

5b. THE "AND COUNTING" BADGES ARE HARDCODED
--------------------------------
   Each of the three sections on the page shows a number above its grid:

       <h2 id="os-countries-h2">Countries Visited Together</h2>
       <div class="countries-count">44</div>

   There is one for Countries, one for Mexico and one for States, and each is
   a plain number typed into our-story.html - no JavaScript computes it, and
   applySpanish() only swaps the heading and the "and counting" label, not the
   figure. Each one currently equals the length of its array.

   So whenever you ADD OR REMOVE a state, country or trip, bump the matching
   badge too. Adding photos to an existing entry does not affect it.
   photo-manager.bat updates it for you, and warns on the picker screen if a
   badge and its array have already drifted apart.

6. ADDING A BRAND-NEW STATE (not just new photos of an existing one)
--------------------------------
   (photo-manager.bat does all of 6, 7 and 8 for you - see section 0. This is
   what it writes, and how to do it by hand.)

   a. Drop photos in States/New, name/compress/convert them as above using
      the new state's name as the base (e.g. "Ohio.jpg", "Ohio2.jpg"), then
      move them into States/.
   b. Add a flag icon PNG for the state into States/Flags/ (match the
      existing naming style, e.g. "ohio-flag-icon-256.png").
   c. Add a new object to the STATES array in our-story.html:
        { name: "Ohio", nameEs: "Ohio", flag: "", flagImg: "ohio-flag-icon-256.png",
          filePrefix: "Ohio", images: ["Ohio.jpg","Ohio2.jpg"] },
      States use flag: "" (empty) plus flagImg (a PNG), NOT an emoji flag.
      Fill in nameEs (see section 9 below on Spanish).
   d. The list re-sorts itself automatically (alphabetically by nameEs), so
      exact placement in the array doesn't matter, but keeping it roughly
      alphabetical makes the file easier to scan.
   e. Bump the States "and counting" badge (section 5b).
      A territory with no flag PNG can use an emoji flag instead, the way
      Puerto Rico does: flag: "&#127477;&#127479;" with flagImg: "".

7. ADDING A BRAND-NEW COUNTRY (not just new photos of an existing one)
--------------------------------
   a. Drop photos in Countries/New, name/compress/convert them as above
      using the new country's name as the base, then move them into
      Countries/.
   b. Add a new object to the COUNTRIES array in our-story.html:
        { name: "Peru", nameEs: "Perú", flag: "🇵🇪", images: ["Peru.jpg","Peru2.jpg"] },
      Countries use an emoji flag in the flag: field (NOT flagImg/a PNG -
      that's states only).
   c. Fill in nameEs (see section 9 below on Spanish).
   d. Bump the Countries "and counting" badge (section 5b).
   e. If the filenames don't start with the country's exact `name` (US, UK, DR
      and Bosnia are like this), also make sure the array is written in
      display order - see section 5a for why.

8. ADDING A BRAND-NEW MEXICO TRIP
--------------------------------
   a. Pick the next trip number after the highest existing one (currently
      trip8, so a new trip is trip9). Drop photos in Mexico/New, name them
      trip9.jpg, trip9_2.jpg, trip9_3.jpg, ... (see section 3), compress
      as above, then move them into Mexico/.
   b. Add a new object to the MEXICO_TRIPS array in our-story.html:
        { name: "Trip 9", nameEs: "Viaje 9",
          subtitle:   "Short description &middot; Location &middot; Month Year",
          subtitleEs: "Descripcion breve &middot; Lugar &middot; Mes Ano",
          filePrefix: "trip9",
          images: ["trip9.jpg","trip9_2.jpg","trip9_3.jpg"] },
      Trips are shown in array order (not auto-sorted), so add the new
      trip at the end (or wherever it belongs chronologically).
   c. Bump the Mexico "and counting" badge (section 5b).
      Note trip10 does not collide with trip1: extra photos always carry the
      underscore (trip10_2.jpg), which is what keeps the two apart.

9. SPANISH VERSION - the site is bilingual
--------------------------------
   The site has an English and a Spanish version, toggled at runtime via
   window.siteLang ('spanish' or otherwise). There is no separate
   translation file for this gallery data - every state, country, and trip
   entry carries its own Spanish text inline, so ANY time you add or edit
   an entry you must fill in the Spanish fields too, not just the English
   ones:
     - name / nameEs           -> state and country display names
                                  (e.g. name: "Belgium", nameEs: "Belgica" or "B&eacute;lgica")
     - name / nameEs           -> Mexico trip names (e.g. "Trip 9" / "Viaje 9")
     - subtitle / subtitleEs   -> Mexico trip date/location captions
   Notes:
     - Accented characters can be written as literal UTF-8 (a, e, i, o, u,
       n) or as HTML entities (&iacute;, &oacute;, etc.) - both are used
       in the existing data, match whichever style is already nearby.
     - If a name is the same in both languages (e.g. "Guatemala"), just
       repeat it in nameEs - don't leave it blank, since sorting and
       display both read from nameEs specifically when the site is in
       Spanish mode.
     - The States/Countries lists are sorted alphabetically by nameEs (via
       localeCompare with the 'es' locale), so a new entry's placement in
       the array doesn't matter, but its nameEs value does affect where it
       appears in the Spanish-sorted list.
     - Mexico trips are NOT auto-sorted - they display in the array's
       order regardless of language.

Example workflow (what was done for Connecticut in July 2026):
   - Two new source photos (Connecticut2.jpeg, Connecticut3.jpeg, ~1200x900,
     275-316 KB) were dropped in States/New.
   - They were compressed to JPEG quality 85 and 80 respectively (down to
     ~224-233 KB) and saved as .jpg.
   - The existing Connecticut2.jpg was renamed to Connecticut4.jpg to make
     room, then the two new files became Connecticut2.jpg and Connecticut3.jpg.
   - our-story.html's Connecticut entry was updated to list all four images.
