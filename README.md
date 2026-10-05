# Spain University Outreach dashboard

Static site: `index.html` is the whole dashboard, `config.js` holds the Microsoft sign-in settings.
Every push to `main` is published to GitHub Pages within about a minute.

## One-time setup

### 1. Azure app registration (lets the page read your Outlook with your own sign-in)
In https://entra.microsoft.com → Applications → App registrations → **New registration**:
- Name: `Cludo Outreach Dashboard`
- Supported account types: *Accounts in this organizational directory only (Cludo)*
- Redirect URI: platform **Single-page application (SPA)**, value = the GitHub Pages URL of this site
  (e.g. `https://<user>.github.io/<repo>/`). Add `http://localhost:8080/` too if you want to test locally.
- After creating: **API permissions → Add a permission → Microsoft Graph → Delegated**:
  `User.Read`, `Mail.Read`, `Files.ReadWrite.AppFolder`. No admin consent is normally needed for these.
- Copy **Application (client) ID** and **Directory (tenant) ID** from the Overview page into `config.js`.

### 2. GitHub Pages
Repository → Settings → Pages → Source: **GitHub Actions**. The workflow in `.github/workflows/deploy.yml` does the rest.

## Updating the contact list or the email templates
The page is generated from the Apollo CSV by `gen.py` + `build.py` (kept in the Claude session);
ask Claude to regenerate `contacts.json` (then import it) or to change the templates in `index.html` and push.

## Where the contacts are
`index.html` contains **no contact data**. The first time you sign in, import the `contacts.json` file
Claude generated; the page stores it in a private app folder of your OneDrive and loads it from there on
every device after sign-in. To update the list, import a new `contacts.json` the same way.

## Where progress is stored
In the browser (localStorage) and, once signed in, in a private app folder of your OneDrive
(`Apps/Cludo Outreach Dashboard/outreach-state.json`), so it follows you across devices.
