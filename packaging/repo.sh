#!/usr/bin/env bash
# Builds the signed apt and dnf repositories from every owasp-crs package in PKGDIR.
# Usage: SIGNING_KEY=<fingerprint> [LTS_LINES="4.25"] packaging/repo.sh PKGDIR SITEDIR
# Needs apt-ftparchive, createrepo_c and gpg holding the signing key. Versions whose X.Y is
# listed in LTS_LINES go to the suite lts-X.Y, everything else to stable, so LTS users are
# never moved to a newer release line.
set -euo pipefail
shopt -s nullglob

pkgs=$(cd "${1:?usage: $0 PKGDIR SITEDIR}" && pwd)
mkdir -p "${2:?usage: $0 PKGDIR SITEDIR}"
site=$(cd "$2" && pwd)
sign=(gpg --batch --yes --local-user "${SIGNING_KEY:?set SIGNING_KEY to the key fingerprint}" --digest-algo SHA512)

suite() {
    local line
    line=$(sed -E 's/^owasp-crs[-_]([0-9]+\.[0-9]+)\..*/\1/' <<<"$1")
    if [[ " ${LTS_LINES:-} " == *" ${line} "* ]]; then echo "lts-${line}"; else echo stable; fi
}

for f in "${pkgs}"/owasp-crs_*.deb; do
    dir="${site}/deb/pool/$(suite "${f##*/}")"
    mkdir -p "${dir}" && cp "$f" "${dir}/"
done
for f in "${pkgs}"/owasp-crs-*.rpm; do
    dir="${site}/rpm/$(suite "${f##*/}")"
    mkdir -p "${dir}" && cp "$f" "${dir}/"
done

cd "${site}/deb"
for pool in pool/*; do
    s=${pool#pool/}
    dist="dists/${s}"
    mkdir -p "${dist}/main/binary-all"
    apt-ftparchive packages "${pool}" > "${dist}/main/binary-all/Packages"
    gzip -9nkf "${dist}/main/binary-all/Packages"
    apt-ftparchive \
        -o APT::FTPArchive::Release::Origin="OWASP CRS" \
        -o APT::FTPArchive::Release::Label="owasp-crs" \
        -o APT::FTPArchive::Release::Suite="${s}" \
        -o APT::FTPArchive::Release::Codename="${s}" \
        -o APT::FTPArchive::Release::Architectures="all" \
        -o APT::FTPArchive::Release::Components="main" \
        release "${dist}" > Release.tmp
    mv Release.tmp "${dist}/Release"
    "${sign[@]}" --clearsign -o "${dist}/InRelease" "${dist}/Release"
    "${sign[@]}" --armor --detach-sign -o "${dist}/Release.gpg" "${dist}/Release"
done

for repo in "${site}"/rpm/*; do
    createrepo_c --quiet "${repo}"
    "${sign[@]}" --armor --detach-sign -o "${repo}/repodata/repomd.xml.asc" "${repo}/repodata/repomd.xml"
done

gpg --armor --export "${SIGNING_KEY}" > "${site}/owasp-crs.asc"
