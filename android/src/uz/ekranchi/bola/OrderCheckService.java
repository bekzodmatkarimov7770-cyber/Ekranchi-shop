package uz.ekranchi.bola;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.job.JobInfo;
import android.app.job.JobParameters;
import android.app.job.JobScheduler;
import android.app.job.JobService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Ilova yopiq bo'lsa ham buyurtma holatini vaqti-vaqti bilan (Android ruxsat bergan eng qisqa oraliq: ~15 daqiqa)
 * tekshiradi va holat o'zgargan bo'lsa bildirishnoma chiqaradi. Firebase kerak emas.
 */
public class OrderCheckService extends JobService {
    static final String PREFS = "ekranchi";
    static final String CHANNEL = "orders";
    private static final int JOB_ID = 1;
    private static final String API = "https://ekranchi-shop.vercel.app/api/index?app=me";

    static void schedule(Context c) {
        JobScheduler js = (JobScheduler) c.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        if (js == null || js.getPendingJob(JOB_ID) != null) return;
        js.schedule(new JobInfo.Builder(JOB_ID, new ComponentName(c, OrderCheckService.class))
            .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
            .setPeriodic(15 * 60 * 1000L)
            .setPersisted(true)
            .build());
    }

    static void cancel(Context c) {
        JobScheduler js = (JobScheduler) c.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        if (js != null) js.cancel(JOB_ID);
    }

    @Override
    public boolean onStartJob(final JobParameters params) {
        new Thread(() -> {
            try { check(); } catch (Exception ignored) { }
            jobFinished(params, false);
        }).start();
        return true;
    }

    @Override
    public boolean onStopJob(JobParameters params) {
        return false;
    }

    private void check() throws Exception {
        SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String token = prefs.getString("token", "");
        if (token.isEmpty()) { cancel(this); return; }

        HttpURLConnection con = (HttpURLConnection) new URL(API).openConnection();
        con.setConnectTimeout(15000);
        con.setReadTimeout(15000);
        con.setRequestProperty("X-App-Token", token);
        int code = con.getResponseCode();
        if (code == 401) {   // sessiya tugagan: tekshirishni to'xtatamiz
            prefs.edit().remove("token").apply();
            cancel(this);
            return;
        }
        if (code != 200) return;
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        try (InputStream in = con.getInputStream()) {
            byte[] chunk = new byte[8192];
            for (int n; (n = in.read(chunk)) > 0; ) buf.write(chunk, 0, n);
        }
        JSONArray orders = new JSONObject(buf.toString("UTF-8")).optJSONArray("orders");
        if (orders == null) return;

        String seenRaw = prefs.getString("seen", null);
        JSONObject seen = seenRaw == null ? null : new JSONObject(seenRaw);
        JSONObject now = new JSONObject();
        for (int i = 0; i < orders.length(); i++) {
            JSONObject o = orders.getJSONObject(i);
            String id = o.optString("id"), status = o.optString("status");
            now.put(id, status);
            // birinchi tekshiruvda (seen yo'q) faqat eslab qolamiz, eski buyurtmalar uchun xabar chiqarmaymiz
            if (seen != null && seen.has(id) && !status.equals(seen.optString(id))) {
                notifyStatus(id, status, o.optString("status_label"));
            }
        }
        prefs.edit().putString("seen", now.toString()).apply();
    }

    private void notifyStatus(String id, String status, String label) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm == null) return;
        nm.createNotificationChannel(new NotificationChannel(CHANNEL, "Buyurtma holati", NotificationManager.IMPORTANCE_HIGH));
        String text;
        switch (status) {
            case "tasdiqlandi": text = "Buyurtmangiz tasdiqlandi, tayyorlanmoqda."; break;
            case "yuborildi": text = "Buyurtmangiz yuborildi, tez orada yetib boradi."; break;
            case "yetkazildi": text = "Buyurtmangiz yetkazildi. Xaridingiz uchun rahmat!"; break;
            case "bekor": text = "Buyurtmangiz bekor qilindi."; break;
            default: text = "Holat: " + label;
        }
        Intent open = new Intent(this, MainActivity.class)
            .putExtra("tab", "profile")
            .addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(this, id.hashCode(), open,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_notify)
            .setColor(0xFF123F38)
            .setContentTitle("Buyurtma #" + id)
            .setContentText(text)
            .setStyle(new Notification.BigTextStyle().bigText(text))
            .setAutoCancel(true)
            .setContentIntent(pi)
            .build();
        nm.notify(id.hashCode(), n);
    }
}
