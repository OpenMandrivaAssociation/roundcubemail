%define mod_conf 	74_roundcubemail.conf
%define basedir 	/var/www/roundcubemail

%define	name		roundcubemail
%define	version		0.1
%define beta		rc1
%if beta
%define	release		%mkrel 0.%beta.4
%else
%define release		%mkrel 1
%endif

Summary:	A PHP-based webmail server
URL:		http://www.roundcube.net/
Name:		%{name}
Version:	%{version}
Release:	%{release}           
Group:		System/Servers
License:	GPLv2
# Use the -dep tarballs. These use system copies of the PHP stuff
# rather than including them, which is better for our purposes.
# - AdamW 2007/07
%if %beta
Source0:	http://downloads.sourceforge.net/roundcubemail/%{name}-%{version}-%{beta}-dep.tar.gz
%else
Source0:	http://downloads.sourceforge.net/roundcubemail/%{name}-%{version}-dep.tar.gz
%endif
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:	noarch
BuildRequires:	apache-devel pcre-devel rpm-helper
Requires:	apache-mod_php
Requires:	php-gettext
Requires:	php-iconv
Requires:	php-mbstring
Requires:	php-openssl
Requires:	php-session
Requires:	php-pear-DB_DataObject
Requires:	php-pear-DB_DataObject_FormBuilder
Requires:	php-pear-DB_NestedSet
Requires:	php-pear-DB_Pager
Requires:	php-pear-DB_QueryTool
Requires:	php-pear-DB_Table
Requires:	php-pear-Mail_Mime
Requires:	php-pear-Net_SMTP
Requires(post):   rpm-helper
Requires(postun): rpm-helper

%description
RoundCube Webmail is a browser-based multilingual IMAP client with an 
application-like user interface. It provides full functionality you 
expect from an e-mail client, including MIME support, address book, 
folder manipulation, message searching and spell checking. RoundCube 
Webmail is written in PHP and requires a MySQL or PostgreSQL database.
The user interface is fully skinnable using XHTML and CSS 2.

%prep
%if %beta
%setup -q -n %{name}-%{version}-%{beta}
%else
%setup -q
%endif

%build

%install
rm -rf $RPM_BUILD_ROOT
# tell it that we're moving the configuration files
perl -pi -e 's,config/main.inc.php,%{_sysconfdir}/%{name}/main.inc.php,g' program/include/main.inc
perl -pi -e 's,config/db.inc.php,%{_sysconfdir}/%{name}/db.inc.php,g' program/include/main.inc
# use systemwide log dir
perl -pi -e 's,logs/,%{_logdir}/%{name}/,g' config/main.inc.php.dist
# and temp dir
perl -pi -e 's,temp/,/tmp/,g' config/main.inc.php.dist
mkdir -p $RPM_BUILD_ROOT%{basedir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_logdir}/%{name}
cp -a config/db.inc.php.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/db.inc.php
cp -a config/main.inc.php.dist $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/main.inc.php
rm -rf config
rm -rf temp
rm -rf logs
cp -a * $RPM_BUILD_ROOT%{basedir}/
rm -f $RPM_BUILD_ROOT%{basedir}/CHANGELOG $RPM_BUILD_ROOT%{basedir}/INSTALL $RPM_BUILD_ROOT%{basedir}/UPGRADING $RPM_BUILD_ROOT%{basedir}/LICENSE $RPM_BUILD_ROOT%{basedir}/README

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
%_post_webapp

%postun
%_postun_webapp

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc %attr(-  root  root) CHANGELOG README README.urpmi
%{basedir}
%{_sysconfdir}/httpd/conf/webapps.d/%{mod_conf}
%dir %{_sysconfdir}/%{name}
%defattr(0775,root,www)
%{_logdir}/%{name}
%defattr(0640,root,www)
%config(noreplace) %{_sysconfdir}/%{name}/db.inc.php
%config(noreplace) %{_sysconfdir}/%{name}/main.inc.php
