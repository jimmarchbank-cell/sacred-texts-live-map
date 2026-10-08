# Sacred Texts Worldwide public map

Copies only the aggregate participation image already published in the registration form. No participant records, Google credentials, or private Apps Script source are used.

The workflow runs daily at 12:47 UTC (7:47 a.m. Central daylight time / 6:47 a.m. Central standard time), and can also be run manually from Actions. GitHub schedules can be delayed.

The approved 740 × 511 map is preserved, including historical results and the green current-season totals. Validation rejects missing, ambiguous, or incorrectly sized images. A failed refresh leaves the previous Pages deployment available.

The public website files are in `public/`. `heat-map.png` keeps its filename across updates; `updated.json` records the last successful copy, not when the registration totals last changed. Each successful refresh is committed for recovery and ongoing repository activity.

To refresh manually: Actions → Refresh public heat map → Run workflow.
