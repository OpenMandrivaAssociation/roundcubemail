%if %mandriva_branch == Cooker
# Cooker
%define release %mkrel 1
%else
# Old distros
%define subrel 1
%define release %mkrel 0
%endif

%if %mdkversion >= 201200
# rpmlint just sucks!!!
%define _build_pkgcheck_set %{nil}
%define _build_pkgcheck_srpm %{nil}
%endif

Summary:	A PHP-based webmail server
Name:		roundcubemail
Version:	0.7.2
Release:	%{release}
Group:		System/Servers
License:	GPLv2
# Use the -dep tarballs. These use system copies of the PHP stuff
# rather than including them, which is better for our purposes.
# - AdamW 2007/07
URL:		http://www.roundcube.net/
Source0:	http://downloads.sourceforge.net/roundcubemail/%{name}-%{version}-dep.tar.gz
Epoch:		1
Requires:	apache-mod_php
Requires:	php-gd
Requires:	php-gettext
Requires:	php-iconv
Requires:	php-mbstring
Requires:	php-mcrypt
Requires:	php-openssl
Requires:	php-pspell
Requires:	php-session
Requires:	php-pear-Auth_SASL
Requires:	php-pear-Mail_Mime
Requires:	php-pear-Net_SMTP
Requires:	php-pear-Net_LDAP2
Requires:	php-pear-MDB2
Requires:	php-pear-Net_IDNA2
# The installer suggests the use of these, but they're not
# required - AdamW 2011/01
Suggests:	php-fileinfo
Suggests:	php-intl
# Most people will probably use mysql, but you can use sqlite or
# pgsql, so not a hard require - AdamW 2008/10
Suggests:	php-pear-MDB2_Driver_mysql
%if %mdkversion < 201010
Requires(post):		rpm-helper
Requires(postun):	rpm-helper
%endif
BuildArch:	noarch
# rpm-build / rpm macros does not seem to require php-cli in cooker
BuildRequires:	php-cli
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
RoundCube Webmail is a browser-based multilingual IMAP client with an
application-like user interface. It provides full functionality you expect
from an e-mail client, including MIME support, address book, folder
manipulation, message searching and spell checking. RoundCube Webmail is
written in PHP and requires a MySQL or PostgreSQL database. The user
interface is fully skinnable using XHTML and CSS 2.

%prep

%setup -q -n %{name}-%{version}-dep

%build

%install
rm -rf %{buildroot}

# tell it that we're moving the configuration files
for i in installer/index.php program/include/iniset.php; do \
	sed -i \
		-e "s,INSTALL_PATH . 'config','%{_sysconfdir}/%{name}',g" \
		$i; \
done
# use systemwide log dir and temp dir
sed -i \
    -e 's,logs/,%{_logdir}/%{name}/,g' \
    -e 's,temp/,/tmp/,g' \
    config/main.inc.php.dist
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_logdir}/%{name}
cp -a config/db.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/db.inc.php
cp -a config/db.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/db.inc.php.dist
cp -a config/main.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/main.inc.php
cp -a config/main.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/main.inc.php.dist
rm -rf config
rm -rf temp
rm -rf logs
cp -a * %{buildroot}%{_datadir}/%{name}

pushd %{buildroot}%{_datadir}/%{name}
rm -f CHANGELOG INSTALL UPGRADING LICENSE README
popd


cat <<EOF > README.urpmi

This package conforms to the Mandriva web applications policy:
http://wiki.mandriva.com/Policies/Web_Applications

It therefore differs from a standard installation in the following
ways:

* Logs are stored to /var/log/roundcubemail
* Temporary files are placed in /tmp
* Configuration files (main.inc.php and db.inc.php) are placed in
  /etc/roundcubemail

You will need to edit /etc/roundcubemail/main.inc.php and
/etc/roundcubemail/db.inc.php appropriately for your site before you
can use Roundcube. You must at least configure an appropriate mail
server and port in main.inc.php, and change the 
$rcmail_config['des_key'] setting. In db.inc.php you must configure
an appropriate database location and user; in the most simple
configuration, you would create a new user and database both named
'roundcubemail' on a MySQL server running on the same machine, give
the roundcubemail user full read/write access to the roundcubemail
database, and set db.inc.php appropriately. Roundcubemail ships with
an installer which can help you do all this, but it is disabled by
default for security reasons. You can enable it in main.inc.php by
setting the 'enable_installer' variable to 'true'. Then browse to
http://server/roundcubemail/installer to use the installer.
EOF

mkdir -p %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
Alias /%{name} %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Order allow,deny
    Allow from all
</Directory>

<Directory %{_datadir}/%{name}/SQL>
    Order deny,allow
    Deny from all
</Directory>

php_value suhosin.session.encrypt Off
EOF

%post
%if %mdkversion < 201010
%_post_webapp
%endif

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CHANGELOG README README.urpmi UPGRADING
%{_datadir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_logdir}/%{name}
# these store the default values, the installer refers to them
# no need to edit them so they're not tagged config - AdamW 2011/01
%{_sysconfdir}/%{name}/db.inc.php.dist
%{_sysconfdir}/%{name}/main.inc.php.dist
%config(noreplace) %{_sysconfdir}/%{name}/db.inc.php
%config(noreplace) %{_sysconfdir}/%{name}/main.inc.php
%config(noreplace) %{_webappconfdir}/%{name}.conf


%changelog
* Tue Apr 03 2012 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.2-1mdv2012.0
+ Revision: 789015
- 0.7.2

* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 1:0.7.1-1
+ Revision: 772794
- 0.7.1

* Thu Aug 25 2011 Oden Eriksson <oeriksson@mandriva.com> 1:0.5.4-1
+ Revision: 697053
- 0.5.4

* Fri Jun 17 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1:0.5.3-1
+ Revision: 685717
- 0.5.3

* Mon Apr 25 2011 Adam Williamson <awilliamson@mandriva.org> 1:0.5.2-1
+ Revision: 659054
- new release 0.5.2

* Wed Mar 02 2011 Adam Williamson <awilliamson@mandriva.org> 1:0.5.1-1
+ Revision: 641366
- new release 0.5.1
- drop php-pear-DB dep (superseded by MDB2)

* Thu Jan 27 2011 Adam Williamson <awilliamson@mandriva.org> 1:0.5-1
+ Revision: 633158
- new release 0.5
- update dependencies
- package .dist files for the installer
- drop the patch (merged upstream a while ago)

* Wed Nov 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.4.2-1mdv2011.0
+ Revision: 598346
- 0.4.2

  + Adam Williamson <awilliamson@mandriva.org>
    - add required suhosin config option to the apache config file
    - new release 0.4 beta

* Mon Mar 01 2010 Oden Eriksson <oeriksson@mandriva.com> 1:0.3.1-4mdv2010.1
+ Revision: 513034
- P0: security fix for CVE-2010-0464 (fedora)

* Sun Feb 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1:0.3.1-3mdv2010.1
+ Revision: 501716
- deny acces to the SQL directory
- install under %%{_datadir} instead of %%{_localstatedir}
- no need to version apache configuration file
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Thu Jan 21 2010 Adam Williamson <awilliamson@mandriva.org> 1:0.3.1-2mdv2010.1
+ Revision: 494702
- add some more explicit php-pear deps

* Sun Nov 08 2009 Frederik Himpe <fhimpe@mandriva.org> 1:0.3.1-1mdv2010.1
+ Revision: 463124
- Update to new version 0.3.1

* Sat Sep 26 2009 Frederik Himpe <fhimpe@mandriva.org> 1:0.3-1mdv2010.0
+ Revision: 449287
- Update to new version 0.3
- Requires php-gd, php-pspell and php-mcrypt (from Debian)
- Requires php-pear-Auth_SASL (used by SIEVE client)

* Mon May 25 2009 Frederik Himpe <fhimpe@mandriva.org> 1:0.2.2-1mdv2010.0
+ Revision: 379650
- update to new version 0.2.2

* Mon Mar 16 2009 Frederik Himpe <fhimpe@mandriva.org> 1:0.2.1-1mdv2009.1
+ Revision: 355585
- Update to new version 0.2.1
- Remove patch integrated upstream

* Wed Feb 11 2009 Adam Williamson <awilliamson@mandriva.org> 1:0.2-2mdv2009.1
+ Revision: 339327
- rediff the patch
- add upstream patch to fix CVE-2009-0413

* Fri Jan 23 2009 Adam Williamson <awilliamson@mandriva.org> 1:0.2-1mdv2009.1
+ Revision: 332693
- package installer/ (needed for the upgrade script) and UPGRADING doc file
- adjust the conditionals a bit for the filename
- new release 0.2 final

* Wed Oct 22 2008 Adam Williamson <awilliamson@mandriva.org> 1:0.2-0.beta.2mdv2009.1
+ Revision: 296537
- don't use the 'www' group (which apparently I invented...)
- fix the config file relocation for changed upstream implementation
- suggest php-pear-MDB2_Driver_mysql

* Tue Oct 21 2008 Adam Williamson <awilliamson@mandriva.org> 1:0.2-0.beta.1mdv2009.1
+ Revision: 296313
- update to new version 0.2-beta

* Mon May 12 2008 Adam Williamson <awilliamson@mandriva.org> 1:0.1.1-1mdv2009.0
+ Revision: 206481
- new release 0.1.1

* Tue Mar 18 2008 Adam Williamson <awilliamson@mandriva.org> 1:0.1-1mdv2008.1
+ Revision: 188649
- don't package the installer
- new release 0.1 final
- prettify pre-release conditionals
- clean spec a little

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Nov 09 2007 Adam Williamson <awilliamson@mandriva.org> 1:0.1-0.rc2.1mdv2008.1
+ Revision: 107158
- new release 0.1rc2

* Thu Jul 26 2007 Adam Williamson <awilliamson@mandriva.org> 1:0.1-0.rc1.4mdv2008.0
+ Revision: 55688
- correct tarball name
- update requirements to pull in all the necessary PHP stuff
- use the new 'pure GPL' tarball which doesn't include its own copies of various PHP libraries
- update license
- update description
- add some comments

* Sun Jun 17 2007 Adam Williamson <awilliamson@mandriva.org> 1:0.1-0.rc1.3mdv2008.0
+ Revision: 40586
- substantial cleanup following webapp policy

* Tue May 22 2007 Adam Williamson <awilliamson@mandriva.org> 1:0.1-0.rc1.2mdv2008.0
+ Revision: 29868
- don't wipe temp dir prior to install

* Tue May 22 2007 Adam Williamson <awilliamson@mandriva.org> 1:0.1-0.rc1.1mdv2008.0
+ Revision: 29856
- 0.1 rc1
- big spec clean based on squirrelmail spec


* Sat Feb 17 2007 Emmanuel Andry <eandry@mandriva.org> 0.1beta2-1mdv2007.0
+ Revision: 122166
- Import roundcubemail

