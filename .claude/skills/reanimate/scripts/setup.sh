#!/bin/sh
# Install the Haskell toolchain for reanimate on Debian/Ubuntu (run as root).
# Uses apt's GHC + cabal (no downloads.haskell.org needed) and Hackage over HTTPS.
set -e
if ! command -v ghc >/dev/null || ! command -v cabal >/dev/null; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ghc cabal-install zlib1g-dev librsvg2-bin potrace imagemagick ffmpeg
fi
CFG=$HOME/.cabal/config
[ -f "$CFG" ] || cabal user-config init >/dev/null
# HTTPS index + Hackage's root keys (old cabal builds lack them and refuse the index)
sed -i 's#url: http://hackage.haskell.org/#url: https://hackage.haskell.org/#' "$CFG"
if ! grep -q '^  root-keys:' "$CFG"; then
  KEYS=fe331502606802feac15e514d9b9ea83fee8b6ffef71335479a2e68d84adc6b0,1ea9ba32c526d1cc91ab5e5bd364ec5e9e8cb67179a471872f6e26f0ae773d42,0a5c7ea47cd1b15f01f5f51a33adda7e655bc0f0b0615baa8e271f4c3351e21d,51f0161b906011b52c6613376b1ae937670da69322113a246a09f807c62f6921,c7de58fc6a224b92b5b513f26fbb8b370f2d97c7cfe0075a951314a55734be93,d26e46f3b631aae1433b89379a6c68bd417eb5d1c408f0643dcc07757fece522
  sed -i "s#^  -- root-keys:#  secure: True\n  root-keys: $KEYS#; s#^  -- key-threshold: 3#  key-threshold: 3#" "$CFG"
fi
cabal update
echo "ready: $(ghc --numeric-version) / cabal $(cabal --numeric-version)"
