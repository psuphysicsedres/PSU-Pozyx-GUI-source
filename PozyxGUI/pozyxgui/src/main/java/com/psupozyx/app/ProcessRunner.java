package com.psupozyx.app;

import java.io.IOException;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;

public class ProcessRunner {
    // used for things like 2D graphing
    private static Process pr;

    private String osName = System.getProperty("os.name");
    private String OS = osName.toLowerCase();

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


    void terminateProcess() {
        System.out.println("destroying");
        if (pr != null) {
            pr.destroy();
        }
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
