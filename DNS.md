# sparrowbsd.com DNS handoff

GitHub Pages hosts the site; IONOS remains the registrar and DNS provider.
The repository Pages setting must claim sparrowbsd.com before these DNS changes.

For the apex (`@`), replace the current website A record with all four:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

For `www`, create a CNAME to `neo-bell-laboratories.github.io` (without the
repository name). Remove conflicting website A/AAAA/CNAME/forwarding entries
for these two names. Preserve MX, mail, verification and other unrelated records.
GitHub will redirect the www name to the configured apex domain.

After DNS resolves to GitHub, enable HTTPS enforcement in Settings → Pages.
GitHub provisions the certificate after validating the DNS records. Do not
publish API keys, IONOS credentials, or DNS tokens in this repository.

Sources:
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https

The catalogs are at `/pkg/index.json`, `/ports/index.json`, and `/cdn/index.json`.
`/cdn/` links to official release assets served by GitHub; it is not a separate
upload service. The native pkg client still uses trusted local source recipes.
