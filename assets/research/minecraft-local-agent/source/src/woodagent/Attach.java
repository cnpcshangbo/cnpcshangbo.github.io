package woodagent;
import com.sun.tools.attach.VirtualMachine;
import java.nio.file.Path;
public final class Attach {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: Attach <Minecraft PID> <agent directory>");
        Path dir = Path.of(args[1]).toAbsolutePath();
        VirtualMachine vm = VirtualMachine.attach(args[0]);
        try { vm.loadAgent(dir.resolve("wood-agent.jar").toString(), dir.toString()); }
        finally { vm.detach(); }
        System.out.println("Local controller attached in idle mode. Read status before starting.");
    }
}
