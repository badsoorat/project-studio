# One-time host setup — finish the F1 scaffold

The F1 scaffold has been laid down by the `chief-of-staff` running in a
Cowork session. **Three steps remain that must be run from your Windows
host**, not from inside the Cowork sandbox, because git cannot write to
its own config files from the sandbox's mount (Windows permission
semantics).

You only need to do these once, immediately after the scaffold completes.

## Step 1 — remove the aborted `.git/` directory

The sandbox tried to `git init` and got stuck mid-way. The result is an
empty, broken `.git/` directory that Windows needs to clean up.

Open **PowerShell** at the repo root:

```powershell
cd C:\Users\rajee\Desktop\Work\Badsoorat\project-studio
Remove-Item -Recurse -Force .git
```

## Step 2 — initialize the repo cleanly and tag the baseline

```powershell
git init
git config user.name  "Your Name"
git config user.email "you@example.com"
git add -A
git commit -m "F1 scaffold: .project-studio/, skill/ v3.1.0 baseline, upgrade-system/, CI stubs, root docs"
git tag -a v3.1.0-baseline -m "v3.1.0-baseline: imported skill contents, meta-project scaffold."
```

Expected result: one commit on `main`, one annotated tag.

## Step 3 — push to GitHub

```powershell
# If you haven't already created the repo on GitHub:
gh repo create badsoorat/project-studio --private --source=. --remote=origin --push

# Otherwise:
git remote add origin git@github.com:badsoorat/project-studio.git
git push -u origin main
git push --tags
```

## Step 4 — enable branch protection on `main`

Plan §8.2 requires branch protection on `main` before any Change
Request is merged. From the GitHub web UI (Settings → Branches), add
a rule for `main` with:

- **Require pull request reviews**: 2 approvals.
- **Require status checks to pass**: all five T-tier workflows
  (`T1 — lint`, `T2 — structural`, `T3 — behavioral`,
  `T4 — integration`, `T5 — compat`).
- **Include administrators**: on.

Or with `gh`:

```powershell
gh api repos/badsoorat/project-studio/branches/main/protection `
  --method PUT `
  -H "Accept: application/vnd.github+json" `
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["T1 — lint", "T2 — structural", "T3 — behavioral", "T4 — integration", "T5 — compat"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 2 },
  "restrictions": null
}
EOF
```

## Step 5 — open session 2 and resume

From a Cowork session, mount
`C:\Users\rajee\Desktop\Work\Badsoorat\project-studio` and prompt:

```
/project-studio — resume project
```

The CoS will read `.project-studio/state.md`, announce the version of
record (installed v3.1.0) and edit target (working tree → v3.2.0), and
open **F2 — Atom enumeration**.

---

After you've finished Step 5, you can delete this file — it is
instructions for a one-time handoff, not durable project state.
