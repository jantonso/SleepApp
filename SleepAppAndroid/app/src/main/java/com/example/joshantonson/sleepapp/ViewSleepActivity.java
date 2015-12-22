package com.example.joshantonson.sleepapp;

import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.graphics.Color;
import android.os.AsyncTask;
import android.provider.Settings;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AbsoluteLayout;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.jjoe64.graphview.DefaultLabelFormatter;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.BarGraphSeries;
import com.jjoe64.graphview.series.DataPoint;

import java.text.DecimalFormat;


public class ViewSleepActivity extends ActionBarActivity {

    private String session_number;
    private String android_id;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_sleep);

        Intent myIntent = getIntent();
        //session_number = myIntent.getStringExtra("session_number");
        // currently just demoing for a given session (will only work for myself as the user)
        session_number = "3";

        android_id = Settings.Secure.getString(getApplicationContext().getContentResolver(),
                Settings.Secure.ANDROID_ID);

        android_id = "96e2404550ebf3cc";

        Log.d("TAG","http://totemic-tower-91423.appspot.com/getmovements/?user_name="
                + android_id + "&session_number=" + session_number );

        final Button back = (Button) findViewById(R.id.back);
        back.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Switch back to home screen
                Intent intent = new Intent(v.getContext(), MainActivity.class);
                startActivity(intent);
            }
        });

        new GetSleepTask()
                .execute("http://totemic-tower-91423.appspot.com/getmovements/?user_name="
                        + android_id + "&session_number=" + session_number);
    }

    // Fetch the movement data from the db
    private class GetSleepTask extends AsyncTask<String, Void, String> {
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
                Log.d("TAG", json.toString());

                int number_of_windows = json.getInt("number_of_windows");
                Log.d("TAG", "Number of windows: " + number_of_windows);
                JSONArray window_movements = json.getJSONArray("window_movements");
                Log.d("TAG", "window_movements: " + window_movements.toString());
                JSONArray time_data = json.getJSONArray("time_data");
                Log.d("TAG", "time_data: " + time_data.toString());

                GraphView graph = (GraphView) findViewById(R.id.graph);

                Log.d("TAG", "length: " + window_movements.length());

                // Create the bar chart to display movement events and predicted labels

                // Compress movement data so that it fits on the screen
                int index = 0;
                int numPoints = number_of_windows * 60;
                DataPoint[] d = new DataPoint[numPoints];
                for (int i = 0; i < 600*number_of_windows; i+= 600) {
                    for (int j = i; j < i+600; j+=10) {
                        double currentMax = 0.0;
                        for (int k = 0; k < 10; k++) {
                            if (window_movements.getDouble(j+k) > currentMax) {
                                currentMax = window_movements.getDouble(j+k);
                            }
                        }
                        d[index] = new DataPoint(index, currentMax);
                        index+=1;
                    }
                }
                BarGraphSeries<DataPoint> series = new BarGraphSeries<DataPoint>(d);

                graph.addSeries(series);
                series.setColor(Color.rgb(115, 0, 115));

                graph.setTitle("Sleep pattern for previous night of sleep");

                graph.getGridLabelRenderer().setHorizontalAxisTitle("20 minute bins");
                graph.getGridLabelRenderer().setVerticalAxisTitle("Movement level (normalized)");

                // y labels
                graph.getViewport().setYAxisBoundsManual(true);
                graph.getViewport().setMinY(0.0);
                graph.getViewport().setMaxY(1.0);

                graph.getGridLabelRenderer().setPadding(35);

                // x labels
                graph.getViewport().setMinX(0);
                graph.getViewport().setMaxX(numPoints);
                graph.getViewport().setXAxisBoundsManual(true);

                graph.getGridLabelRenderer().setNumHorizontalLabels(number_of_windows+1);

                // want the x labels to be 0,1,2,3,4,5,6...number of windows
                graph.getGridLabelRenderer().setLabelFormatter(new DefaultLabelFormatter() {
                    @Override
                    public String formatLabel(double value, boolean isValueX) {
                        if (isValueX) {
                            // show normal x values
                            return super.formatLabel(value/60, isValueX);
                        } else {
                            // show normal y values
                            return super.formatLabel(value, isValueX);
                        }
                    }
                });

                // These were the labels generated by my classifier for this given session
                // Ideally, would make a call to the server to fetch classifer results... but
                // this provides a good demo of the functionality
                String[] labels = {"r","a","a","a","w","r","a","a","w","a","a","a","a","a","a","a",
                        "w","r","a","a","a","a","a","a","a","w"};
                int rtotal = 0;
                int wtotal = 0;
                int atotal = 0;

                // Add each of the labels to the graph
                AbsoluteLayout al = (AbsoluteLayout) findViewById(R.id.al);
                for (int j = 0; j < number_of_windows; j++) {
                    TextView newView = new TextView(getApplicationContext());
                    newView.setText(labels[j]);
                    if (labels[j].equals("w")) {
                        // red
                        newView.setTextColor(Color.rgb(212, 36, 54));
                        wtotal++;
                    } else if (labels[j].equals("r")) {
                        // blue
                        newView.setTextColor(Color.rgb(64, 153, 255));
                        rtotal++;
                    } else {
                        // green
                        newView.setTextColor(Color.rgb(0, 128, 0));
                        atotal++;
                    }

                    newView.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 110 + 83 * j, 100));
                    al.addView(newView);
                }

                al.removeView((TextView) findViewById(R.id.header));

                // Add information about time spent asleep, awake, number of time woken up etc.
                TextView timeAsleep = new TextView(getApplicationContext());
                TextView timeRestless = new TextView(getApplicationContext());
                TextView numTimesWokenUp = new TextView(getApplicationContext());

                // Limit float values to 2 decimal points
                DecimalFormat df = new DecimalFormat();
                df.setMaximumFractionDigits(2);

                timeAsleep.setText("Time asleep: " + df.format(atotal*20/60.0) + " hours");
                timeRestless.setText("Time restless: " + df.format(rtotal*20/60.0) + " hours");
                numTimesWokenUp.setText("Number of times woken up: " + wtotal);

                timeAsleep.setTextColor(Color.BLACK);
                timeRestless.setTextColor(Color.BLACK);
                numTimesWokenUp.setTextColor(Color.BLACK);

                timeAsleep.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 10, 10));
                timeRestless.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 10, 40));
                numTimesWokenUp.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 10, 70));

                al.addView(timeAsleep);
                al.addView(timeRestless);
                al.addView(numTimesWokenUp);
            } catch (JSONException e) {
                Log.d("TAG", "JSON EXCEPTION....");
            }
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_view_sleep, menu);
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
}
