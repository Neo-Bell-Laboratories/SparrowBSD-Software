# SparrowBSD Software

The official publication repository for SparrowBSD system releases, native
source ports, packages, and the sparrowbsd.com information site.

- `OS/`: system release material.
- `Ports/`: native source-port material.
- `Packages/`: package publication material.
- `site/`: static site source.
- `scripts/build_site.py`: stable-release catalogs and page builder.

The site rebuilds on pushes, published/edited/deleted official releases, manual
workflow runs, and a daily refresh. Drafts and prereleases never enter the stable
catalog. Asset naming selects the channel: `sparrowbsd-`/`os-` for system assets,
`pkg-` for package artifacts, and `ports-` for source bundles. Every asset is also
listed in Downloads. Release URLs must belong to this repository.

Publish releases as drafts, attach complete artifacts and checksum files, then
publish. The catalogs preserve GitHub's asset digest when available. An absent
digest is reported as absent. Creating catalogs does not add remote-install or
system-update support to the OS's native pkg client.

Run `python3 scripts/build_site.py` and serve `dist/` to preview. Run
`python3 -m unittest discover -s tests -v` to test catalog generation.

GitHub Pages hosts the site. IONOS manages the sparrowbsd.com DNS zone. See
`DNS.md` for the DNS records and the custom-domain handoff.
