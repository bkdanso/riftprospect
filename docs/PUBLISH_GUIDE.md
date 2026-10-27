# Publish guide (v0.1.0)

*Plain-language note: what is published, and the one step left for you.*

| Output | Where | Status |
|---|---|---|
| Python package | https://pypi.org/project/riftprospect/0.1.0/ | Live 2026-10-27 |
| Software DOI | https://doi.org/10.5281/zenodo.23697827 | Live 2026-10-27 |
| Ranked target table DOI | https://doi.org/10.5281/zenodo.23697829 | Live 2026-10-27 |
| Code repository | https://github.com/bkdanso/riftprospect | Created; waiting for your upload (below) |
| Interactive map | https://bkdanso.github.io/riftprospect/ | Goes live after the upload and step 3 |

## Upload the code to GitHub (10 minutes, in your web browser)

The cloud session was not allowed to push to the new repository, so this is done in the browser.

1. Unzip `riftprospect_github_upload.zip`. You get a folder called `riftprospect`.
2. Go to https://github.com/bkdanso/riftprospect and click **uploading an existing file** (on the empty-repository page).
3. Open the `riftprospect` folder, select **everything inside it** (Cmd+A on Mac, Ctrl+A on Windows), and drag it onto the GitHub page. Wait until every file shows in the list (74 files).
4. In "Commit changes", type `riftprospect v0.1.0` and click **Commit changes**. The page should show README text and a map image.
5. Turn on the map: go to https://github.com/bkdanso/riftprospect/settings/pages. Under "Build and deployment", Source: **Deploy from a branch**; Branch: **main**, folder **/ (root)**; click **Save**. After 1 to 3 minutes, https://bkdanso.github.io/riftprospect/ opens the map.
6. Make the release: go to https://github.com/bkdanso/riftprospect/releases/new. Choose a tag: type `v0.1.0` and click "Create new tag". Title: `riftprospect v0.1.0`. Description (paste): `First release. Software DOI 10.5281/zenodo.23697827; ranked target table DOI 10.5281/zenodo.23697829; PyPI: pip install riftprospect.` Click **Publish release**.

## Then revoke the tokens (3 minutes)

- GitHub: https://github.com/settings/personal-access-tokens
- Zenodo: https://zenodo.org/account/settings/applications/
- PyPI: https://pypi.org/manage/account/token/
