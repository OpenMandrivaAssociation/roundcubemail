%define mod_conf 	74_roundcubemail.conf
%define basedir 	/var/www/roundcubemail

%define rel		2
%define beta		0
%if %beta
%define	release		%mkrel 0.%beta.%rel
%define distname	%name-%version-%beta-dep.tar.gz
%define dirname		%name-%version-%beta-dep
%else
%define release		%mkrel %rel
%define distname	%name-%version-dep.tar.gz
%define dirname		%name-%version-dep
%endif

Summary:	A PHP-based webmail server
URL:		http://www.roundcube.net/
Name:		roundcubemail
Version:	0.3.1
Release:	%{release}           
Group:		System/Servers
License:	GPLv2
# Use the -dep tarballs. These use system copies of the PHP stuff
# rather than including them, which is better for our purposes.
# - AdamW 2007/07
Source0:	http://downloads.sourceforge.net/roundcubemail/%{distname}
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:	noarch
#BuildRequires:	apache-devel pcre-devel rpm-helper
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
Requires:	php-pear-DB
Requires:	php-pear-Mail_Mime
Requires:	php-pear-Net_SMTP
Requires:	php-pear-Net_LDAP2
Requires:	php-pear-MDB2
# Most people will probably use mysql, but you can use sqlite or
# pgsql, so not a hard require - AdamW 2008/10
Suggests:	php-pear-MDB2_Driver_mysql

Requires(post):		rpm-helper
Requires(postun):	rpm-helper

%description
RoundCube Webmail is a browser-based multilingual IMAP client with an 
application-like user interface. It provides full functionality you 
expect from an e-mail client, including MIME support, address book, 
folder manipulation, message searching and spell checking. RoundCube 
Webmail is written in PHP and requires a MySQL or PostgreSQL database.
The user interface is fully skinnable using XHTML and CSS 2.

%prep
%setup -q -n %{dirname}

%build

%install
rm -rf %{buildroot}
# tell it that we're moving the configuration files
sed -i -e "s,INSTALL_PATH . 'config','%{_sysconfdir}/%{name}',g" program/include/iniset.php
# use systemwide log dir
sed -i -e 's,logs/,%{_logdir}/%{name}/,g' config/main.inc.php.dist
# and temp dir
sed -i -e 's,temp/,/tmp/,g' config/main.inc.php.dist
mkdir -p %{buildroot}%{basedir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_logdir}/%{name}
cp -a config/db.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/db.inc.php
cp -a config/main.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/main.inc.php
rm -rf config
rm -rf temp
rm -rf logs
cp -a * %{buildroot}%{basedir}/
rm -f %{buildroot}%{basedir}/CHANGELOG %{buildroot}%{basedir}/INSTALL %{buildroot}%{basedir}/UPGRADING %{buildroot}%{basedir}/LICENSE %{buildroot}%{basedir}/README

cat <<EOF > %{mod_conf}

Alias /%{name} %{basedir}

<Directory %{basedir}>

    Allow from all

</Directory>

EOF

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
database, and set db.inc.php appropriately.

EOF

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{mod_conf}

%post
%{_post_webapp}

%postun
%{_postun_webapp}

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root)
%doc %attr(-  root  root) CHANGELOG README README.urpmi UPGRADING
%{basedir}
%{_sysconfdir}/httpd/conf/webapps.d/%{mod_conf}
%dir %{_sysconfdir}/%{name}
%defattr(0775,root,root)
%{_logdir}/%{name}
%defattr(0644,root,root)
%config(noreplace) %{_sysconfdir}/%{name}/db.inc.php
%config(noreplace) %{_sysconfdir}/%{name}/main.inc.php

