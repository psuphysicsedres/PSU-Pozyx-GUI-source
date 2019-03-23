package com.psupozyx.app;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.stage.Stage;

import java.io.*;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.ResourceBundle;

public class ConsoleWindow implements Initializable {
    @FXML
    private Label console;

    private static Process pr;

    private static final int CHARACTERDISPLAYBUFFER = 30000;

    private String osName = System.getProperty("os.name");
    private String OS = osName.toLowerCase();

    void launchScript(String startMessage, String executable, String[] args) {
        if (startMessage != null) {
            console.setText(startMessage);
        }

        console.setText("Running " + executable + " on " + osName + '\n');
        new Thread(() -> {
            try {
                Controller controller = new Controller();
                String executableWithDirectory = "";
                if (isWindows()) {
                    executableWithDirectory += "/scripts/win/" + executable + "/" + executable + ".exe";
                }
                else if (isMac()) {
                    executableWithDirectory += "/build/exe.macosx-10.6-intel-3.6/" + executable + ".app";
                    Platform.runLater( () -> console.setText("Unfortunately your operating system is not yet supported.\n" +
                            "Please try again on a Windows device."));
                    throw new NotImplementedException();
                }
                else if (isUnix()) {
                    executableWithDirectory += "/scripts/unix/" + executable;
                }
                else {
                    console.setText("Unfortunately your operating system is not yet supported.\n" +
                            "Please try again on a Windows, Mac, or Linux device.");
                    throw new NotImplementedException();
                }

                // System.out.println(executableWithDirectory);
                String commandRoot = ConsoleWindow.class.getResource(executableWithDirectory).getPath();
                // System.out.println("Root: " + commandRoot);

                if(ConsoleWindow.class.getResource("ConsoleWindow.class").toString().startsWith("jar:")) {
                    // running inside the jar file
                    String jarPath = ConsoleWindow.class.getProtectionDomain().getCodeSource().getLocation().toString().replace("%20", " ");
                    // Platform.runLater( () -> console.setText("\nJarPath: " + jarPath+ "\n" + console.getText()));
                    Thread.sleep(300);
                    String appFolder = jarPath.substring(jarPath.indexOf("file:") + 6, jarPath.lastIndexOf("app") + 3);
                    // Platform.runLater( () -> console.setText("\nAppFolder: " + appFolder+ "\n" + console.getText()));
                    Thread.sleep(500);
                    commandRoot = appFolder + executableWithDirectory;
                }

                String[] command;
                if(args == null) command = new String[]{commandRoot};
                else {
                    List<String> list = new LinkedList<>(Arrays.asList(args));
                    list.add(0, commandRoot);
                    command = list.toArray(new String[list.size()]);
                }
                ProcessBuilder ps=new ProcessBuilder(command);

                ps.redirectErrorStream(true);
                if(pr != null) {
                    pr.destroy();
                }
                pr = ps.start();
                InputStream inputStream = pr.getInputStream();

                BufferedReader in = new BufferedReader(new InputStreamReader(inputStream), 2048);
                String line;
                String pooledOutput;

                // read python script output
                while ((line = in.readLine()) != null) {

                    pooledOutput = line + '\n' + console.getText();
                    if(pooledOutput.length() >= CHARACTERDISPLAYBUFFER) {
                        pooledOutput = pooledOutput.substring(0, CHARACTERDISPLAYBUFFER);
                    }
                    final String finalOutput = pooledOutput;
                    Platform.runLater( () -> console.setText(finalOutput));
                }
                pr.waitFor();

                in.close();
            } catch (IOException | InterruptedException e) {
                Platform.runLater( () -> console.setText(e.toString() + "\n" + console.getText()));
                e.printStackTrace();
            }
        }).start();

    }

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        System.out.println("initialized");
    }

    void terminateProcess() {
        System.out.println("destroying");
        if (pr != null) {
            //pr = Runtime.getRuntime().exec("taskkill /F /IM 1D._ranging.exe");
            pr.destroy();
        }
        //Runtime.getRuntime().addShutdownHook(new Thread() {
           // @Override
            //public void run() {
              //  System.out.println("inside add shutdown hook");
            //}
        //});

    }



    private boolean isWindows() {
        return (OS.contains("win"));
    }

    private boolean isMac() {
        return (OS.contains("mac"));
    }

    private boolean isUnix() {
        return (OS.contains("nix") || OS.contains("nux") || OS.indexOf("aix") > 0 );
    }
}
