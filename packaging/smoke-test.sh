#!/usr/bin/env bash
# Installs the owasp-crs package from PKGDIR with Apache and ModSecurity v2, then checks
# that CRS blocks an attack and lets a clean request through.
# Runs as root in a Debian- or RHEL-family container. Usage: packaging/smoke-test.sh PKGDIR
set -euo pipefail

pkgdir=$(cd "${1:?usage: $0 PKGDIR}" && pwd)

if command -v apt-get >/dev/null; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get -qq update
    apt-get -qq install -y --no-install-recommends apache2 libapache2-mod-security2 curl \
        "${pkgdir}"/owasp-crs_*_all.deb
    sed 's/^SecRuleEngine .*/SecRuleEngine On/' /etc/modsecurity/modsecurity.conf-recommended \
        > /etc/modsecurity/modsecurity.conf
    echo 'Include /usr/share/owasp-crs/owasp-crs.conf' > /etc/apache2/conf-enabled/owasp-crs.conf
    httpd=(apache2ctl)
else
    # mod_security's own config already sets SecRuleEngine On
    dnf -q -y install httpd mod_security "${pkgdir}"/owasp-crs-*.noarch.rpm
    echo 'Include /usr/share/owasp-crs/owasp-crs.conf' > /etc/httpd/conf.d/zz-owasp-crs.conf
    httpd=(httpd)
fi

echo ok > /var/www/html/index.html
"${httpd[@]}" -t
"${httpd[@]}" -k start
sleep 1

attack=$(curl -s -o /dev/null -w '%{http_code}' 'http://localhost/?q=/etc/passwd')
clean=$(curl -s -o /dev/null -w '%{http_code}' 'http://localhost/')
echo "attack: ${attack}, clean: ${clean}"
[ "${attack}" = 403 ] && [ "${clean}" = 200 ]
