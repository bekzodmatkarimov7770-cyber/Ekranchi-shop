---
name: reanimate
description: Make math-style 2D vector animations (3Blue1Brown/manim-like) in Haskell with the reanimate library, rendered to MP4, GIF or WebM. Use when the user asks for an animation, explainer, diagram animation or animated chart written with reanimate or Haskell, or names reanimate.
---

# reanimate

reanimate (https://github.com/reanimate/reanimate, public domain) turns a Haskell
`Animation` into a self-contained executable that renders itself. Frames are SVG;
ffmpeg encodes them.

## 1. Toolchain

Check `ghc --version` and `cabal --version`. If either is missing, or `cabal update`
fails with "does not have enough signatures", run (as root):

```bash
sh "<skill base directory>/scripts/setup.sh"
```

It installs GHC 9.4 + cabal from apt, ffmpeg, rsvg, potrace, imagemagick, switches
Hackage to HTTPS and sets Hackage's root keys. Report anything else missing instead
of installing it. LaTeX (`texlive`) is only needed for `latex`/`latexAlign`; ask
before installing it (it is large). The first build compiles ~100 packages
(20–40 min); later builds reuse `~/.cabal/store`. Run it in the background.

## 2. Project

Put each animation in its own folder, e.g. `animations/<name>/`:

`<name>.cabal`
```cabal
cabal-version: 2.4
name: <name>
version: 0.1
executable <name>
  main-is: Main.hs
  build-depends: base, reanimate, reanimate-svg, text, linear
  default-language: Haskell2010
  ghc-options: -threaded -rtsopts
```

`Main.hs`
```haskell
{-# LANGUAGE OverloadedStrings #-}
import Reanimate

main :: IO ()
main = reanimate $ addStatic (mkBackground "white") $
  mapA (withStrokeWidth 0.05 . withFillOpacity 0) $
  animate $ \t -> partialSvg t (pathify (mkCircle 2))
```

## 3. Render

```bash
cabal build
cabal run <name> -- render --target out.mp4 --width 1280 --height 720 --fps 30
```

Other flags: `--format mp4|gif|webm`, `--preset quick|medium|high|youtube|gif`,
`--raster none|auto|rsvg|inkscape|imagemagick` (use `rsvg` if text or gradients
render wrong). Check frames before a full render: do a quick low-res pass
(`--preset quick`, or `--width 640 --height 360 --fps 15`), then pull a still with
`ffmpeg -ss 1.5 -i out.mp4 -frames:v 1 frame.png` and look at the PNG.
`cabal run <name> -- check` reports which external tools reanimate can find.

## 4. Key ideas

- Canvas: 16 × 9 units, origin at the centre, Y up.
- `SVG` = one picture; `Animation` = SVG over time (`Duration` in seconds).
- Build: `staticFrame d svg`, `animate (\t -> ...)` (t from 0 to 1), `mkText`,
  `mkCircle`, `mkRect`, `mkLine`, `mkGroup`, `translate x y`, `scale`, `rotate`,
  `withFillColor`, `withStrokeColor`, `center`.
- Combine: `a `seqA` b` (one after another), `a `parA` b` (together),
  `a `andThen` b` (b after a, a's last frame stays), `playThenReverseA`,
  `setDuration`, `signalA (curveS 2)` for easing, `pauseAtEnd`.
- Higher level: `Reanimate.Scene` (`scene`, `play`, `newSpriteSVG`, `fork`,
  `tweenVar`) for multi-object choreography; `Reanimate.Transition` for fades.
- Examples to copy from: https://github.com/reanimate/reanimate/tree/master/examples
- API: https://hackage.haskell.org/package/reanimate/docs/Reanimate.html

## 5. Deliver

Give the user the rendered file's path and the source folder. Keep `dist-newstyle/`
out of git.
