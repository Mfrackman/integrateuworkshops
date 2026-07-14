# Your Morning Intel Scout

Every morning at 7 AM Eastern, this repository reads three news feeds you
choose, asks Claude (an AI) to find the opportunities worth a phone call
for YOUR business, and emails you a short brief. You are about to make
your own copy and turn it on. Total editing required: two files, two
secrets, one button.

**Before class (from the prep video):** you need three free accounts:
a GitHub account, an Anthropic account with an API key and about 5
dollars of credit (console.anthropic.com), and a Resend account with an
API key (resend.com). Keep both keys somewhere you can copy from.

---

## Step 1: Open your fork in the web editor

1. Make sure you are looking at YOUR copy of this repository (the fork
   you created; the address bar should show your username, not
   hfscdogg).
2. Press the **period key** ( . ) on your keyboard. GitHub opens the
   web editor: it looks like a programmer's tool, but you will only
   touch two files. Nothing installs on your computer.
3. You can see the file list on the left. That's the whole project.

## Step 2: Pick your inputs

1. In the file list, click **config.yml**.
2. You'll see three feed lines under `feeds:`. They come pre-loaded with
   three national construction feeds, so the scout works even if you
   change nothing.
3. To make it local, replace any of the three addresses with an RSS
   feed from your city: your business journal, local news site, or
   county news page. Search Google for "your city business journal
   RSS". Keep each line's dash and quotes: `- "https://..."`

## Step 3: Give it a brain

1. **Add your two secrets.** In a new browser tab, open your fork on
   github.com (not the editor) and go to **Settings > Secrets and
   variables > Actions > New repository secret**. Add these two, names
   typed exactly, values pasted with no extra spaces:
   - Name: `ANTHROPIC_API_KEY` -- Value: your key from console.anthropic.com
   - Name: `RESEND_API_KEY` -- Value: your key from resend.com
2. **Teach it your business.** Back in the web editor, click
   **prompt.txt**. Find the loud comment that says EDIT THIS LINE.
   Replace `[YOUR CITY]` and `[YOUR NICHE]` with your real city and
   what you sell. That one line is the only thing you need to change.

## Step 4: Ship it

1. In the web editor, click **config.yml** one more time and replace
   `you@example.com` with your real email address: the SAME address you
   signed up to Resend with (the free plan only delivers to that one).
2. **Commit (save) your changes:** click the Source Control icon in the
   left sidebar (the branching-lines symbol with a blue dot), type any
   short message like `my setup`, and click **Commit & Push**.
3. Go back to your fork on github.com and click the **Actions** tab.
   **GitHub switches workflows off on every new fork.** You'll see a
   button that says something like "I understand my workflows, go ahead
   and enable them": click it. Without this, nothing can run.
4. In the left list click **Morning Brief**, then the **Run workflow**
   button on the right, then the green **Run workflow** confirm button.
5. Click the run that appears (give it a few seconds), then click
   **brief** to watch it work. In about a minute you'll see
   "All done. Check your inbox."
6. Check your inbox. First time, also check spam and mark it "not
   spam" so tomorrow's lands where it should.

From now on it runs by itself every morning at 7 AM Eastern.

---

## Troubleshooting

**"Your ANTHROPIC_API_KEY secret wasn't found."**
The secret is missing or the name isn't exact. It must be all caps with
underscores: `ANTHROPIC_API_KEY`. Add it in YOUR fork under Settings >
Secrets and variables > Actions (secrets do not copy over when you
fork).

**"Claude rejected your API key" or "out of credit."**
Your key was pasted incompletely or with spaces, or your Anthropic
account has no credit. Create a fresh key at console.anthropic.com and
update the secret; add about 5 dollars of credit under Billing.

**"Resend refused to deliver" or no email arrives.**
The free Resend plan only delivers to the exact email you signed up
with. Make sure the `email:` line in config.yml matches your Resend
account address. If the log says the email sent, check your spam
folder.

**"None of your feeds returned any headlines."**
One or more feed addresses in config.yml isn't really an RSS feed. Open
each address in your browser: a feed looks like raw code full of
`<item>` tags. If you see a normal webpage, find that site's RSS link
and use that address instead, or put back one of the three defaults.

**There's no Run workflow button in the Actions tab.**
Two causes. First: GitHub disables workflows on new forks, so click the
"enable workflows" button on the Actions tab if you see one. Second:
make sure you clicked **Morning Brief** in the left-hand list first;
the button lives on that page.

---

## What this is the tip of

This is the workshop edition: one file of pipeline, small enough to
read over coffee. The production version this was carved from runs the
same loop every morning but adds deduplication (so the same project
never shows up twice), multi-recipient delivery for a whole sales team,
and lead extraction: pulling out the actual companies and contacts
behind each story, scoring them, and learning from thumbs-up and
thumbs-down feedback. If the daily brief earns its keep, that's the
direction it grows.
