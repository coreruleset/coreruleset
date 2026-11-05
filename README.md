# crs-toolchain

[![Regression Tests](https://github.com/coreruleset/crs-toolchain/actions/workflows/regression.yml/badge.svg)](https://github.com/coreruleset/crs-toolchain/actions/workflows/regression.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/coreruleset/crs-toolchain/badge)](https://securityscorecards.dev/viewer/?uri=github.com/coreruleset/crs-toolchain)

The CRS developer's utility belt. The documentation lives at [coreruleset.org](https://coreruleset.org/docs/development/crs_toolchain/).

## Installation

### Homebrew (macOS and Linux)

`crs-toolchain` can be installed on macOS and Linux via [Homebrew](https://brew.sh) using the [CRS tap](https://github.com/coreruleset/homebrew-tap):

```shell
brew tap coreruleset/tap
brew install crs-toolchain
```

To upgrade to the latest version:

```shell
brew upgrade crs-toolchain
```

### Linux

Download the latest release archive for your architecture from the [releases page](https://github.com/coreruleset/crs-toolchain/releases), then extract and install the binary:

```shell
# Replace <version> and <arch> with the appropriate values (e.g. 1.0.0 and amd64)
curl -sSL https://github.com/coreruleset/crs-toolchain/releases/download/v<version>/crs-toolchain_<version>_linux_<arch>.tar.gz | tar -xz crs-toolchain
sudo mv crs-toolchain /usr/local/bin/
```

Alternatively, `.deb` and `.rpm` packages are available on the [releases page](https://github.com/coreruleset/crs-toolchain/releases):

```shell
# Debian/Ubuntu (.deb)
sudo dpkg -i crs-toolchain_<version>_linux_<arch>.deb

# RHEL/Fedora (.rpm)
sudo rpm -i crs-toolchain_<version>_linux_<arch>.rpm
```

### Install with Go

If you have Go 1.19+ installed, you can install `crs-toolchain` directly:

```shell
go install github.com/coreruleset/crs-toolchain/v2@latest
```

Make sure your Go bin directory (typically `~/go/bin`) is on your `PATH`.

### Self-Update

Once `crs-toolchain` is installed (via any method), you can update to the latest version using the built-in self-update command:

```shell
crs-toolchain util self-update
```

This will automatically download and replace the current binary with the latest release for your platform.
