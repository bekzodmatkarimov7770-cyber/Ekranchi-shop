package uz.ekranchi.bola;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.IOException;

/**
 * Do'kon sahifasi APK ichida (assets/www) turadi va sayt manzili ostida ochiladi: internet sekin bo'lsa ham darhol chiqadi.
 * Narx va qoldiq har doim serverdan (/api) keladi.
 */
public class MainActivity extends Activity {
    private static final String HOST = "ekranchi-shop.vercel.app";
    private static final String HOME = "https://" + HOST + "/market.html?app=1";

    private static final int REQ_LOCATION = 1, REQ_NOTIFY = 2;

    private WebView web;
    private GeolocationPermissions.Callback geoCallback;
    private String geoOrigin;

    /** Sahifadan chaqiriladi: kirish tokeni va ko'rilgan holatlar fon tekshiruvi uchun saqlanadi. */
    private final class Bridge {
        @JavascriptInterface
        public void setToken(String token) {
            boolean has = token != null && !token.isEmpty();
            getSharedPreferences(OrderCheckService.PREFS, MODE_PRIVATE).edit()
                .putString("token", has ? token : "").apply();
            if (!has) {
                getSharedPreferences(OrderCheckService.PREFS, MODE_PRIVATE).edit().remove("seen").apply();
                OrderCheckService.cancel(MainActivity.this);
                return;
            }
            OrderCheckService.schedule(MainActivity.this);
            runOnUiThread(() -> {
                if (Build.VERSION.SDK_INT >= 33
                        && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIFY);
                }
            });
        }

        @JavascriptInterface
        public void setSeen(String json) {
            // ilova ichida ko'rsatilgan o'zgarish uchun bildirishnoma ikkinchi marta chiqmasin
            getSharedPreferences(OrderCheckService.PREFS, MODE_PRIVATE).edit().putString("seen", json).apply();
        }
    }

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        web.setBackgroundColor(0xFFF3F5F2);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);   // savat va katalog keshi shu yerda saqlanadi
        s.setDatabaseEnabled(true);
        s.setTextZoom(100);
        s.setUserAgentString(s.getUserAgentString() + " EkranchiApp/1.0");
        s.setGeolocationEnabled(true);
        web.addJavascriptInterface(new Bridge(), "EkranchiApp");

        // Joylashuv: sahifa so'raganda (mijoz tugmani bosganda) Android ruxsati so'raladi
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                    callback.invoke(origin, true, false);
                    return;
                }
                geoCallback = callback;
                geoOrigin = origin;
                requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION}, REQ_LOCATION);
            }
        });

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if ("https".equals(u.getScheme()) && HOST.equals(u.getHost())) return false;
                // Telegram, telefon raqami va boshqa havolalar o'z ilovasida ochiladi
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
                return true;
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                String path = u.getPath();
                if (!"GET".equals(request.getMethod()) || !HOST.equals(u.getHost()) || path == null
                        || path.startsWith("/api") || path.contains("..")) return null;
                try {
                    return new WebResourceResponse(mime(path), "utf-8", getAssets().open("www" + path));
                } catch (IOException notBundled) {
                    return null;   // APK ichida yo'q fayl internetdan olinadi
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) showOffline();
            }
        });

        if (state != null) web.restoreState(state);
        else web.loadUrl("profile".equals(getIntent().getStringExtra("tab")) ? HOME + "#profile" : HOME);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        // bildirishnoma bosilganda ochiq turgan ilova Profil bo'limiga o'tadi
        if ("profile".equals(intent.getStringExtra("tab"))) {
            web.evaluateJavascript("window.__appOpen && window.__appOpen('profile')", null);
        }
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(code, permissions, results);
        if (code != REQ_LOCATION || geoCallback == null) return;
        boolean granted = false;
        for (int r : results) granted |= r == PackageManager.PERMISSION_GRANTED;
        geoCallback.invoke(geoOrigin, granted, false);
        geoCallback = null;
    }

    private static String mime(String path) {
        if (path.endsWith(".html")) return "text/html";
        if (path.endsWith(".js")) return "application/javascript";
        if (path.endsWith(".json")) return "application/json";
        if (path.endsWith(".svg")) return "image/svg+xml";
        if (path.endsWith(".css")) return "text/css";
        if (path.endsWith(".png")) return "image/png";
        return "application/octet-stream";
    }

    private void showOffline() {
        String html = "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
            + "<body style='margin:0;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;"
            + "font-family:sans-serif;background:#F3F5F2;color:#15201E;text-align:center;padding:24px;box-sizing:border-box'>"
            + "<h2 style='margin:0 0 8px'>Internet yoʻq</h2>"
            + "<p style='margin:0 0 20px;color:#62716D'>Aloqani tekshirib, qayta urinib koʻring.</p>"
            + "<a href='" + HOME + "' style='background:#123F38;color:#fff;text-decoration:none;padding:14px 28px;"
            + "border-radius:14px;font-weight:600'>Qayta ochish</a></body>";
        web.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        // Sahifa o'zi hal qiladi: oynani yopadi yoki bosh sahifaga qaytadi; qaytadigan joy qolmasa ilova yopiladi
        web.evaluateJavascript("window.__appBack ? window.__appBack() : false", handled -> {
            if (!"true".equals(handled)) finish();
        });
    }
}
