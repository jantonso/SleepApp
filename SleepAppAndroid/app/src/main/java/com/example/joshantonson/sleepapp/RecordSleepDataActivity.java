package com.example.joshantonson.sleepapp;

import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.AsyncTask;
import android.os.Looper;
import android.os.PowerManager;
import android.provider.Settings;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.text.format.Time;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RelativeLayout;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;


public class RecordSleepDataActivity extends ActionBarActivity implements SensorEventListener{

    private SensorManager mSensorManager;
    private ArrayList<String> x_accs = new ArrayList<String>();
    private ArrayList<String> y_accs = new ArrayList<String>();
    private ArrayList<String> z_accs = new ArrayList<String>();
    private int sensorCounter = 0;
    private long lastSyncTime = System.currentTimeMillis();
    private int timeWindowSize = 60;
    private int sessionNumber;
    private String android_id;

    private PowerManager.WakeLock wakeLock;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_record_sleep_data);

        // Make it so that the app still runs if the phone sleeps
        PowerManager mgr = (PowerManager) getApplicationContext().getSystemService(Context.POWER_SERVICE);
        wakeLock = mgr.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyWakeLock");
        wakeLock.acquire();

        // user name = ANDROID_ID
        android_id = Settings.Secure.getString(getApplicationContext().getContentResolver(),
                Settings.Secure.ANDROID_ID);

        // Get the last session_number
        new GetSessionNumberTask()
            .execute("http://totemic-tower-91423.appspot.com/getsessionnumber/?user_name=" + android_id);

        final Button submit = (Button) findViewById(R.id.submit_data);
        submit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // In the background, post the sleep record to the db
                Toast toast = Toast.makeText(getApplicationContext(), "sending a new request...", Toast.LENGTH_LONG);
                toast.show();
                new SendDataTask().execute();
            }
        });

        // Register the sensor lister for the accelerometer
        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        mSensorManager.registerListener(this,
            mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
            SensorManager.SENSOR_DELAY_NORMAL);
    }

    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            sensorCounter += 1;
            // Vary sensorCounter to vary the rate at which we collect the sensor data
            // 20 == about once per 2 seconds, 10 == once per second, 1 == 5 times per second
            if (sensorCounter == 1) {
                sensorCounter = 0;
                x_accs.add(Float.toString(event.values[0]));
                y_accs.add(Float.toString(event.values[1]));
                z_accs.add(Float.toString(event.values[2]));
                if (System.currentTimeMillis() >= lastSyncTime + timeWindowSize*1000) {
                    lastSyncTime = System.currentTimeMillis();
                    // Send acc data to db
                    Log.d("TAG", "Sending acceleration data...");
                    new PostSleepDataTask().execute("accelerometer", x_accs.toString(),
                            y_accs.toString(), z_accs.toString(), Long.toString(System.currentTimeMillis()));
                    x_accs = new ArrayList<String>();
                    y_accs = new ArrayList<String>();
                    z_accs = new ArrayList<String>();
                }
            }
        // In the future could add support for gyroscope
        } else if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
            new PostSleepDataTask().execute("gyroscope", Float.toString(event.values[0]),
                Float.toString(event.values[1]), Float.toString(event.values[2]));
        }
    }

    // Get the last session number for the given user from db
    private class GetSessionNumberTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... params) {
            HttpClient httpclient = new DefaultHttpClient();
            HttpGet httpget = new HttpGet(params[0]);

            try {
                Log.d("TAG", "Http get request to app engine");
                HttpResponse response = httpclient.execute(httpget);
                Log.d("TAG", response.getStatusLine().toString());
                Log.d("TAG", response.getEntity().toString());
                Log.d("TAG", response.toString());
                String responseString = new BasicResponseHandler().handleResponse(response);
                return responseString;
            } catch (Exception e) {
                e.printStackTrace();
                return "failure";
            }
        }

        @Override
        protected void onPostExecute(String result) {
            try {
                JSONObject json = new JSONObject(result);

                // The new session number is the last one plus one
                sessionNumber = json.getInt("session_number") + 1;

            } catch (JSONException e) {
                sessionNumber = 0;
            }
        }
    }

    // This is called once every minute automatically
    private class PostSleepDataTask extends AsyncTask<String, Void, String> {

        @Override
        protected String doInBackground(String... params) {

            // Send the data up to the db
            HttpClient httpclient = new DefaultHttpClient();
            HttpPost httppost = new HttpPost("http://totemic-tower-91423.appspot.com/");

            List<NameValuePair> pairs = new ArrayList<NameValuePair>();
            pairs.add(new BasicNameValuePair("entry_type", "sleep_data"));
            pairs.add(new BasicNameValuePair("sensor_type", params[0]));
            pairs.add(new BasicNameValuePair("x_acc", params[1]));
            pairs.add(new BasicNameValuePair("y_acc", params[2]));
            pairs.add(new BasicNameValuePair("z_acc", params[3]));
            pairs.add(new BasicNameValuePair("time", params[4]));
            pairs.add(new BasicNameValuePair("user_name", android_id));
            pairs.add(new BasicNameValuePair("session_number", Integer.toString(sessionNumber)));

            try {
                httppost.setEntity(new UrlEncodedFormEntity(pairs));
                HttpResponse response = httpclient.execute(httppost);

                return "success";
            } catch (Exception e) {
                e.printStackTrace();
                return "failure";
            }
        }

        // onPostExecute displays the results of the AsyncTask.
        @Override
        protected void onPostExecute(String result) {
            Context context = getApplicationContext();
            if (result.equals("success")) {
                Log.d("TAG", "Success");
            } else{
                Toast toast = Toast.makeText(context, "Sleep data couldn't be saved...", Toast.LENGTH_LONG);
                toast.show();
            }
        }
    }

    // This is called only when the user clicks the Send Data button, so that they don't have to
    // wait one minute once they wake up
    private class SendDataTask extends AsyncTask<String, Void, String> {

        @Override
        protected String doInBackground(String... params) {

            // Send the data up to the db
            HttpClient httpclient = new DefaultHttpClient();
            HttpPost httppost = new HttpPost("http://totemic-tower-91423.appspot.com/");

            List<NameValuePair> pairs = new ArrayList<NameValuePair>();
            pairs.add(new BasicNameValuePair("entry_type", "sleep_data"));
            pairs.add(new BasicNameValuePair("sensor_type", "accelerometer"));
            pairs.add(new BasicNameValuePair("x_acc", x_accs.toString()));
            pairs.add(new BasicNameValuePair("y_acc", y_accs.toString()));
            pairs.add(new BasicNameValuePair("z_acc", z_accs.toString()));
            pairs.add(new BasicNameValuePair("time", lastSyncTime + "," + Long.toString(System.currentTimeMillis())));
            pairs.add(new BasicNameValuePair("user_name", android_id));
            pairs.add(new BasicNameValuePair("session_number", Integer.toString(sessionNumber)));

            x_accs = new ArrayList<String>();
            y_accs = new ArrayList<String>();
            z_accs = new ArrayList<String>();
            lastSyncTime = System.currentTimeMillis();

            try {
                Log.d("TAG", "Sending http post");
                httppost.setEntity(new UrlEncodedFormEntity(pairs));
                HttpResponse response = httpclient.execute(httppost);
                Log.d("TAG", response.getStatusLine().toString());

                Log.d("TAG", "success");

                return "success";
            } catch (Exception e) {
                e.printStackTrace();

                Log.d("TAG", "failure");
                return "failure";
            }
        }

        // onPostExecute displays the results of the AsyncTask.
        @Override
        protected void onPostExecute(String result) {
            Context context = getApplicationContext();
            if (result.equals("success")) {

                Log.d("TAG", "RELEASING THE LOCK DOG");
                wakeLock.release();

                // Switch to a new screen to record all the data
                Intent intent = new Intent(getApplicationContext(), ViewSleepActivity.class);
                intent.putExtra("session_number", Integer.toString(sessionNumber));

                startActivity(intent);
            } else{
                Toast toast = Toast.makeText(context, "Sleep data couldn't be saved...", Toast.LENGTH_LONG);
                toast.show();
            }
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_record_sleep_data, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }



    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d("TAG", "RELEASING THE LOCK DOG");
        wakeLock.release();

    }
}
