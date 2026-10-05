# Cludo Outreach Desk

A BDR outreach platform that runs as a Claude app: each BDR keeps their prospects in private campaigns,
works through a 3-email sequence (first contact, follow-up after N working days, last follow-up after M more),
and sends with one click from Outlook. Status is read from the mailbox, not from clicks.

## Files
- `platform.html` – the whole app, published as a Claude artifact with the `db`, `user` and `mcp` (Microsoft 365) capabilities.
  Everything a user does is stored in the artifact's database under `data/users/<id>/…`, private to that user.
- `tools/gen.py` – turns an Apollo contacts CSV into `contacts.json` for import: filters valid, not-yet-contacted
  contacts, maps job titles to the Spanish [área] phrase, builds the personalised first email per contact.
  Run with `python3 tools/gen.py` next to `apollo-contacts-export.csv` (never commit the CSV or the JSON).

## How a BDR uses it
1. Open the app from Claude (ask the owner to share it as Contributor).
2. Allow Outlook access once (Microsoft 365 connector, no admin consent needed).
3. Import prospects (`contacts.json` from `tools/gen.py`, or any CSV with first_name, last_name, email, organisation, title).
4. Work the queue: To contact → Follow-up due → Waiting → Replied → Finished. Press "Open in Outlook", send, and the
   sync picks up the sent email, replies and bounces.
5. Adjust templates, waiting days and holidays under "Sequence & settings"; create one campaign per list/language.

## Data
No prospect data lives in this repository. The `.gitignore` blocks CSV and JSON exports.
