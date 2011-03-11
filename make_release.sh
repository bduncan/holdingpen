#!/bin/bash

set -e
REL=${1:?missing version}

# Update the changelog and tag the release.
git-dch  --debian-tag='%(version)s' --new-version=${REL} --release
git commit debian/changelog -m "Release: ${REL}"
git tag -s ${REL} -m "Release: ${REL}"

# Now build an RPM and a DEB.
./setup.py bdist_rpm
git-buildpackage
