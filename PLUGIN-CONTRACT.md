# CRS Plugin Contract: Extending CRS List Variables

> **Status:** Draft for discussion in [#4286](https://github.com/coreruleset/coreruleset/issues/4286).
> Decided so far: one variable per plugin rule (design B), and the pipe format for methods ([#4960](https://github.com/coreruleset/coreruleset/pull/4960)).
> Open points are marked with **[OPEN]**.
>
> This file is the reference for the plugin contract. The [Writing plugins](https://coreruleset.org/docs/4-about-plugins/4-2-writing-plugins/) page on coreruleset.org explains how to use it and links here.

## 1. Purpose

CRS plugins sometimes need to allow more than the CRS defaults. For example, a Nextcloud plugin needs WebDAV methods like `PROPFIND`.

Plugins are loaded before `REQUEST-901-INITIALIZATION.conf`. Rule 901 only sets a default if the variable does not exist yet. So if a plugin sets `tx.allowed_methods` itself, the CRS defaults are skipped. The plugin then has to copy the whole default list and keep it in sync with every CRS release.

This contract solves that. Plugins write their additions to **their own variables**. CRS collects them after the defaults are set. Plugins never touch the CRS list variables directly.

The key words MUST, MUST NOT, SHOULD and MAY in this document are used as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## 2. Scope

This contract covers **adding entries** to these seven **list variables**:

| CRS list variable | Checked by |
|---|---|
| `tx.allowed_methods` | 911100 |
| `tx.allowed_request_content_type` | 920420 |
| `tx.allowed_request_content_type_charset` | 920480, 922100 |
| `tx.allowed_http_versions` | 920430 |
| `tx.restricted_extensions` | 920440 |
| `tx.restricted_headers_basic` | 920450 |
| `tx.restricted_headers_extended` | 920451 |

For `allowed_*` lists, adding an entry **allows more**. For `restricted_*` lists, adding an entry **restricts more**.

Not covered (see section 8): removing entries, scalar settings, and any other variable.

## 3. How a plugin adds entries

### 3.1 Variable name

A plugin sets one variable per rule and list:

```
tx.plugin_<list>_<rule id>
```

- `<list>` is the name of the CRS list variable without `tx.`, for example `allowed_methods`.
- `<rule id>` is the ID of the plugin rule that sets the variable. It MUST be digits only.

Example: rule `9508190` adds methods with `tx.plugin_allowed_methods_9508190`.

Because rule IDs are unique, variable names are unique too. Plugins cannot overwrite each other.

### 3.2 Rules for plugin authors

A plugin that adds entries to a CRS list:

1. MUST set the variable in its **`-before.conf`** file.
2. MUST set the variable in **phase 1**. If a condition is used, it MUST only use data that is available in phase 1 (for example `REQUEST_FILENAME`, `REQUEST_HEADERS`, `REQUEST_METHOD`), not the request body.
3. MUST use the name format from section 3.1, with the ID of the rule that sets it.
4. MUST use the value format of the list (section 4). Several entries in one value are separated by a space.
5. MUST NOT set an empty value. Some engines refuse to load an empty `setvar` (section 6).
6. When adding a content type that a body processor can parse (JSON, XML, URL-encoded, multipart), MUST also select that processor for the same requests with `ctl:requestBodyProcessor`, as rules 901360 and 901370 do. Otherwise the body is not parsed into `ARGS`, and rules that only inspect `ARGS` miss attacks in it. For content types without a matching processor, the body can only be inspected as `REQUEST_BODY`; the plugin SHOULD document that.
7. MUST NOT set or change the CRS list variables (`tx.allowed_methods`, …) directly.
8. MUST NOT set or change internal CRS variables, for example `tx.request_method` (section 7).
9. SHOULD limit additions to where they are needed (for example, WebDAV methods only under `/remote.php/dav/`) instead of adding them for every request.
10. SHOULD include go-ftw tests that show the addition works where it is needed and does not apply elsewhere. For added content types, the tests SHOULD also show that an attack in the body is still detected.

### 3.3 Example

```apache
# nextcloud-rule-exclusions-before.conf

# Allow WebDAV methods and content types, but only for the WebDAV endpoints
SecRule REQUEST_FILENAME "@rx /(?:remote|public)\.php/dav/" \
    "id:9508190,\
    phase:1,\
    pass,\
    t:none,\
    nolog,\
    ver:'nextcloud-rule-exclusions-plugin/x.y.z',\
    setvar:'tx.plugin_allowed_methods_9508190=|PROPFIND| |PROPPATCH| |MKCOL| |MOVE| |COPY| |LOCK| |UNLOCK| |REPORT|',\
    setvar:'tx.plugin_allowed_request_content_type_9508190=|text/vcard| |text/calendar|'"
```

## 4. Value format per list

The CRS checks use `@within`, which looks for a **substring**. The delimiters make sure that only whole entries match. Some checks convert the request value to lowercase but not the list, so list entries MUST already be lowercase where noted.

| List | Format of one entry | Case | Example value |
|---|---|---|---|
| `allowed_methods` | `\|METHOD\|` | exactly as sent, usually uppercase (methods are case-sensitive) | `\|PROPFIND\| \|MKCOL\|` |
| `allowed_http_versions` | `HTTP/x.y` **[OPEN]** | exactly as sent | `HTTP/2.0` |
| `allowed_request_content_type` | `\|type/subtype\|` (no parameters) | **lowercase** | `\|text/vcard\| \|text/calendar\|` |
| `allowed_request_content_type_charset` | `\|charset\|` | **lowercase** | `\|utf-16\|` |
| `restricted_extensions` | `.ext/` | **lowercase** | `.bak/ .old/` |
| `restricted_headers_basic` | `/header-name/` | **lowercase** | `/x-debug/` |
| `restricted_headers_extended` | `/header-name/` | **lowercase** | `/x-debug/` |

An entry in the wrong case never matches, and no error is reported.

An entry MUST NOT contain its own delimiter (`|` or `/`) or a space. For example, `|FOO|BAR|` would allow both `FOO` and `BAR`. A request cannot exploit this on its own: entries are separated by spaces, and a method or content type cannot contain a space, so a request value never matches more than one entry.

**Methods** are wrapped in pipes, like content types. Rule 911100 wraps the request method as `|%{REQUEST_METHOD}|` and checks it against `tx.allowed_methods`. A plain space-separated list (`GET POST`) does not work any more: no method would match, and every request would be flagged. This format comes with [#4960](https://github.com/coreruleset/coreruleset/pull/4960) (not merged yet). See section 9.

Why pipes and not spaces: padding the values with spaces is not reliable, because ModSecurity v2 removes leading spaces from `setvar` values (section 6). Then `OST` would match `POST`.

**[OPEN]** **HTTP versions** are still separated by spaces only and have the same substring problem (920430). They are expected to move to the pipe format in a separate PR. Until then, plugins use the space-separated format for `allowed_http_versions`.

## 5. What CRS guarantees

For each list in section 2, `REQUEST-901-INITIALIZATION.conf` contains one collect rule. The rules are placed **directly after the default values** (901160–901171), so they run after the defaults are set and before any rule that checks the lists. Example:

```apache
SecRule TX:/^plugin_allowed_methods_[0-9]+$/ "@rx \S" \
    "id:901600,\
    phase:1,\
    pass,\
    t:none,\
    nolog,\
    tag:'OWASP_CRS',\
    ver:'OWASP_CRS/4.x.0',\
    setvar:'tx.allowed_methods=%{tx.allowed_methods} %{MATCHED_VAR}'"
```

CRS guarantees that:

1. The CRS defaults, or the values the user set in `crs-setup.conf`, stay in the list. Plugin entries are **added**.
2. Every matching `tx.plugin_<list>_<id>` variable is collected, in any order. Duplicate entries are harmless.
3. If no plugin sets a variable, nothing changes.
4. The collect rule adds the separator. Plugins do not need a leading space.
5. The variable names in section 3.1 and the formats in section 4 are a public interface. Any change to them is a breaking change and is announced in `CHANGES.md` and on the CRS blog.
6. This works the same on ModSecurity v2, libModSecurity v3 and Coraza.
7. The collect rules themselves need no change in `crs-setup.conf`. (The new method format does, see section 9.)

**Proposed rule IDs [OPEN]:**

| ID | Collects into |
|---|---|
| 901600 | `tx.allowed_methods` |
| 901610 | `tx.allowed_request_content_type` |
| 901620 | `tx.allowed_request_content_type_charset` |
| 901630 | `tx.allowed_http_versions` |
| 901640 | `tx.restricted_extensions` |
| 901650 | `tx.restricted_headers_basic` |
| 901660 | `tx.restricted_headers_extended` |

The regex MUST end with `_[0-9]+$`. Without it, the rule for `allowed_request_content_type` would also collect `allowed_request_content_type_charset` variables.

## 6. Engine notes

These engine differences are why the contract looks the way it does. They were tested on ModSecurity 2.9.7, libModSecurity 3.0.12 and Coraza (main, November 2026).

| Behaviour | v2 | v3 | Coraza |
|---|---|---|---|
| `%{tx.missing}` (variable does not exist) | empty | empty | literal `tx.missing` |
| `setvar:'tx.x='` (empty value) | loads | **config fails to load** | **config fails to load** |
| leading space in a `setvar` value | removed | kept | kept |
| `setvar` runs once per variable matched by `TX:/regex/` | yes | yes | yes |

Because of this, plugins MUST NOT build values from their own variable (`%{tx.plugin_…}`), and MUST NOT set empty values. The contract above avoids both. Coraza issue: [corazawaf/coraza#1857](https://github.com/corazawaf/coraza/issues/1857).

The removed leading space on v2 is also the reason why CRS uses delimiters like `|…|` instead of spaces to compare whole entries (section 4).

## 7. Internal variables

Variables that CRS derives from the list variables are **internal**. They can change in any release. Plugins MUST NOT read or write them. Examples:

- `tx.request_method` (rule 911100)
- `tx.content_type`, `tx.content_type_charset`, `tx.extension`, `tx.header_name_*`

## 8. What this contract does not cover

- **Removing entries.** SecLang cannot remove part of a string. To allow something that a `restricted_*` list blocks, or to skip a check, plugins keep using rule exclusions such as `ctl:ruleRemoveById` or `ctl:ruleRemoveTargetById`, scoped as narrowly as possible.
- **Scalar settings** such as paranoia level, anomaly thresholds or sampling. These are decisions for the operator, not for plugins.
- **Other variables.** Only the seven lists in section 2 are extension points.

## 9. Breaking changes and migration

The new method format (section 4) is a **breaking change**. It MUST be announced in `CHANGES.md` and in a blog post.

The method format change and the collect rules (section 5) MUST ship in the **same release**. If the method format shipped first, plugins that set `tx.allowed_methods` directly would break, and the `tx.plugin_*` variables that replace them would still be ignored.

### 9.1 Users

Users who set `tx.allowed_methods` in `crs-setup.conf` (rule 900200) MUST switch to the pipe format when they update CRS:

```apache
# before
setvar:'tx.allowed_methods=GET HEAD POST OPTIONS'
# after
setvar:'tx.allowed_methods=|GET| |HEAD| |POST| |OPTIONS|'
```

If they don't, **every request** is flagged by 911100, because no method matches the old list. This was confirmed on ModSecurity v2, libModSecurity v3 and Coraza.

### 9.2 Plugins

Plugins that set `tx.allowed_methods` directly (for example the Nextcloud plugin, which copies the defaults in rules 9508100 and appends methods later) break in the same way: their old-format list blocks every request. These plugins MUST:

1. Remove the rules that copy the CRS default lists (for example Nextcloud rules 9508100 and 9508101).
2. Replace every direct change of a CRS list variable with a `tx.plugin_<list>_<rule id>` variable (section 3), using the pipe format for methods.
3. State the minimum CRS version in `plugin.yaml` **[OPEN: version]**. Older CRS versions have no collect rules and would ignore the `tx.plugin_*` variables.

Plugins that only change other lists (content types, charsets, extensions, headers) are not broken by the method change, but they SHOULD migrate too, so they no longer copy the CRS defaults.

## 10. Open points

- **[OPEN]** Rule IDs 9016xx for the collect rules.
- **[OPEN]** Format of HTTP versions (section 4).
- **[OPEN]** Minimum CRS version that supports this contract and the pipe format for methods.
- **[OPEN]** Confirm that #4960 (method format) and the collect rules ship in the same release (section 9).
