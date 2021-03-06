Name     : clear-containers-docker
Version  : 1.9.1
Release  : 16
URL      : https://github.com/docker/docker/archive/v1.9.1.tar.gz
Source0  : https://github.com/docker/docker/archive/v1.9.1.tar.gz
Summary  : the open-source application container engine
Group    : Development/Tools
License  : Apache-2.0

Patch1   : 0001-Add-go-md2man-sources.patch
Patch2   : 0001-Drop-socket-group-docker.patch

Patch401 : 0001-Dockerfile-add-kvmtool-and-linux-container-for-clr-e.patch
Patch402 : 0002-Clear-Containers-for-Docker-Engine-v1.9.1.patch
Patch403 : 0003-Clear-Linux-VERSION-and-default-exec-driver.patch
Patch5   : 0005-Fix-none-network-in-clr-driver.patch
Patch6   : 0006-fix-compilation-errors-with-btrfs-progs-4.5.patch
Patch7   : 0007-Add-pacrunner-call-for-proxy-resolution.patch
Patch8   : 0008-Disable-systemd-networkd.patch

BuildRequires : go
BuildRequires : glibc-staticdev
BuildRequires : pkgconfig(sqlite3)
BuildRequires : pkgconfig(devmapper)
BuildRequires : btrfs-progs-devel
Requires : kvmtool
Requires : linux-container
Conflicts : docker

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# This matches v1.9.1 tag/tarball from https://github.com/docker/docker/releases
%define commit_id a34a1d5-clear-containers

%description
Docker Core Engine

%prep
%setup -q -n docker-%{version}
%patch1 -p1
%if "%{_vendor}" != "clr"
%patch2 -p1
%endif
%patch401 -p1
%patch402 -p1
%patch403 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

%build
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary
GOPATH="$(pwd)/.gopath:$(pwd)/vendor" go build github.com/cpuguy83/go-md2man
export PATH="$PATH:$(pwd)"
./man/md2man-all.sh

%install
rm -rf %{buildroot}
install -D ./bundles/latest/dynbinary/docker %{buildroot}%{_bindir}/docker
install -D ./bundles/latest/dynbinary/dockerinit %{buildroot}%{_prefix}/lib/docker/dockerinit
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}%{_prefix}/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}%{_prefix}/lib/systemd/system/docker.socket
install -d %{buildroot}%{_mandir}/man1 %{buildroot}%{_mandir}/man5
install ./man/man1/* %{buildroot}%{_mandir}/man1
install ./man/man5/* %{buildroot}%{_mandir}/man5
mkdir -p %{buildroot}/usr/lib/systemd/system/sockets.target.wants
ln -s ../docker.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/multi-user.target.wants
ln -s ../docker.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/docker.service
chmod -x %{buildroot}/%{_mandir}/man*/*

%files
%defattr(-,root,root,-)
%dir /usr/lib/docker
%dir /usr/lib/systemd/system/multi-user.target.wants
%{_bindir}/docker
%{_prefix}/lib/docker/dockerinit
%{_prefix}/lib/systemd/system/*.socket
%{_prefix}/lib/systemd/system/*.service
%{_prefix}/lib/systemd/system/*/*.socket
%{_prefix}/lib/systemd/system/*/*.service
%{_mandir}/man*/*
