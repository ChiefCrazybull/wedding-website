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

   - Numbers must be contiguous (no gaps) starting from 2.
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

   (Note: trip3 has a pre-existing inconsistency - trip3_1.jpg instead of
   trip3_2.jpg. Don't repeat that pattern for new trips; start new trips'
   second photo at _2 like the others.)

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

6. ADDING A BRAND-NEW STATE (not just new photos of an existing one)
--------------------------------
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

7. ADDING A BRAND-NEW COUNTRY (not just new photos of an existing one)
--------------------------------
   a. Drop photos in Countries/New, name/compress/convert them as above
      using the new country's name as the base, then move them into
      Countries/.
   b. Add a new object to the COUNTRIES array in our-story.html:
        { name: "Peru", nameEs: "Perú", flag: "🇵🇪", images: ["Peru.jpg","Peru2.jpg"] },
      Countries use an emoji flag in the flag: field (NOT flagImg/a PNG -
      that's states only).
   c. Fill in nameEs (see section 8 below on Spanish).

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
