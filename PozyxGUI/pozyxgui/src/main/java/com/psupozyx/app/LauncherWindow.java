package com.psupozyx.app;

import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

import java.io.*;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.ResourceBundle;

public class LauncherWindow implements Initializable {

    private static ConsoleWindow consoleController;

    private static Process pr;

    private String osName = System.getProperty("os.name");
    private String OS = osName.toLowerCase();

    public void launchConsole() {
        new Controller().launchConsoleLogging("console_printing", true, null, "Console Window");
    }

    public void launchGraphing() {
        launchScript("graphing_realtime_2D",null);
    }


    void launchScript(String executable, String[] args) {
        new Thread(() -> {
            try {
                String executableWithDirectory = "";
                if (isWindows()) {
                    executableWithDirectory += "/scripts/win/" + executable + "/" + executable + ".exe";
                }
                else if (isMac()) {
                    executableWithDirectory += "/build/exe.macosx-10.6-intel-3.6/" + executable + ".app";
                    throw new NotImplementedException();
                }
                else if (isUnix()) {
                    executableWithDirectory += "/scripts/unix/" + executable + "/" + executable;
                }
                else {
                    throw new NotImplementedException();
                }

                // System.out.println(executableWithDirectory);
                String commandRoot = ConsoleWindow.class.getResource(executableWithDirectory).getPath();
                // System.out.println("Root: " + commandRoot);

                if(ProcessRunner.class.getResource("ProcessRunner.class").toString().startsWith("jar:")) {
                    // running inside the jar file
                    String jarPath = ProcessRunner.class.getProtectionDomain().getCodeSource().getLocation().toString().replace("%20", " ");
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

                pr = ps.start();

                pr.waitFor();

            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        System.out.println("Initialized");
    }

    void setConsoleController() {
        FXMLLoader loader = new FXMLLoader(Controller.class.getClassLoader().getResource("fxml/console_window.fxml"));
        consoleController = loader.getController();
    }

    public void terminateProcess() {
        pr.exitValue();
        if (pr != null) {
            pr.destroy();
        }
        System.out.println("destroying");
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
