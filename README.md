# ⚖️ Martindale Lawyer Directory API: law firm data and US attorney profiles as structured JSON

> Search a practice area plus a city, no URL required, and get back attorney profiles with every bar admission and its year, law school, first admission year, firm and role, contact details, languages, and peer review stars.

**Actor page:** [apify.com/johnvc/lawyer-directory-api](https://apify.com/johnvc/lawyer-directory-api?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/lawyer-directory-api/input-schema](https://apify.com/johnvc/lawyer-directory-api/input-schema?fpr=9n7kx3)

Most legal data products are built on court records, so they can tell you what a lawyer has litigated but not what the lawyer is licensed to do. This API returns the credential layer instead. Every row carries `admissions`, the full list of jurisdictions with the year each one was granted, alongside `lawSchool` with degree and year, `firstAdmissionYear` as a clean integer, plus the practice areas, firm and role, office address, phones, and website that make up usable law firm data. This repo is a working Python client plus MCP install instructions for five assistants, so you can call it from a script or hand it to an agent.

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The Martindale Lawyer Directory API has two modes, and the one that makes it a search product rather than a URL hydrator is `search`. Put a practice area and a city in `keywords`, such as `medical malpractice Philadelphia`, set `maxResultsPerKeyword`, and you get one flat row per attorney with no URL to find first. That is the whole setup for the law firm data most teams want: `areasOfPractice`, `firm` with role, `address`, `phones`, `website`, `state`, and `firstAdmissionYear`. The credentials block is where it separates from a contact list: `admissions` lists every jurisdiction with its year, federal district and appeals courts included, so one live run in this repo returned an attorney with eleven admissions going back to 1991 next to one admitted in 2024. The second mode, `url`, takes up to 500 profile URLs you already hold, which is how you re-check a list on a schedule; `isln` is a stable identifier that survives firm moves, so rows join across runs and a changed `firm` field is a lateral move. One honest caveat: the source matches keywords across names, schools, and locations at once, so a search for `family law Austin` can return an attorney surnamed Austin in Wisconsin. Every row carries the `searchKeyword` it matched, and `state` plus `areasOfPractice` are the reliable filters after collection.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnisanerd/Apify-Martindale-Lawyer-Directory-API.git
   cd Apify-Martindale-Lawyer-Directory-API
   ```

2. **Install dependencies with UV**
   ```bash
   # Install UV if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Apify API key
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**
   ```bash
   uv run python martindale-lawyer-directory-api-example.py

   # Or pick a recipe:
   uv run python martindale-lawyer-directory-api-example.py --example credentials
   uv run python martindale-lawyer-directory-api-example.py --example watchlist
   ```

### Alternative: set the API key directly
```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python martindale-lawyer-directory-api-example.py
```

## Why Use This Martindale Lawyer Directory API?

**Legal professional search with no URL to find first.** Type what you are looking for. A practice area with a city, a bare location, a firm name, or an attorney name all work as free text in `keywords`, up to 20 per run. Competing tools want a directory URL or a fixed dropdown of state and practice-area filters before they will return anything.

**Bar admissions with the year, not just a state.** `admissions` is the field nobody else exports. It carries every listed jurisdiction with the year it was granted, including US District Courts, Courts of Appeals, and the Supreme Court. `firstAdmissionYear` comes back as an integer, so time in practice is one subtraction rather than a parsing job.

**Practice area search that filters cleanly afterwards.** `areasOfPractice` is a real array and `practiceCount` is an integer, so grouping a result set by practice area or filtering to attorneys with a single specialty takes one line of code.

**A stable join key.** `isln`, the International Standard Lawyer Number, identifies the individual attorney rather than the page. It survives firm moves and name changes, which is what makes re-running a watchlist and diffing the `firm` field meaningful.

**Cost you can predict.** The charge that matters is one event per profile pushed to the dataset, and `maxResultsPerKeyword` caps that at the source before anything is collected. A keyword that matches nothing returns no profile rows and so adds nothing to the bill. A two-profile test run costs about what two profiles cost, which is why every recipe in this repo asks for two. Current rates are on the [Actor page](https://apify.com/johnvc/lawyer-directory-api?fpr=9n7kx3).

## Features

### Core Capabilities
- Search mode: up to 20 free-text keywords per run, each with its own result cap
- URL mode: up to 500 attorney profile URLs per run for lists you already hold
- Credentials: `admissions` with a year per jurisdiction, `lawSchool` with degree and year, `university`, `firstAdmissionYear`
- Practice: `areasOfPractice` array, `practiceCount`, `firm` with role, `firmYearEstablished` where listed
- Contact: `address`, `mailingAddress`, `phones` array, `website`
- Person: `biography`, `about`, `languages`, `memberships`, `awards`, `photoUrl`, `videoCallPlatforms`
- Reputation: `peerReview` with `stars` and `reviewCount`
- Two ready-made dataset views in the Console: Attorneys overview and Credentials

### Data Quality
- One flat row per attorney, so CSV, Excel, and Google Sheets exports need no post-processing
- `searchKeyword` on every row, so fuzzy matches from the source are filterable rather than mysterious
- Zeros in `peerReview` are kept on purpose: no reviews yet is different from missing data
- Inputs that match nothing return a row with `result_type` of `error` and a plain-language `error_message` instead of vanishing
- `fetched_at` timestamps every row, so a scheduled run builds a dated history
- Fields the source profile does not list come back as `None`, so nothing is silently invented

## Recipes

Three recipes ship in `martindale-lawyer-directory-api-example.py`. Each keeps its input small on purpose, because billing is one charged event per profile returned.

### Practice area search in a city (default)

The general quick-start. One keyword, `medical malpractice Philadelphia`, two profiles back, and a wide slice of the output printed: practice areas, practice count, firm and role, state, address, phones, website, law school, university, first admission year, full admissions, languages, peer review, and the row summary.

Local: `uv run python martindale-lawyer-directory-api-example.py`

### Screen counsel by credentials

The credential layer on its own: law school with degree and year, undergraduate education, first admission year, years in practice computed from it, every listed admission with its jurisdiction and year, memberships, awards, languages, and peer review. A live run of this recipe returned one attorney with eleven admissions dating to 1991 and one admitted in 2024, which is the comparison the field exists for.

Local: `uv run python martindale-lawyer-directory-api-example.py --example credentials`

### Re-check a profile watchlist

URL mode against a fixed list of profile URLs. Prints firm and role, address, phones, admissions, and `fetched_at` for each. Because `isln` is stable across firm moves, running the same list on a schedule and diffing the `firm` field is how a lateral move shows up.

Local: `uv run python martindale-lawyer-directory-api-example.py --example watchlist`

**Schedule tip:** Save any of these inputs as a Task in the Apify Console and [schedule it](https://apify.com/johnvc/lawyer-directory-api?fpr=9n7kx3) to run weekly or monthly. Firm affiliations and new admissions move slowly, so a monthly refresh keeps a counsel list or a regional directory current without anyone remembering to press a button, and `fetched_at` dates each observation for you.

## Usage Examples

### Basic Example
```json
{
  "mode": "search",
  "keywords": ["medical malpractice Philadelphia"],
  "maxResultsPerKeyword": 2
}
```

### Advanced Example
```json
{
  "mode": "search",
  "keywords": [
    "medical malpractice Philadelphia",
    "employment law Chicago",
    "family law Austin",
    "Austin, TX"
  ],
  "maxResultsPerKeyword": 25
}
```

URL mode instead, for a list you already hold:

```json
{
  "mode": "url",
  "profileUrls": [
    "https://www.martindale.com/attorney/benjamin-john-simmons-168779542/",
    "https://www.martindale.com/attorney/marcus-aric-washington-168778862/"
  ]
}
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mode` | `str` | YES | `search` | `search` finds profiles from free-text keywords and needs no URL. `url` collects specific profile pages you already hold. |
| `keywords` | `list[str]` | in search mode | `["personal injury Houston"]` | Free-text searches: a practice area with a city, a location, a firm, or an attorney name. Up to 20 per run. |
| `maxResultsPerKeyword` | `int` | no | `25` | Profiles returned per keyword, from 1 to 2000. You are charged per profile returned, so this is also the cost control. |
| `profileUrls` | `list[str]` | in url mode | - | Specific attorney profile URLs, used in URL mode. Up to 500 per run. |

That is the whole input surface. There are no credential fields, so nothing sensitive can leak through a shared task configuration.

## Output Format

One row per attorney. `result_type` is `lawyer` for a collected profile and `error` for an input that matched nothing. Real output from a live run, biography trimmed for readability:

```json
{
  "result_type": "lawyer",
  "searchKeyword": "medical malpractice Philadelphia",
  "isln": "923120618",
  "name": "Benjamin John Simmons",
  "profileUrl": "https://www.martindale.com/attorney/benjamin-john-simmons-168779542/",
  "areasOfPractice": [
    "Birth And Neonatal Injury",
    "Medical Malpractice",
    "Catastrophic Injury",
    "Wrongful Death"
  ],
  "practiceCount": 4,
  "state": "PA",
  "address": "1845 Walnut Street, 18th Floor, Philadelphia, PA 19103",
  "mailingAddress": "1845 Walnut Street, 18th Floor, Philadelphia, PA 19103",
  "phones": ["215-602-4781", "215-714-2779", "(215) 545-8800"],
  "website": "https://mceldrewpurtell.com/",
  "firm": "Trial Lawyer at McEldrew Purtell",
  "lawSchool": "Drexel University Earle Mack School of Law, J.D., 2012",
  "university": "Commonwealth University",
  "firstAdmissionYear": 2012,
  "admissions": "2012, Pennsylvania; US District Court (Eastern & Middle Districts of PA); US Court of Appeals (Third Circuit)",
  "biography": "Ben Simmons is a Pennsylvania-licensed attorney whose practice focuses on medical malpractice...",
  "about": "Ben Simmons is a Pennsylvania-licensed attorney whose practice focuses on medical malpractice...",
  "photoUrl": "https://www.martindale.com/LBM_Images/Lawyers/lawyer-benjamin-simmons-photo-5213843.png",
  "videoCallPlatforms": ["Zoom", "Skype", "FaceTime"],
  "peerReview": { "stars": 0, "reviewCount": 0 },
  "summary": "Benjamin John Simmons, practicing Birth And Neonatal Injury, Medical Malpractice, Catastrophic Injury, at 1845 Walnut Street, 18th Floor, Philadelphia, PA 19103. Admitted 2012.",
  "fetched_at": "2026-08-09T00:59:01.751126+00:00"
}
```

An input that matches nothing returns this shape instead:

```json
{
  "result_type": "error",
  "sourceUrl": "https://www.martindale.com/attorney/does-not-exist-1/",
  "error_message": "No profiles matched this keyword.",
  "error_type": "CollectionError"
}
```

Not every profile lists every field. `languages`, `memberships`, `awards`, `mailingAddress`, `firmYearEstablished`, and `videoCallPlatforms` appear only when the source profile carries them, so check for `None` before you depend on one.

## People also search for

### How do I find attorneys by practice area?

Put the practice area in `keywords`, on its own or with a city, and run in `search` mode. Each row comes back with `areasOfPractice` as an array and `practiceCount` as an integer, so you can filter to attorneys who list that area and drop the incidental matches. Adding the city to the keyword narrows the result set, and `state` plus `address` confirm the location afterwards.

### How do law firms get clean data for legal reporting?

By pulling structured rows instead of copying pages. Every profile here arrives flat and typed: arrays for practice areas, phones, and awards, an integer for `firstAdmissionYear`, an object for `peerReview`. The Credentials view in the Apify Console lines law school, admissions, languages, and peer review side by side, and both views export to CSV, Excel, or Google Sheets with no reshaping.

### How do I build a list of attorneys by state?

Run one keyword per city in that state, up to 20 keywords in a single run, then filter the combined rows on `state`. Because the source matches keywords loosely across names and locations, filtering on the structured `state` field rather than trusting the keyword is what keeps the list clean. Raise `maxResultsPerKeyword` once a small test run looks right.

### How do I find lawyers who speak a specific language?

Collect first, then filter on `languages`. The field is returned as the source phrases it, for example "French and Spanish", and it is populated on some profiles and not others, so treat it as a filter over a collected set rather than a search input. Searching a language as a keyword is not reliable.

### How do I use law firm data from Python?

Clone this repo, `uv sync`, set `APIFY_API_TOKEN`, and run `uv run python martindale-lawyer-directory-api-example.py`. The client is `apify-client` 3.x, where `.call()` returns a typed `Run`, so results are read with `run.default_dataset_id`. See Quick Start and Recipes above.

### Can I use this with MCP or Claude?

Yes. Add the Actor as an MCP tool in [Claude Code](https://claude.ai/referral/uIlpa7nPLg) (free trial), [Claude Cowork](https://claude.ai/referral/uIlpa7nPLg) (free trial), Claude on the web, Cursor, or ChatGPT using the five install sections below, then ask in plain language, for example "find family law attorneys in Austin admitted before 2010".

### What is an ISLN?

The International Standard Lawyer Number, a stable identifier for an individual attorney. It survives firm moves and name changes, which makes it the right join key when you enrich an existing dataset or re-run a watchlist and want to know whether the row is the same person.

### Does it return client reviews?

No. Peer review stars and counts come back in `peerReview`, but client-review fields were empty on every profile tested, so they are deliberately not part of the output rather than present and always blank.

### Is this an official bar record?

No. It returns what an attorney's directory profile lists, which is why the admissions field is worth having and also why it is not a licensing verification of record. For an official status check, go to the relevant state bar or court. This is research and enrichment tooling, and if you plan any outreach you are responsible for the bar and solicitation rules that apply to you.

---

<!-- The five install sections below use the Actor's hosted MCP server URL:
     https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api -->

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Martindale Lawyer Directory API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Martindale Lawyer Directory API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Martindale Lawyer Directory API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/lawyer-directory-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api`, using OAuth when prompted.
5. Ask Claude to run the Martindale Lawyer Directory API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Martindale Lawyer Directory API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/lawyer-directory-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

## Related APIs

- [Google Scholar Case Law API](https://apify.com/johnvc/google-scholar-case-law?fpr=9n7kx3) for the case law these attorneys practice against
- [Owler Company Intelligence API](https://apify.com/johnvc/owler-company-api?fpr=9n7kx3) for the companies a firm's clients come from
- [LinkedIn Profile API](https://apify.com/johnvc/linkedin-profile-api?fpr=9n7kx3) for a professional-network view of the same person

---

## 🌐 About Alpha OSINT

This example repo is part of [Alpha OSINT](https://www.alphaosint.com), toolset of financial and operations data sources and APIs.
For support or requests for this actor, please start a ticket [directly on our support page](https://apify.com/johnvc/lawyer-directory-api/issues/open?fpr=9n7kx3).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Martindale Lawyer Directory API to power your legal research, counsel screening, and law firm data workflows with reliable, structured results.*

Last Updated: 2026.08.13
