package uz.ekranchi.bola;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Do'kon sahifasini ilova ichida ochadi: narx va qoldiq saytdan keladi, shuning uchun ilovani yangilash shart emas. */
public class MainActivity extends Activity {
    private static final String HOST = "ekranchi-shop.vercel.app";
    private static final String HOME = "https://" + HOST + "/market.html?app=1";

    private WebView web;

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
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) showOffline();
            }
        });

        if (state != null) web.restoreState(state);
        else web.loadUrl(HOME);
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
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
