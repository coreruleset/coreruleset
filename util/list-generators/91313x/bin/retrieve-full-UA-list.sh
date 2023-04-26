#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script is used to retrieve a list of user-agents from several online sources
# The script also transforms the strings it receives and prints them via STDOUT.
#

CURL_OPTIONS="--silent"

(

	curl $CURL_OPTIONS https://raw.githubusercontent.com/mitchellkrogza/apache-ultimate-bad-bot-blocker/master/Apache_2.4/custom.d/globalblacklist.conf -s | \
	   grep BrowserMatchNoCase | \
	   grep bad_bot | \
	   cut -d\" -f2 | cut -b7- | \
	   sed \
		   -e "s/AiHitBot/AiHit/" \
		   -e "s/Anarchy99/Anarchy/" \
		   -e "s/coccocbot/coccoc/" \
		   -e "s/ECCP\/1.0/ECCP/" \
		   -e "s/ExtractorPro/Extractor/" \
		   -e "s/Lipperhey.*/Lipperhey/" \
		   -e "s/Majestic.*/Majestic/" \
		   -e "s/PageThing.com/PageThin/" \
		   -e "s/RankingBot.*/RankingBot/" \
		   -e "s/seocompany.store/seocompany/" \
		   -e "s/Sogou\\ web\\ spider/Sogou\\ web/" \
		   -e "s/Trendiction.*/Trendiction/" \
		   -e "s/ubermetrics-technologies.com/ubermetrics-technologies/" \
		   -e "s/Wallpapers\/3.0/Wallpapers/" \
		   -e "s/xpymep1.exe/xpymep/" \
		   -e "s/zauba.io/zauba/" \
		   -e "s/(?:.*//" -e "s/\\\ / /g" \
		   -e "/Curious/d" \
		   -e "/Firefox\/7.0/d"


	curl $CURL_OPTIONS https://raw.githubusercontent.com/JayBizzle/Crawler-Detect/master/raw/Crawlers.txt | sed \
		    -e "/.*bot|crawl.*/s/[(|]/\n/g" \
		    -e "/^\[a-z0-9.*/d" \
		    -e "s/\^docker.*/docker/"    \
		    -e "s/\^Ruby.*/Ruby/" \
		    -e "s/\^VSE.*/VSE/"   \
		    -e "s/\^XRL.*/XRL/"   \
		    -e "s/^acebook.*/facebookexternalhit/"  \
		    -e "s/^Aprc.*/Aprc/"  \
		    -e "s/^Blackboard Safeassign/Blackboard/"  \
		    -e "s/^CAAM.*/CAAM/"  \
		    -e "s/^centuryb.o.t9.*/centuryb.o.t9/" \
		    -e "s/^colly -/colly/" \
		    -e "s/^Daum.*/Daum/"   \
		    -e "s/^developers.*google.*/developers.google/" \
		    -e "s/Dispatch\\\\\//Dispatch/" \
		    -e "s/Disqus\\\\\//Disqus/" \
		    -e "s/Domains Project\\\\\//Domains Project/" \
		    -e "s/^Drupal.*/Drupal/"  \
		    -e "s/^Fetch\\\\\/.*/Fetch\//"    \
		    -e "s/^Fever.*/Fever/"    \
		    -e "s/^Fuzz Faster U Fool/Fuzz Faster/"    \
		    -e "s/^Go .*/Go/"     \
		    -e "s/HAA.A..RTLAND.*/HAARTLAND\nHAAARTLAND/"  \
		    -e "s/^IPS.*/IPS/"    \
		    -e "s/^IPWorks.*/IPWorks/"    \
		    -e "s/^Java.*/Java/"    \
		    -e "s/Jetty\\\\\//Jetty/" \
		    -e "s/^Jobsearch.*/Jobsearch/"    \
		    -e "s/Majestic.*/Majestic/" \
		    -e "s/masscan\\\\\//masscan/" \
		    -e "s/Mediapartners.*/Mediapartners/" \
		    -e "s/Mojolicious.*/Mojolicious/" \
		    -e "s/MuckRack\\\\\//MuckRack/" \
		    -e "s/NING../NGIN\//"   \
		    -e "s/newspaper../newspaper\//"   \
		    -e "s/^NewsBlur.*/NewsBlur/"  \
		    -e "s/Nmap.*/Nmap/" \
		    -e "s/Perlu -/Perlu/" \
		    -e "s/PhantomJS\\\\\//PhantomJS/" \
		    -e "s/Ploetz.*/Ploetz/" \
		    -e "s/PhantomJS Screenshoter/PhantomJS/" \
		    -e "s/^PTST.*/PTST/"   \
		    -e "s/^Realplayer%20/Realplayer /"  \
		    -e "s/Seznam/SeznamBot/"   \
		    -e "s/^Sitemap.*/Sitemap/"   \
		    -e "s/^Wallpapers.*/Wallpapers/"  \
		    -e "s/^WhereGoes.*/WhereGoes/"  \
		    -e "s/WordPress.*/Wordpress/"  \
		    -e "s/wprecon.*/wprecon/"  \
		    -e "s/^xpymep.*/xpymep/"  \
		    -e "s/^Y!J-.*/Y!J-/"   \
		    -e "s/^ YLT/YLT/"   \
		    -e "s/Yandex(.*/Yandex/" \
		    -e "s/Y!J-/Y!J/" \
		    -e "s/\\\\\\\\\/$//" \
		    -e "s/\\\\$//" \
		    -e "/\^NG.*0-9/d" \
		    -e "/\^NGIN/d"


		curl $CURL_OPTIONS -s "https://raw.githubusercontent.com/monperrus/crawler-user-agents/master/crawler-user-agents.json" | grep pattern | cut -d\" -f4 | sed \
		    -e "s/Ahrefs.*/Ahrefs/" \
		    -e "s/aiHitBot/aiHit/" \
		    -e "s/AspiegelBot/Aspiegel/" \
		    -e "s/AdsBot-Google.*/AdsBot-Google/" \
		    -e "s/Bark.rR.owler/BarkRowler/" \
		    -e "s/CriteoBot/Criteo/" \
		    -e "s/.Cc.urebot/Curebot/" \
		    -e "s/Dataprovider.com/Dataprovider/" \
		    -e "s/Digg Deeper/Digg/" \
		    -e "s/Digincore bot/Digincore/" \
		    -e "s/gluten free crawler./gluten free crawler/" \
		    -e "s/Googlebot.*/Googlebot/" \
		    -e "s/Livelap.bB.ot/LivelapBot/" \
		    -e "s/.pP.ingdom/pingdom/" \
		    -e "s/.*PTST/PTST/" \
		    -e "s/Mediapartners.*/Mediaparners/" \
		    -e "s/Nimbostratus.*/Nimbostratus/" \
		    -e "s/Nmap.*/Nmap/" \
		    -e "s/NINJA bot/NINJA/" \
		    -e "s/pinterest.com.bot/pinterest.com/" \
		    -e "s/S.eE..mM.rushBot/SemrushBot/" \
		    -e "s/sistrix crawler/sistrix/" \
		    -e "s/siteexplorer.*/siteexplorer/" \
		    -e "s/Siteimprove.com/Siteimprove/" \
		    -e "s/.*sentry/sentry/" \
		    -e "s/..\.uptime..\./.uptime./" \
		    -e "s/Uptimebot...org/Uptimebot/" \
		    -e "s/Validator...nu/Validator.nu/" \
		    -e "s/Yandex.*/Yandex/" \
		    -e "s/\[wW\]get/wget/" \
		    -e "s/\\\\\\\\\/$//" \
		    -e "s/\\\\$//" \
		    -e "/^NING/d" \
		    -e "/^Fetch/d" \

		) \
		| sed \
			-e "s/\\\\\//\//" \
			-e "s/\\\././g" \
			-e "s/\\\\\\\//g" \
			-e "s/\\\\\././" \
			-e "s/\\\\(/(/" \
			-e "s/\\\\)/)/" \
			-e "s/^[\^]//" \
			-e "s/\$$//" \
		| tr "A-Z" "a-z" | \
		sort | \
		uniq


