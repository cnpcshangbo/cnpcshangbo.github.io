package woodagent;

import java.lang.instrument.Instrumentation;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Path;

/** Attaches without transforming Minecraft classes. Reloads only our own controller. */
public final class Bootstrap {
    private static AutoCloseable controller;
    private static URLClassLoader loader;
    public static synchronized void agentmain(String argument, Instrumentation ignored) throws Exception {
        if (controller != null) controller.close();
        if (loader != null) loader.close();
        Path directory = Path.of(argument).toAbsolutePath();
        loader = new URLClassLoader(new URL[]{directory.resolve("wood-agent.jar").toUri().toURL()}, Bootstrap.class.getClassLoader()) {
            @Override protected synchronized Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
                if (name.startsWith("woodagent.") && !name.equals("woodagent.Bootstrap")) {
                    Class<?> found = findLoadedClass(name);
                    if (found == null) found = findClass(name);
                    if (resolve) resolveClass(found);
                    return found;
                }
                return super.loadClass(name, resolve);
            }
        };
        controller = (AutoCloseable) loader.loadClass("woodagent.Controller")
            .getConstructor(Path.class).newInstance(directory);
    }
}
