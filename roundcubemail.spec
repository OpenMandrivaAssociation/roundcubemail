%global __requires_exclude pear\\(vendor/autoload.php\\)|pear\\(xmlapi.php\\)
## pear(xmlapi.php) may need to be packaged, but for the time being a bug has been filed

%global  php_inidir    %{_sysconfdir}/php.d

# Paths. Do not include trailing slash
%global roundcube %{_datadir}/roundcubemail
%global roundcube_plugins %{roundcube}/plugins
%global roundcube_conf %{_sysconfdir}/roundcubemail
%global roundcube_log %{_logdir}/roundcubemail
%global roundcube_lib %{_localstatedir}/lib/roundcubemail

Name:		roundcubemail
Version:	1.1.1
Release:	1
Summary:	Round Cube Webmail is a browser-based multilingual IMAP client
Group:		System/Servers
License:	GPLv3
# Use the -dep tarballs. These use system copies of the PHP stuff
# rather than including them, which is better for our purposes.
# - AdamW 2007/07
URL:		http://www.roundcube.net/
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:        roundcubemail.conf
Source2:	roundcubemail.logrotate
Source100:	roundcubemail.rpmlintrc
# Elegantly handle removal of moxieplayer Flash binary in tinymce
# media plugin (see "Drop precompiled flash" in %%prep)
Patch0:		roundcubemail-1.1.1-no_swf.patch
Epoch:		1
Requires:	apache-mod_php
Requires:	php-gd
Requires:	php-gettext
Requires:	php-iconv
Requires:	php-mbstring
Requires:	php-openssl
Requires:	php-session
Requires:	php-pdo_mysql
Requires:	php-pear-Auth_SASL
Requires:	php-pear-Mail_Mime
Requires:	php-pear-Mail_mimeDecode
Requires:	php-pear-Net_SMTP
Requires:	php-pear-Net_LDAP2
Requires:	php-pear-Net_Sieve
Requires:	php-pear-Net_Socket
Requires:	php-pear-MDB2
Requires:	php-pear-Net_IDNA2
Requires(pre):	php-pear >= 1.9.0
Requires:	php-xml
Requires:	iRony
Requires:	php-pear-Crypt_GPG
# The installer suggests the use of these, but they're not
# required - AdamW 2011/01
Recommends:	php-fileinfo
Recommends:	php-intl
Recommends:	php-pear-MDB2_Driver_mysql
Recommends:	php-zip
BuildArch:	noarch

%description
RoundCube Webmail is a browser-based multilingual IMAP client with an 
application-like user interface. It provides full functionality you 
expect from an e-mail client, including MIME support, address book, 
folder manipulation, message searching and spell checking.
RoundCube Webmail is written in PHP and requires a database: MariaDB,
PostgreSQL and SQLite are known to work.
The user interface is fully skinnable using XHTML and CSS 2.

%prep
%setup -q
%patch0 -p1

# remove any reference to sqlite in config file so people don't mistakely
# assume it works
sed -i '/sqlite/d' config/defaults.inc.php
sed -i 's/\r//' SQL/mssql.initial.sql

# Drop precompiled flash
find . -type f -name '*.swf' | xargs rm -f

# Wipe bbcode plugin from bundled TinyMCE to make doubleplus sure we cannot
# be vulnerable to CVE-2012-4230, unaddressed upstream
echo "CVE-2012-4230: removing tinymce bbcode plugin, check path if this fails."
test -d program/js/*mce/plugins/bbcode && rm -rf program/js/*mce/plugins/bbcode || exit 1


%build

%install
install -d %{buildroot}%{roundcube}
cp -pr ./* %{buildroot}%{roundcube}
cp -a ./.htaccess %{buildroot}%{roundcube}/.htaccess
# Remove settings from .htaccess we don't want
sed -i \
    -e '/memory_limit/d' \
    -e '/post_max_size/d' \
    -e '/upload_max_filesize/d' \
    %{buildroot}%{roundcube}/.htaccess

rm -rf %{buildroot}%{roundcube}/installer

mkdir -p %{buildroot}%{_webappconfdir}
cp -pr %SOURCE1 %{buildroot}%{_webappconfdir}


mkdir -p %{buildroot}%{roundcube_conf}
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cp -pr %SOURCE2 %{buildroot}%{_sysconfdir}/logrotate.d/roundcubemail

mkdir -p %{buildroot}%{roundcube_lib}/plugins/enigma
mkdir -p %{buildroot}%{roundcube_log}

# use dist files as config files
mv %{buildroot}%{roundcube}/config/config.inc.php.sample %{buildroot}%{roundcube_conf}/config.inc.php
mv %{buildroot}%{roundcube}/config/defaults.inc.php %{buildroot}%{roundcube_conf}/defaults.inc.php
# keep any other config files too
mv %{buildroot}%{roundcube}/config/* %{buildroot}%{roundcube_conf}/
rm -rf %{buildroot}%{roundcube}/config
rm -rf %{buildroot}%{roundcube}/logs
rm -rf %{buildroot}%{roundcube}/temp

pushd %{buildroot}%{roundcube}
ln -s ../../..%{roundcube_conf} config
ln -s ../../..%{roundcube_log} logs
ln -s ../../..%{roundcube_lib} temp
popd

# Enigma
mv %{buildroot}%{roundcube_plugins}/enigma/config.inc.php.dist %{buildroot}%{roundcube_conf}/enigma.inc.php
rm -rf %{buildroot}%{roundcube_plugins}/enigma/config.inc.php
pushd %{buildroot}%{roundcube_plugins}/enigma
ln -s ../../../../..%{roundcube_conf}/enigma.inc.php config.inc.php
rm -rf home/
ln -s ../../../../..%{roundcube_lib}/plugins/enigma/ home
popd
mkdir -p %{buildroot}%{roundcube_lib}/plugins/enigma

# ACL plugin
mv %{buildroot}%{roundcube_plugins}/acl/config.inc.php.dist %{buildroot}%{roundcube_conf}/acl.inc.php
rm -rf %{buildroot}%{roundcube_plugins}/acl/config.inc.php
pushd %{buildroot}%{roundcube_plugins}/acl/
ln -s ../../../../..%{roundcube_conf}/acl.inc.php config.inc.php
popd

# Managesieve plugin
mv %{buildroot}%{roundcube_plugins}/managesieve/config.inc.php.dist %{buildroot}%{roundcube_conf}/managesieve.inc.php
pushd %{buildroot}%{roundcube_plugins}/managesieve/
ln -s ../../../../..%{roundcube_conf}/managesieve.inc.php config.inc.php
popd

# Password plugin
mv %{buildroot}%{roundcube_plugins}/password/config.inc.php.dist %{buildroot}%{roundcube_conf}/password.inc.php
pushd %{buildroot}%{roundcube_plugins}/password/
ln -s ../../../../..%{roundcube_conf}/password.inc.php config.inc.php
popd

# clean up the buildroot
rm -rf %{buildroot}%{roundcube}/{CHANGELOG,INSTALL,LICENSE,README,UPGRADING,SQL}

# Fix anything executable that does not have a shebang
for file in `find %{buildroot}/%{roundcube} -type f -perm /a+x`; do
    [ -z "`head -n 1 $file | grep \"^#!/\"`" ] && chmod -v 644 $file
done

# Find files with a shebang that do not have executable permissions
for file in `find %{buildroot}/%{roundcube} -type f ! -perm /a+x`; do
    [ ! -z "`head -n 1 $file | grep \"^#!/\"`" ] && chmod -v 755 $file
done

# Find files that have non-standard-executable-perm
find %{buildroot}/%{roundcube} -type f -perm /g+wx -exec chmod -v g-w {} \;

# Find files that are not readable
find %{buildroot}/%{roundcube} -type f ! -perm /go+r -exec chmod -v go+r {} \;

#
# Exclude the following external libraries
#
# php-pear-Net-IDNA2
rm -rf %{buildroot}/%{roundcube}/program/lib/Net/IDNA2/ \
    %{buildroot}/%{roundcube}/program/lib/Net/IDNA2.php
# php-pear-Net-SMTP
rm -rf %{buildroot}/%{roundcube}/program/lib/Net/SMTP.php
# php-pear-Net-Socket
rm -rf %{buildroot}/%{roundcube}/program/lib/Net/Socket.php
# php-pear-Mail
rm -rf %{buildroot}/%{roundcube}/program/lib/Mail/
# php-pear-MDB2
rm -rf %{buildroot}/%{roundcube}/program/lib/MDB2/ \
    %{buildroot}/%{roundcube}/program/lib/MDB2.php
# php-pear
rm -rf %{buildroot}/%{roundcube}/program/lib/PEAR.php \
    %{buildroot}/%{roundcube}/program/lib/PEAR5.php
# php-pear-Net-Sieve
rm -rf %{buildroot}/%{roundcube_plugins}/managesieve/lib/Net


%pre
# needed if you have kolab installed
if [ -f "/etc/roundcubemail/kolab.inc.php" ]; then
    mv /etc/roundcubemail/kolab.inc.php /etc/roundcubemail/libkolab.inc.php
fi

if [ -L %{roundcube_plugins}/enigma/home -a ! -d %{roundcube_plugins}/enigma/home ]; then
    rm -rf %{roundcube_plugins}/enigma/home >/dev/null 2>&1 || :
fi



%post
# replace default des string in config file for better security
function makedesstr () {
    chars=(0 1 2 3 4 5 6 7 8 9 a b c d e f g h i j k l m n o p q r s t u v w x y z A
    B C D E F G H I J K L M N O P Q R S T U V W X Y Z)

    max=${#chars[*]}

    for i in `seq 1 24`; do
        let rand=${RANDOM}%%${max}
        str="${str}${chars[$rand]}"
    done
    echo $str
}

sed -i "s/rcmail-\!24ByteDESkey\*Str/`makedesstr`/" /etc/roundcubemail/defaults.inc.php || : &> /dev/null

sed -i -r -e "s/.*(\s*define\(\s*'RCMAIL_VERSION'\s*,\s*').*('\);)/\1%{version}-%{release}\2/g" \
    %{roundcube}/program/include/iniset.php || :

if [ -f "%{php_inidir}/99_apcu.ini" ]; then
    if [ ! -z "`grep ^apcu.enabled=1 %{php_inidir}/99_apc.ini`" ]; then

        /sbin/systemctl condrestart %{httpd_name}

    fi
fi

/usr/share/roundcubemail/bin/updatedb.sh \
    --dir /usr/share/doc/roundcubemail/SQL/ \
    --package roundcube || : \
    >/dev/null 2>&1

exit 0

cat > README.urpmi <<EOF
WARNING: when upgrading from <= 0.9.5 the old configuration files named 
main.inc.php and db.inc.php are now deprecated and should be replaced 
with one single config.inc.php file. Run the ./bin/update.sh script to 
get this conversion done or manually merge the files. 
Also see the UPGRADE file in the doc section.
NOTE: the new config.inc.php should only contain options that differ 
from the ones listed in defaults.inc.php.
EOF

%files
%doc CHANGELOG INSTALL LICENSE README.md SQL UPGRADING
%{_datadir}/%{name}
%dir %{_sysconfdir}/%{name}
%attr(0755,root,apache)%{_logdir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
# Lets write out them specifically, so we can see when additional files are added (or deleted)
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/acl.inc.php
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/defaults.inc.php
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/config.inc.php
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/enigma.inc.php
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/managesieve.inc.php
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/mimetypes.php
%attr(0640,root,apache)%config(noreplace) %{_sysconfdir}/%{name}/password.inc.php
%config(noreplace) %{_webappconfdir}/%{name}.conf
%attr(0775,root,apache) %dir %{_localstatedir}/lib/roundcubemail
%attr(0770,root,apache) %dir %{_localstatedir}/lib/roundcubemail/plugins
%attr(0770,root,apache) %dir %{_localstatedir}/lib/roundcubemail/plugins/enigma


