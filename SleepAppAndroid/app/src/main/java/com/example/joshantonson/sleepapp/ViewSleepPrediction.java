package com.example.joshantonson.sleepapp;

import android.content.Intent;
import android.graphics.Color;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AbsoluteLayout;
import android.widget.Button;
import android.widget.TextView;

import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.BarGraphSeries;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;

import java.text.DecimalFormat;
import java.util.ArrayList;


public class ViewSleepPrediction extends ActionBarActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_sleep_prediction);

        final Button back = (Button) findViewById(R.id.back);
        back.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Switch back to home screen
                Intent intent = new Intent(v.getContext(), MainActivity.class);
                startActivity(intent);
            }
        });

        Intent myIntent = getIntent();

        GraphView graph = (GraphView) findViewById(R.id.graph);

        // These were all of the generated labels for myself
        // Ideally, would fetch these from server side... but this provides a good demo of functionality
        String[][] labels = {{"r", "a", "a", "a", "a", "w", "r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w"},
                {"r", "a", "a", "a", "w", "r", "a","a", "w", "a", "a", "a", "a", "a", "a", "a", "w", "r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w", "r"},
                {"a", "a", "a", "a", "a", "a", "a","a", "w", "r","r", "a","a","a", "w", "a","a","a","a","a","a","a", "w"},
                {"a","a","a", "w", "r","r","r","r","r", "a", "a", "a", "a", "a", "a", "w", "a", "w", "r","r","r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w"},
                {"r","r","a","a", "w", "a", "w", "r","r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a","a","w", "a", "w"},
                {"r", "a", "a", "a", "a", "a", "a","a", "w", "a","a", "w", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w"},
                {"r","r", "a", "a", "a", "a", "a", "a", "w"},
                {"a", "a", "a", "a", "a", "a","a","a", "w", "a", "a", "a", "a", "a", "a","a","a", "w", "r","r","r","r", "a","a","a","w", "a","a","a","a"},
                {"a", "a", "a", "a", "a","a", "a", "a", "a", "a", "w", "r","r","r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w", "r"},
                {"r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w", "a","a", "w", "r","r"},
                {"r","r","r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w", "r"},
                {"r","r", "a", "a", "w", "a","a","a","a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a",},
                {"r","r", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a","a","a", "w"},
                {"r","r", "a", "a", "a", "a", "a", "a","a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "w", "a"}
        };

        int maxLength = 0;
        ArrayList<Integer> lengths = new ArrayList<Integer>();
        int[] rs = new int[14];
        int[] ws = new int[14];
        int[] as = new int[14];

        for (int i = 0; i < labels.length; i++) {
            if (labels[i].length > maxLength) {
                maxLength = labels[i].length;
            }
            lengths.add(labels[i].length);
        }

        int[] numPoints = new int[maxLength];
        double[] totalScore = new double[maxLength];

        // Add up the weights of each label for each i-th index of 20-minute windows
        for (int j = 0; j < labels.length; j++) {
            for (int k = 0; k < labels[j].length; k++) {
                String label = labels[j][k];
                if (label.equals("w")) {
                    ws[j] ++;
                    totalScore[k] += 4.0;
                } else if (label.equals("r")) {
                    totalScore[k] += 1.0;
                    rs[j] ++;
                } else {
                    as[j] ++;
                }
                numPoints[k] ++;
            }
        }
        // Divide by the number of windows in the i-th index
        DataPoint[] d = new DataPoint[maxLength];
        for (int i = 0; i < maxLength; i++) {
            d[i] = new DataPoint(i, totalScore[i] / numPoints[i]);
        }

        // Create a new line graph to display predicted sleep/wake patterns

        Log.d("TAG", d.toString());
        LineGraphSeries<DataPoint> series = new LineGraphSeries<>(d);

        graph.addSeries(series);

        graph.setTitle("Predicted sleep pattern");

        graph.getGridLabelRenderer().setHorizontalAxisTitle("20 minute bins");
        graph.getGridLabelRenderer().setVerticalAxisTitle("Movement level");

        // y labels
        graph.getViewport().setYAxisBoundsManual(true);
        graph.getViewport().setMinY(0.0);
        graph.getViewport().setMaxY(2.0);

        graph.getGridLabelRenderer().setNumHorizontalLabels(maxLength+1);

        AbsoluteLayout al = (AbsoluteLayout) findViewById(R.id.al);

        int as_total = 0;
        int ws_total = 0;
        int rs_total = 0;

        for (int i = 0; i < 14; i ++ ) {
            as_total += as[i];
            rs_total += rs[i];
            ws_total += ws[i];
        }

        double rs_avg = ((double)rs_total) / 14.0;
        double ws_avg = ((double)ws_total) / 14.0;
        double as_avg = ((double)as_total) / 14.0;

        // Add information about time spent asleep, awake, number of time woken up etc.
        TextView timeAsleep = new TextView(getApplicationContext());
        TextView timeRestless = new TextView(getApplicationContext());
        TextView numTimesWokenUp = new TextView(getApplicationContext());

        // Limit float values to 2 decimal points
        DecimalFormat df = new DecimalFormat();
        df.setMaximumFractionDigits(2);

        timeAsleep.setText("avg time asleep: " + df.format(as_avg*20/60.0) + " hours");
        timeRestless.setText("avg time restless: " + df.format(rs_avg*20/60.0) + " hours");
        numTimesWokenUp.setText("avg number of times woken up: " + df.format(ws_avg));

        timeAsleep.setTextColor(Color.BLACK);
        timeRestless.setTextColor(Color.BLACK);
        numTimesWokenUp.setTextColor(Color.BLACK);

        timeAsleep.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 10, 10));
        timeRestless.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 10, 40));
        numTimesWokenUp.setLayoutParams(new AbsoluteLayout.LayoutParams(AbsoluteLayout.LayoutParams.WRAP_CONTENT, AbsoluteLayout.LayoutParams.WRAP_CONTENT, 10, 70));

        al.addView(timeAsleep);
        al.addView(timeRestless);
        al.addView(numTimesWokenUp);
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_view_sleep_prediction, menu);
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
