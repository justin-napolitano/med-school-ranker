# Critical Review

## Finding 1: Simplifying could hide important uncertainty

Risk: Moving details out of the main view could make weak or missing data look stronger than it is.

Resolution: Keep data quality badges visible and put full details in collapsed sections, not removed.

## Finding 2: Internal dossier contracts are still used

Risk: Renaming everything from dossier to score card could break exports, local state, or tests.

Resolution: Keep internal names stable. Change visible language only.

## Finding 3: Profile page could become too decorative

Risk: A friendlier profile could lose decision utility.

Resolution: Keep the first viewport action-oriented: status, compare, rank, tier, MCAT, GPA, and costs.

## Finding 4: The Score Cards tab could duplicate Rankings

Risk: Score Cards may become another ranking table.

Resolution: Score Cards should focus on school profile review and status decisions. Rankings remains the primary sorting/filtering surface.

## Finding 5: Export controls still matter

Risk: Hiding export controls too deeply could make local-state persistence unclear.

Resolution: Keep export controls accessible in Data Details or a secondary action row, and keep local-state caveats concise.

## Finding 6: MCAT/GPA missingness can look like missing research when it may be approval policy

Risk: Blank MCAT/GPA values may make the user think no data exists, even when candidate source evidence exists but was not safely matched for canonical scoring.

Resolution: Label admissions-stat gaps as approved value missing, candidate value available but not safely matched, or no candidate value found. Do not change source normalization inside this UI slice.
