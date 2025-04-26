# `restricted-upload.data` file generator

This script generates the `restricted-upload.data` file based on the content of `restricted-files.data`.

This script requires crs-toolchain command to work.

## How It Works

- It first clears all non-commented lines from `restricted-upload.data`.
- It parses `restricted-files.data` to extract:
  - The last path segment after the last `/` in each line.
  - Only words longer than 3 characters.
- These extracted words are deduplicated, sorted, and filtered through `fp-finder` to remove common English words.
- The final list is appended to `restricted-upload.data`.

## Usage

```bash
./generate-restricted-upload-data.bash
```
