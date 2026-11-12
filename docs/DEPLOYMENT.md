# GitHub deployment

## Status of this delivery

No GitHub repository was created. No files were pushed. No Actions run or public
Pages URL was verified. The connected GitHub tools exposed in the creation session
could identify the account and inspect repositories but did not expose new-repository
creation or Pages configuration. The available browser connector was read-only.
No other project was modified.

## Recommended: run the included script locally

Prerequisites: Node 20+, Git and GitHub CLI (`gh`). Authenticate with `gh auth login`.
Do not put a personal access token into the source, HTML, a chat message or the website.

```bash
bash scripts/deploy-github.sh iro-style-atlas
```

The script resolves the current account, requires the repository name as confirmation,
refuses to overwrite an existing repository, checks and builds the source, copies it
to a temporary working directory, creates a public repository, enables Pages build
mode `workflow`, dispatches `pages.yml`, waits, and prints the actual returned URL.
It does not buy services or call an image model.

`IRO_CONFIRM_CREATE=yes` can skip the typed confirmation only in an already authorized
local workflow. Do not use it to infer permission for another account or repository.

## Manual setup

Create a new **public** repository. Add the contents of this project root, including
`.github/workflows/pages.yml`, `data`, `src`, `scripts`, `tests` and `package.json`.
`dist` and `IRO-preview.html` are build outputs and need not be committed.

In repository Settings → Pages, select **GitHub Actions** as the source. Push to
`main` or run **Publish IRO to GitHub Pages** from Actions. GitHub builds and publishes
`dist`. Use the URL returned by the deployment, not a guessed URL.

After deployment, check the homepage, `/en/`, a nested style page, search, locale switch,
copy permissions, saving/reloading a collection, JSON backup import and phone layout.

## Existing repository or partial failure

The create script intentionally stops if the repository exists. Do not delete the
repository or force-push merely to rerun it. For a repository created in a partial run,
inspect its existing contents and Actions history first, then intentionally enable
Pages or dispatch the existing workflow. Updating an existing repository is a separate,
explicit operation.

Pages configuration requires the appropriate repository administration / Pages
permissions. An authentication or authorization error is not an invitation to put a
Key in frontend JavaScript.

## Official references checked 2026-10-17

- GitHub CLI repository creation: https://cli.github.com/manual/gh_repo_create
- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- Pages REST setup: https://docs.github.com/en/rest/pages/pages#create-a-github-pages-site
- Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

The included shell script was syntax-checked only; the remote actions remain untested.
