package com.example.demo;

import java.io.*;

public class RunPython {
    public static void main(String[] args) {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(
                    "C:/Users/Sara/AppData/Local/Programs/Python/Python39/python.exe",
                    "C:/Users/Sara/Desktop/Devops/third/main.py");

            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Read output from Python script
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

            // Wait for the process to finish
            int exitCode = process.waitFor();
            System.out.println("Exited with code: " + exitCode);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
