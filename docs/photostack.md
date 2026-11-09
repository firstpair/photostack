# About this book

This book is by Alexy Khrabrov, with Claude as co-author. The ideas and decisions are Alexy's; Claude wrote the text and much of the code with him.

It is a map. Nine other books on the First Pair shelves each describe one tool for keeping photographs: how to tell copies apart, remember what a volume holds, preserve one copy against another, synchronize, store, serve and repair. This book says how they fit together, walks through them end to end, and points to the book that owns each detail. It describes them as of November 2026. Every example uses synthetic paths such as `/Volumes/Archive`.

# The problem

A photograph rarely exists once. There is the camera's file, a DNG converted from it, a copy on a backup disk, another on a shuttle disk, previews in a catalog, and a cloud original. Over years the copies drift. An editor writes a rating into one. A converter rewrites another. A clock correction shifts every capture time. A copy is interrupted halfway and nobody notices.

Then someone wants to free a disk, and has to answer a question that sounds simple: *is everything on this disk somewhere else?* The usual tools answer badly in both directions.

- **A checksum says "different" too often.** Two DNGs with the same sensor samples and a different rating have different SHA-256 hashes. Deleting by checksum keeps everything.
- **A file name says "same" too easily.** Two files called `IMG_0001.DNG` may be different photographs, or one may be truncated. Deleting by name loses things.
- **A thumbnail can lie.** A DNG's embedded preview sits early in the file. When a copy is cut short, the preview often survives, and the file looks fine in every browser while its raw data is gone.

The tools in this book answer the question properly. They identify photographs by what they contain, remember those identities for whole volumes, account for one volume in another by content, and keep every byte that would otherwise be lost, as a delta against the copy that remains.

# The stack

![Each layer is one book, built on the layer below.](book/diagrams/stack.svg)

Read the diagram from the bottom.

**Reading files.** [tiffgraph](https://firstpair.org/books/tiffgraph/) walks the structure of a TIFF or DNG file under a fixed grammar. It finds the one region an editor may rewrite, the XMP packet, and refuses any file outside its grammar with a reason. Beside it sit the ExifTool engines: Perl ExifTool, the engine of record, and exiftool-rs, a faster reimplementation whose records are a separate identity and are never mixed with Perl's.

**Identity.** [phidentify](https://firstpair.org/books/phidentify/) computes six identities of a file. Whole-file SHA-256 answers "is it the same file?"; DNG raw blocks and image data answer "is it the same photograph?"; the Lightroom fingerprint answers "is it the original my catalog recorded?"; the metadata record says what an editor changed; and the preserved digest proves that only the XMP packet differs.

**Index and alignment.** [phindex](https://firstpair.org/books/phindex/) keeps those identities for every file of a volume in one SQLite index, cheap to rerun. `phindex align` accounts for one volume in another by identity, so moved, renamed and re-dated copies are found, and writes pair lists of what matched and how.

**Comparison and preservation.** [DNG Compare](https://firstpair.org/books/dng-compare/) takes those pairs, or a whole tree, and through one command, `dngc`, compares each pair, preserves the source as a verified delta against its counterpart, and records metadata differences in a searchable index. Its archive rebuilds any source file byte for byte.

**Sync and storage.** [Semantic Unison](https://firstpair.org/books/semantic-unison/) synchronizes photo trees, sending a metadata edit without resending image bytes, and preserves what a shuttle disk brings into the same kind of archive. [packdir](https://firstpair.org/books/packdir/) keeps directories of many small files, such as a preview cache, as SQLite archives that still work like plain files. Both store their databases through [Tursolite](https://firstpair.org/books/tursolite/), one interface over SQLite and Turso.

**Applications.** [Lightroom Repair](https://firstpair.org/books/lightroom-repair/) repairs Lightroom Classic catalogs, previews and Sync without forging their state. [diskproxy](https://firstpair.org/books/diskproxy/) serves a folder as a virtual disk, so previews can be browsed and rated with the originals offline, with camera metadata spliced in and ratings captured into sidecars.

# One volume accounted for in another

This walk takes a source volume, `/Volumes/Archive/Photos`, and proves that a backup, `/Volumes/Backup/Photos`, holds everything on it, or keeps what it does not. Each step names the book that describes it fully.

1. **Index both volumes** (phindex). One read of every file, once; later runs read only what changed.

    ```sh
    phindex --db archive.sqlite --root /Volumes/Archive/Photos
    phindex --db backup.sqlite  --root /Volumes/Backup/Photos
    ```

2. **Align them** (phindex). Every source file gets a tier: `identical` (same bytes), `dng-metadata` or `image-metadata` (same photograph, metadata differs), `xmp-only`, `lightroom`, `unit-partner`, or `unmatched`.

    ```sh
    phindex align --left archive.sqlite --left-root /Volumes/Archive/Photos \
                  --right backup.sqlite --right-root /Volumes/Backup/Photos --out align/
    ```

3. **Preserve the whole source** (DNG Compare). Identical files become reference records without being read; the rest become verified deltas against their counterparts; unmatched files become full copies. Metadata comes from the indexes.

    ```sh
    dngc run /Volumes/Archive/Photos /Volumes/Backup/Photos /Volumes/Backup/dngc/Archive \
         --index archive.sqlite backup.sqlite --metadata phindex
    ```

4. **Verify** (DNG Compare). Rebuild a sample from the archive and check every hash.

    ```sh
    dngc verify /Volumes/Backup/dngc/Archive --restore-sample 50
    dngc query  /Volumes/Backup/dngc/Archive              # what metadata differed, most often first
    ```

Only now may the source volume be freed, and only together with the archive and the backup it refers to. Any file comes back with `dngc restore`.

On one real pair of volumes, 1.7 million source files, this accounted for 1.2 million identical files without reading them, 480,000 DNGs whose raw samples matched but whose bytes did not, and 5,600 files with no copy at all. It also found 77 originals that had been truncated long ago while an intact converted copy existed elsewhere: the case where deleting by thumbnail would have kept the broken files.

# A shuttle disk, through Semantic Unison

A shuttle disk carries new photographs from a laptop to the archive. [Semantic Unison](https://firstpair.org/books/semantic-unison/) synchronizes it with the archive's tree. When only metadata changed, it sends the XMP packet, not the image, and checks with the preserved digest that nothing else moved. Before the shuttle is emptied, Unison preserves what it brought into a DNG Compare archive with the same layout, so a refilled path later gets a new *version* rather than overwriting the old one. `dngc versions` lists them and `dngc restore --version` rebuilds any of them.

# Working without the originals

Previews are small, and originals are large and often offline. Two paths make previews useful on their own.

- **Lightroom's previews.** Lightroom Classic builds regular previews and Smart Previews. [Lightroom Repair](https://firstpair.org/books/lightroom-repair/) describes building and verifying them without disturbing the catalog.
- **Serving them as a library.** [diskproxy](https://firstpair.org/books/diskproxy/) presents a folder as a virtual disk without writing it. Its previews plugin serves Smart Previews as DNG stand-ins with a large preview added, or preview JPEGs with camera EXIF spliced in from small stubs; the stubs can be written from phindex's metadata records and kept in one SQLite store. An application such as Photo Mechanic then shows camera, lens, exposure and GPS for every preview. On a writable view, ratings, labels and flags it writes are captured as small XMP sidecars with a journal, and the source is never touched.

Bringing those ratings back into a Lightroom catalog has to go through Lightroom's own writer; Lightroom Repair says what is and is not qualified for that.

# Which tool answers which question

| Question | Start with | Book |
| --- | --- | --- |
| Is this file in my backup? | SHA-256, then raw blocks or image data, from the indexes | phindex, phidentify |
| Was this only a metadata edit? | the preserved digest and the metadata diff | phidentify |
| What changed in the metadata, across a whole archive? | `dngc query` | DNG Compare |
| Can I delete this copy? | `dngc run`, then `dngc verify` | DNG Compare |
| Did the shuttle copy arrive intact? | SHA-256; the preserved digest if metadata was written on arrival | phidentify, Semantic Unison |
| Is this still the original my catalog recorded? | the Lightroom fingerprint | phidentify, Lightroom Repair |
| Can I browse and rate with the originals offline? | diskproxy's previews plugin | diskproxy |
| How do I keep a million small files on a backup disk? | packdir | packdir |

# Who owns what

Each contract is explained in full in one book. The others give it a sentence and a link.

| Contract | Owning book |
| --- | --- |
| The identities and what equality proves | phidentify |
| Index schema, align tiers, pair files | phindex |
| Archive layout, byte-section rule, versions, the engine rule | DNG Compare |
| DNG profiles, `SDE/0-preserved`, the shuttle cycle | Semantic Unison |
| Grammars and refusals for the XMP region | tiffgraph |
| Container format and clones | packdir |
| Engines, journals, sealing and the Turso rules | Tursolite |
| Map file, metadata splicing, ratings capture | diskproxy |
| Catalog, preview and Sync procedures | Lightroom Repair |

## Where it fits

This book is one of nine on the FirstPair photo tools. Each owns one part, and
[The FirstPair Photo Stack](https://firstpair.org/books/photostack/) shows how they fit together.

- **[tiffgraph](https://firstpair.org/books/tiffgraph/)** walks a TIFF or DNG file's structure under a fixed grammar and finds its editable XMP packet.
- **[phidentify](https://firstpair.org/books/phidentify/)** computes a photo's identities: SHA-256, DNG raw blocks, image data, Lightroom fingerprint, metadata record and preserved digest.
- **[phindex](https://firstpair.org/books/phindex/)** keeps those identities for every file of a volume, and aligns two volumes by content.
- **[DNG Compare](https://firstpair.org/books/dng-compare/)** compares pairs and preserves one side byte for byte as deltas against the other, with a searchable metadata section, through `dngc`.
- **[Semantic Unison](https://firstpair.org/books/semantic-unison/)** synchronizes photo trees, sending metadata edits without resending image bytes, and preserves what a shuttle disk brings into the same archives.
- **[packdir](https://firstpair.org/books/packdir/)** keeps directories of small files as SQLite archives that still work like plain files.
- **[Tursolite](https://firstpair.org/books/tursolite/)** is the SQLite and Turso layer under packdir, DNG Compare and Mechanic.
- **[diskproxy](https://firstpair.org/books/diskproxy/)** serves a folder as a virtual disk, such as previews with camera metadata spliced in, and captures ratings into sidecars.
- **[Lightroom Repair](https://firstpair.org/books/lightroom-repair/)** repairs Lightroom Classic catalogs, previews and Sync without forging their state.

The block above is the one every book carries word for word. Its source is `where-it-fits.md` in this book's repository, and `scripts/check-where-it-fits.py` checks a book's copy against it.
