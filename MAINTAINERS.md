# Maintainer Notes (Henry)

Attendees never need this file. It covers keeping the workshop repo
healthy and the morning-of checklist.

## Updating the pinned Claude model

The model string lives in ONE place: the `CLAUDE_MODEL` constant near
the top of `brief.py` (currently `claude-sonnet-5`). To update:

1. Check the current model list at docs.anthropic.com (Models page).
2. Change the constant to the new id.
3. Run the end-to-end test below from a fresh fork before class.
4. Rough cost check: each run sends ~36 headlines (~4-6k input tokens)
   and gets back <1k output tokens. Fifty attendees running twice
   during class is well under a dollar total on any current model, but
   confirm the new model's pricing hasn't changed that math.

Also pinned, and worth a glance once a quarter: the two actions in
`.github/workflows/brief.yml` (`actions/checkout@v4.2.2`,
`actions/setup-python@v5.3.0`) and the two libraries in
`requirements.txt`. Bump deliberately, test, commit.

## End-to-end test from a fresh fork

This is the same journey an attendee takes; do it with a throwaway
GitHub account if you want the full first-timer experience.

1. Fork github.com/hfscdogg/integrateuworkshops to a test account.
2. Follow README Steps 1-4 exactly as written, using a real Anthropic
   key (with credit) and a real Resend key for an inbox you control.
3. Confirm: Actions tab required the "enable workflows" click; the run
   goes green in under ~2 minutes; the log shows all four steps and the
   brief text; the email lands (check spam).
4. Break it on purpose, twice, to confirm the error messages hold up:
   delete the ANTHROPIC_API_KEY secret and run (expect the exact
   "wasn't found" message); set a garbage feed URL and run (expect the
   per-feed WARNING and a successful brief from the other two feeds).

## Pre-class health checklist (morning of)

Run this before people arrive; it takes about ten minutes.

- [ ] Verify the three default feeds are alive: open each URL from
      config.yml in a browser and confirm raw XML with recent dates.
      (nahbnow.com/feed, constructiondive.com/feeds/news,
      housingwire.com/feed). If one is dead, replace it in config.yml
      and push BEFORE anyone forks.
- [ ] Trigger Run workflow on your own fork; confirm green run + email
      delivered end to end. This also confirms the pinned model id is
      still live and the Anthropic API is up.
- [ ] Confirm the Anthropic console and resend.com are reachable and
      their signup flows haven't changed since the prep video.
- [ ] Skim the Actions log output on the test run: the four numbered
      steps should read cleanly on a projector.
- [ ] Have one spare Anthropic key with credit and one spare Resend key
      ready for attendees whose pre-flight failed.

## Things that bite

- Secrets do NOT copy into forks; everyone must add both secrets to
  their own fork. This is the number one support question.
- Workflows are disabled on new forks until the attendee clicks enable
  on the Actions tab. README Step 4 and Troubleshooting both cover it;
  say it out loud anyway.
- Resend's free tier only delivers to the account owner's address. If
  someone insists on a different recipient, they need to verify a
  domain in Resend; that's out of scope for the hour.
- The cron fires at 11:00 UTC. During EDT that's 7 AM; after the
  November time change it becomes 6 AM Eastern.
