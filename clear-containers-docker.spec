Name     : clear-containers-docker
Version  : 1.11.0
Release  : 11
URL      : https://github.com/docker/docker/archive/v1.11.0-rc4.tar.gz
Source0  : https://github.com/docker/docker/archive/v1.11.0-rc4.tar.gz
Summary  : the open-source application container engine
Group    : Development/Tools
License  : Apache-2.0
BuildRequires : go
BuildRequires : glibc-staticdev
BuildRequires : pkgconfig(sqlite3)
BuildRequires : pkgconfig(devmapper)
BuildRequires : btrfs-progs-devel
BuildRequires : gzip
Requires : kvmtool
Requires : linux-container
Requires : gzip
Requires : containerd
Requires : runc
Conflicts : docker
# Patch1   : 0001-Add-go-md2man-sources.patch
# Patch2   : 0001-Drop-socket-group-docker.patch
# Patch401 : 0001-Dockerfile-add-kvmtool-and-linux-container-for-clr-e.patch
# Patch402 : 0002-Clear-Containers-for-Docker-Engine-v1.9.1.patch
# Patch403 : 0003-Clear-Linux-VERSION-and-default-exec-driver.patch
# Patch5   : 0005-Fix-none-network-in-clr-driver.patch
# Patch6   : 0006-fix-compilation-errors-with-btrfs-progs-4.5.patch

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global gopath /usr/lib/golang
%global library_path github.com/docker/

%global commit_id f5e2b400ec7b96538df80f728eb08c5afa07d85f
%global revision rc4

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n docker-%{version}-%{revision}
#%patch1 -p1
#%if "%{_vendor}" != "clr"
#%patch2 -p1
#%endif
# %patch401 -p1
# %patch402 -p1
# %patch403 -p1
# %patch5 -p1
# %patch6 -p1

%build
mkdir -p src/github.com/docker/
ln -s $(pwd) src/github.com/docker/docker
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/%{_bindir}
install -p -m 755 bundles/latest/dynbinary/docker-%{version}-%{revision} %{buildroot}%{_bindir}/docker

# install containerd
ln -s /usr/bin/containerd %{buildroot}/%{_bindir}/docker-containerd
ln -s /usr/bin/containerd-shim %{buildroot}/%{_bindir}/docker-containerd-shim
ln -s /usr/bin/containerd-ctr %{buildroot}/%{_bindir}/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/%{_bindir}/docker-runc

# install systemd unit files
install -m 0644 -D ./contrib/init/systemd/docker.service %{buildroot}%{_prefix}/lib/systemd/system/docker.service
install -m 0644 -D ./contrib/init/systemd/docker.socket %{buildroot}%{_prefix}/lib/systemd/system/docker.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/sockets.target.wants
ln -s ../docker.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/multi-user.target.wants
ln -s ../docker.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/docker.service

# add init scripts
install -d %{buildroot}/etc/sysconfig
install -d %{buildroot}/%{_initddir}

%files
%defattr(-,root,root,-)
%{_bindir}/docker
%{_bindir}/docker-containerd
%{_bindir}/docker-containerd-shim
%{_bindir}/docker-containerd-ctr
%{_bindir}/docker-runc
%{_prefix}/lib/systemd/system/*.socket
%{_prefix}/lib/systemd/system/*.service
%{_prefix}/lib/systemd/system/*/*.socket
%{_prefix}/lib/systemd/system/*/*.service
