# Security Policy

## Supported Versions

OWASP CRS has three types of releases: Major releases (4.0.0), minor releases (4.25.0, 4.26.0, etc.), and point releases (4.25.1, 4.25.2, etc.).
For more information see our [wiki](https://github.com/coreruleset/coreruleset/wiki/Release-Policy).

The OWASP CRS officially supports the following versions with security patches:

- The **two latest point releases** on the current development line.
- The **CRS v4.25.x LTS** release line, which receives security fixes until **Q3 2027**.

We are happy to receive and merge PR's that address security issues in older versions of the project, but the team itself may choose not to fix these.
Along those lines, OWASP CRS team may not issue security notifications for unsupported software.

| Version   | Supported          | Notes                              |
| --------- | ------------------ | ------------------------------     |
| 4.NN.z    | :white_check_mark: | Current stable                     |
| 4.NN-1.z  | :white_check_mark: | Previous stable                    |
| 4.25.z    | :white_check_mark: | **LTS — supported until Q3 2027 ** |
| 4.y.z     | :x:                | Not supported                      |
| 3.3.x     | :x:                | EOL - Q3 2026                      |
| 3.2.x     | :x:                | EOL                                |
| 3.1.x     | :x:                | EOL                                |
| 3.0.x     | :x:                | EOL                                |
| 2.x       | :x:                | EOL                                |

> **Note for LTS users:** The v4.25.x LTS receives only security fixes, critical regression fixes, and critical false positive fixes. New rules and features are available exclusively on the current stable releases. See [BACKPORT_POLICY.md](BACKPORT_POLICY.md) for details on what is backported to the LTS branch.

:warning: If you are on the **v3.3.x** branch, it will be completely unsupported by ** Q3 2026 **.

## GPG Signed Releases

Releases are signed using [our GPG key](https://coreruleset.org/security.asc), (fingerprint: 3600 6F0E 0BA1 6783 2158 8211 38EE ACA1 AB8A 6E72). You can verify the release using GPG/PGP compatible tooling.

### Importing the GPG Key

To get our key using gpg: `gpg --keyserver pgp.mit.edu --recv 0x38EEACA1AB8A6E72` (this id should be equal to the last sixteen hex characters in our fingerprint).
You can also use `gpg --fetch-key https://coreruleset.org/security.asc` directly.

### Verifying the CRS Release

Download the release file and the corresponding signature. The following example shows how to do it for `v4.25.0` release:

```bash
$ wget https://github.com/coreruleset/coreruleset/archive/refs/tags/v4.25.0.tar.gz
$ wget https://github.com/coreruleset/coreruleset/releases/download/v4.25.0/coreruleset-4.25.0.tar.gz.asc
```

**Verification**:

```bash
❯ gpg --verify coreruleset-4.25.0.tar.gz.asc v4.25.0.tar.gz
gpg: Signature made ...
gpg:                using RSA key 36006F0E0BA167832158821138EEACA1AB8A6E72
gpg: Good signature from "OWASP Core Rule Set <security@coreruleset.org>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 3600 6F0E 0BA1 6783 2158  8211 38EE ACA1 AB8A 6E72
```

If the signature was good, the verification succeeded. If you see a warning like the above, it means you know our public key, but you are not trusting it. You can trust it by using the following method:

```bash
gpg --edit-key 36006F0E0BA167832158821138EEACA1AB8A6E72
gpg> trust
Your decision: 5 (ultimate trust)
Are you sure: Yes
gpg> quit
```

Then you will see this result when verifying:
```bash
gpg --verify coreruleset-4.25.0.tar.gz.asc v4.25.0.tar.gz
gpg: Signature made ...
gpg:                using RSA key 36006F0E0BA167832158821138EEACA1AB8A6E72
gpg: Good signature from "OWASP Core Rule Set <security@coreruleset.org>" [ultimate]
```

## Reporting a Vulnerability

We strive to make the OWASP CRS accessible to a wide audience of beginner and experienced users.
We welcome bug reports, false positive alert reports, evasions, usability issues, and suggestions for new detections.
Submit these types of non-vulnerability related issues via Github.
Please include your installed version and the relevant portions of your audit log.
False negative or common bypasses should [create an issue](https://github.com/coreruleset/coreruleset/issues/new) so they can be addressed.

Do this before submitting a vulnerability using our email:
1) Verify that you have the latest version of OWASP CRS.
2) Validate which Paranoia Level this bypass applies to. If it works in PL4, please send us an email.
3) If you detected anything that causes unexpected behavior of the engine via manipulation of existing CRS provided rules, please send it by email.
4) Check whether the exploit/vulnerability is covered at a higher paranoia level by testing it against the [CRS Sandbox](https://coreruleset.org/docs/6-development/6-4-using-the-crs-sandbox/) at a higher paranoia level.

We also provide you with the [Sandbox project](https://coreruleset.org/docs/development/sandbox/), where you can test your bypass and report back to us. If testing using the sandbox, please include the `X-Unique-ID` from the response in your email.

Our email is [security@coreruleset.org](mailto:security@coreruleset.org). You can send us encrypted email using the same GPG key we use to sign releases, fingerprint: `3600 6F0E 0BA1 6783 2158 8211 38EE ACA1 AB8A 6E72`.

We are happy to work with the community to provide CVE identifiers for any discovered security issues if requested.

> **LTS-specific note:** Security vulnerabilities that affect v4.25.x LTS will be patched in a point release on the `lts/v4.25.x` branch. If you are running the LTS and discover a vulnerability, please specify "LTS v4.25.x" in your report so we can prioritize the backport accordingly.

If in doubt, feel free to reach out to us!

## EU Cyber Resilience Act (CRA) — Steward Policy

OWASP CRS is developed under the [OWASP Foundation](https://owasp.org), which is expected
to act as the CRA "Open Source Software Steward" for this project. The relationship between
the Foundation and CRS as a formally designated Steward/Project pair has not yet been
ratified; this section will be updated once that is finalized. This is not legal guidance.

This policy, together with the rest of this document, is put in place and documented to
foster the development of a secure product and the effective handling of vulnerabilities,
as follows:

- **Fostering secure development**: every rule change goes through mandatory PR review
  (architecture, regex correctness, ReDoS risk), an automated regression test suite, a
  linter (`crs-linter`) enforcing metadata and tagging conventions, and a quantitative
  false-positive corpus check before merging. See [CONTRIBUTING.md](CONTRIBUTING.md).
- **Documenting, addressing, and remediating vulnerabilities**: see "Reporting a
  Vulnerability" above. Fixed vulnerabilities are documented via GitHub Security Advisories
  (GHSAs) and, where warranted, a CVE. Triage and remediation is coordinated by the CRS
  security response role described in the project's governance documentation.
- **Sharing information within the open source community**: where a reported vulnerability
  originates in or also affects an upstream engine (ModSecurity, Coraza) or a sibling
  WAF rule set, we notify the relevant upstream/sibling maintainers.
- **Voluntary reporting to a CSIRT/ENISA**: CRS supports voluntary reporting of
  vulnerabilities, incidents, and near-misses to a national CSIRT designated as
  coordinator, or to ENISA, as provided for under CRA Article 15. **The specific CSIRT
  has not yet been designated** — this depends on OWASP Foundation's establishment
  status, which has not yet been determined for this purpose. This section will name
  the designated CSIRT once that determination is made.
- **Market Surveillance Authority**: not yet designated, for the same reason as above.
  Market surveillance authorities may request a copy of this policy and evidence of its
  application.

The OWASP CRS Team.
