%define	name	roundcubemail
%define	version	0.1beta2
%define	release	%mkrel 1

%define sqm_path	%{_var}/www/htdocs/%{name}
%define b_sqm_path	$RPM_BUILD_ROOT/%{sqm_path}
#%define sqm_doc		/%{_defaultdocdir}/roundcube
#%define b_sqm_doc	$RPM_BUILD_ROOT/%{sqm_doc}

Summary:        a web-mailer written in php4
URL:            http://www.roundcube.net/
Name:		%{name}
Version:	%{version}
Release:	%{release}           
Group:          System/Servers
License:        GPL
Source0:        %{name}-%{version}.tar.bz2
Patch0:		%{name}-0.1-beta2.2.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArchitectures:            noarch
BuildRequires:  apache-devel pcre-devel
Requires:       apache-mod_php
Requires:       php-gettext
Requires:       php-iconv
Requires:       php-mbstring
Requires:       php-openssl
Requires:       php-session


%description
RoundCube Webmail is a browser-based multilingual IMAP client with an application-like user interface. It provides full functionality you expect from an e-mail client, including MIME support, address book, folder manipulation, message searching and spell checking. RoundCube Webmail is written in PHP and requires the MySQL database. The user interface is fully skinnable using XHTML and CSS 2.

%prep
%setup -q

%build

%install
install -d -m 0755 %{b_sqm_path}
cp -a * %{b_sqm_path}/
cp -a config/db.inc.php.dist %{b_sqm_path}/config/db.inc.php
cp -a config/main.inc.php.dist %{b_sqm_path}/config/main.inc.php

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc %attr(-  root  root) CHANGELOG INSTALL UPGRADING LICENSE README
%dir %{sqm_path}
%dir %{sqm_path}/config
%config(noreplace) %{sqm_path}/config/.htaccess
%config(noreplace) %{sqm_path}/config/db.inc.php
%config(noreplace) %{sqm_path}/config/main.inc.php
%{sqm_path}/config/*.dist
%{sqm_path}/[^c]*



