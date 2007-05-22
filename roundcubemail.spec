%define mod_conf 	74_roundcubemail.conf
%define basedir 	/var/www/roundcubemail

%define	name		roundcubemail
%define	version		0.1
%define beta		rc1
%if beta
%define	release		%mkrel 0.%beta.1
%else
%define release		%mkrel 1
%endif

Summary:	A PHP-based webmail server
URL:		http://www.roundcube.net/
Name:		%{name}
Version:	%{version}
Release:	%{release}           
Group:		System/Servers
License:	GPL
%if %beta
Source0:	http://downloads.sourceforge.net/roundcubemail/%{name}-%{version}-%{beta}.tar.bz2
%else
Source0:	http://downloads.sourceforge.net/roundcubemail/%{name}-%{version}.tar.bz2
%endif
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:	noarch
BuildRequires:	apache-devel pcre-devel
Requires:	apache-mod_php
Requires:	php-gettext
Requires:	php-iconv
Requires:	php-mbstring
Requires:	php-openssl
Requires:	php-session


%description
RoundCube Webmail is a browser-based multilingual IMAP client with an 
application-like user interface. It provides full functionality you 
expect from an e-mail client, including MIME support, address book, 
folder manipulation, message searching and spell checking. RoundCube 
Webmail is written in PHP and requires the MySQL database. The user 
interface is fully skinnable using XHTML and CSS 2.

%prep
%if %beta
%setup -q -n %{name}-%{version}-%{beta}
%else
%setup -q
%endif

%build

%install
install -d -m 0755 $RPM_BUILD_ROOT%{basedir}
rm -rf temp
cp -a * $RPM_BUILD_ROOT%{basedir}/
rm -f $RPM_BUILD_ROOT%{basedir}/CHANGELOG $RPM_BUILD_ROOT%{basedir}/INSTALL $RPM_BUILD_ROOT%{basedir}/UPGRADING $RPM_BUILD_ROOT%{basedir}/LICENSE $RPM_BUILD_ROOT%{basedir}/README
cp -a config/db.inc.php.dist $RPM_BUILD_ROOT%{basedir}/config/db.inc.php
cp -a config/main.inc.php.dist $RPM_BUILD_ROOT%{basedir}/config/main.inc.php

cat <<EOF > %{mod_conf}

Alias /%{name} %{basedir}

<Directory %{basedir}>

    Allow from all

</Directory>

EOF

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{mod_conf}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc %attr(-  root  root) CHANGELOG README
%dir %{basedir}
%dir %{basedir}/config
%config(noreplace) %{basedir}/config/.htaccess
%config(noreplace) %{basedir}/config/db.inc.php
%config(noreplace) %{basedir}/config/main.inc.php
%{basedir}/config/*.dist
%{basedir}/[^c]*
%{_sysconfdir}/httpd/conf/webapps.d/%{mod_conf}
