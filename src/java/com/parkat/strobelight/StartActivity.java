package com.parkat.strobelight;

import java.util.Random;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraCharacteristics;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.Button;
import android.Manifest;

public class StartActivity extends Activity {
    private boolean isStrobing = false;
    private CameraManager cameraManager;
    private String cameraId;
    private Handler handler = new Handler();
    private boolean isFlashOn = false;
    private Random rand;

    private Button button;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        this.rand = new Random();
        super.onCreate(savedInstanceState);
        Log.e(">>>", "Starting app");

        setContentView(R.layout.activity_main);
        
        //Button button = new Button(this);
        //button.setText("Start Strobe");
        button = findViewById(R.id.button1);
        
        // Initialize camera manager
        cameraManager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
        try {
            cameraId = cameraManager.getCameraIdList()[0];
            CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(cameraId);
            Integer maxLevelObj = characteristics.get(CameraCharacteristics.FLASH_INFO_STRENGTH_MAXIMUM_LEVEL);
            // TODO ...
        } catch (Exception e) {
            Log.e(">>>", "Failed to get camera: " + e.toString());
        }
        
        button.setOnClickListener(v -> {
            isStrobing = !isStrobing;
            button.setText(isStrobing ? "Stop Strobe" : "Start Strobe");
            
            if (isStrobing) {
                startStrobe();
            } else {
                stopStrobe();
            }
        });
        
        //setContentView(button);
        Log.e(">>>", "Setup complete");
    }
    
    private void startStrobe() {
        handler.postDelayed(() -> {
            if (isStrobing) {
                try {
                    isFlashOn = !isFlashOn;
                    double delay = this.rand.nextGaussian() * 1 + 2;
                    if (this.rand.nextGaussian() > 0.6) {
                        delay = 300.0;
                    }
                    if (delay < 1)
                        delay = 1;
                    double intensity = this.rand.nextGaussian() * 7 + 4;
                    if (delay < 1)
                        delay = 1;
                    cameraManager.setTorchMode(cameraId, isFlashOn);
                    // TODO a better way?
                    //if (isFlashOn) {
                    //    cameraManager.turnOnTorchWithStrengthLevel(cameraId, currentLevel);
                    //} else {
                    //    cameraManager.setTorchMode(cameraId, isFlashOn);
                    //}
                    handler.postDelayed(this::startStrobe, (int)delay);
                } catch (Exception e) {
                    Log.e(">>>", "Strobe error: " + e.toString());
                }
            }
        }, 1);
    }
    
    private void stopStrobe() {
        isStrobing = false;
        try {
            cameraManager.setTorchMode(cameraId, false);
        } catch (Exception e) {
            Log.e(">>>", "Error stopping strobe: " + e.toString());
        }
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        stopStrobe();
    }
}
