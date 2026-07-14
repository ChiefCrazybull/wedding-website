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
     existing files after it so there are no gaps or duplicates.
   - Match the state/country name exactly as it appears in the other files
     for that place (including spacing, e.g. "New York13.jpg" or
     "Vatican City3.jpg").

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

Example workflow (what was done for Connecticut in July 2026):
   - Two new source photos (Connecticut2.jpeg, Connecticut3.jpeg, ~1200x900,
     275-316 KB) were dropped in States/New.
   - They were compressed to JPEG quality 85 and 80 respectively (down to
     ~224-233 KB) and saved as .jpg.
   - The existing Connecticut2.jpg was renamed to Connecticut4.jpg to make
     room, then the two new files became Connecticut2.jpg and Connecticut3.jpg.
   - our-story.html's Connecticut entry was updated to list all four images.
