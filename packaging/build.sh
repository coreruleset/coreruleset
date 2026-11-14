#!/usr/bin/env bash
# Builds the minimal release archives and the owasp-crs .deb/.rpm for a tagged release.
# Usage: packaging/build.sh VERSION [OUTDIR]   (e.g. packaging/build.sh 4.30.0)
# Needs GNU tar, zip and nfpm (https://nfpm.goreleaser.com). Signing is done separately.
set -euo pipefail

version=${1:?usage: $0 VERSION [OUTDIR]}
repo=$(git rev-parse --show-toplevel)
mkdir -p "${2:-build}"
out=$(cd "${2:-build}" && pwd)
name="coreruleset-${version}"
# GNU tar is "gtar" on macOS; bsdtar lacks --sort and fails below
tar=$(command -v gtar || command -v tar)
# Fixed timestamps make the archives reproducible
mtime=$(git -C "${repo}" log -1 --format=%ct "v${version}")

rm -rf "${out:?}/${name}"
git -C "${repo}" archive --prefix="${name}/" "v${version}" | "${tar}" -x -C "${out}"
cd "${out}"
rm -rf "${name}"/{util,regex-assembly,tests,packaging} "${name}/renovate.json" "${name}"/.[!.]*
mv -f "${name}"/*.md "${name}/docs/"

"${tar}" --sort=name --mtime="@${mtime}" --owner=0 --group=0 --numeric-owner -cf - "${name}" \
    | gzip -9n > "${name}-minimal.tar.gz"
# git archive already set every file's mtime to the commit time; -D skips directory entries
rm -f "${name}-minimal.zip"
find "${name}" -type f | LC_ALL=C sort | TZ=UTC zip -qXD -@ "${name}-minimal.zip"

# nfpm paths are relative to the minimal tree; the loader file only goes in the packages
cp "${repo}/packaging/owasp-crs.conf" "${name}/"
cd "${name}"
for packager in deb rpm; do
    VERSION="${version}" nfpm package -f "${repo}/packaging/nfpm.yaml" -p "${packager}" -t "${out}"
done
