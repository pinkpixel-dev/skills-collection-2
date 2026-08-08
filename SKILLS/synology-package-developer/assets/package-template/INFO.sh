#!/bin/bash
set -eu

. /pkgscripts-ng/include/pkg_util.sh

package="__PACKAGE_ID__"
version="__VERSION__"
os_min_ver="__OS_MIN_VER__"
displayname="__DISPLAY_NAME__"
description="__DESCRIPTION__"
arch="__ARCH__"
maintainer="__MAINTAINER__"
thirdparty="yes"

[ "$(caller)" != "0 NULL" ] && return 0
pkg_dump_info
