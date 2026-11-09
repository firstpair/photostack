slug: photostack
shelf: photography
default_edition: full

# Publication contract

This repository owns the hub book of the FirstPair photo tools, its manuscript
`docs/photostack.md`, the shared "Where it fits" block `where-it-fits.md` that
every photo book carries word for word (checked by `scripts/check-where-it-fits.py`),
and the cover and headboard in `cover/`. FirstPair owns catalog entries, stable
download and reader routes, and Blob manifests. Follow the shared
`~/src/firstpair/AGENTS.md` publication rules.

The book is by Alexy Khrabrov with Claude as co-author, under the Apache License 2.0.
`cover/photostack-cover.png` and `cover/photostack-headboard.png` are the user's art.

```sh
PATH=/usr/local/bin:$PATH ~/src/firstpair/publishing/scripts/build-library-book.sh --repo-root ~/src/photostack
cd ~/src/firstpair
npm run library:publish -- ~/src/photostack --source https://github.com/firstpair/photostack
```
