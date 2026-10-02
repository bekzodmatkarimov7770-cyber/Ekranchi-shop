import fs from 'fs';
import { Config } from '@remotion/cli/config';

// Bulut muhitida oldindan o'rnatilgan Chromium bor; bo'lmasa Remotion o'zinikini yuklab oladi.
const shell = process.env.REMOTION_BROWSER || '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
if (fs.existsSync(shell)) Config.setBrowserExecutable(shell);
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setChromiumOpenGlRenderer('swangle');
