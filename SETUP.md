# Profile README setup

Copy these files into the root of the `NobinSijo7T/NobinSijo7T` repository, preserving their folder structure:

- `README.md`
- `.github/workflows/profile-insights.yml`
- `scripts/generate_profile_insights.py`
- `assets/profile-insights.svg`
- `assets/language-insights.svg`
- `assets/top-repositories.svg`
- `assets/public-activity.svg`

Then commit and push to the `main` branch. The `Profile Insights` workflow runs automatically after the README/workflow/script update, and refreshes the four SVG cards from GitHub's public REST API. It is also scheduled to run daily. To run it manually, open the repository's **Actions** tab, select **Profile Insights**, and choose **Run workflow**.

The workflow writes assets back to the repository. It uses the built-in `GITHUB_TOKEN`; no personal access token or third-party stats service is required. If repository settings disable GitHub Actions or write permissions for Actions, enable Actions and allow workflow tokens to write repository contents.

The activity card counts recent events returned by GitHub's public-events endpoint. It deliberately does not present those events as a complete contribution calendar and cannot show private activity.
