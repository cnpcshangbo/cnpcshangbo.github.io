package woodagent;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.client.multiplayer.MultiPlayerGameMode;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;

/**
 * Temporarily owns progressive log mining without depending on mouse capture.
 * Every method must be called on the Minecraft client thread. The controller is
 * still responsible for tree validation, aiming, line of sight, and home limits.
 * No direct destroyBlock call or hand-built gameplay packet is used here.
 */
public final class BackgroundGameMode extends MultiPlayerGameMode implements AutoCloseable {
    private static final long OWNERSHIP_TTL = TimeUnit.MILLISECONDS.toNanos(750);
    private static final long TARGET_LIMIT = TimeUnit.SECONDS.toNanos(6);
    private static final List<Field> STATE_FIELDS = stateFields();

    private final Minecraft client;
    private final MultiPlayerGameMode original;
    private final ClientLevel expectedLevel;
    private final LocalPlayer expectedPlayer;
    private BlockPos target;
    private BlockPos timedOutTarget;
    private long leaseUntil, targetUntil;
    private int lastMiningTick = Integer.MIN_VALUE;
    private boolean workerCall, restored;

    private BackgroundGameMode(Minecraft client, MultiPlayerGameMode original,
                               ClientPacketListener connection) throws ReflectiveOperationException {
        super(client, connection);
        this.client = client;
        this.original = original;
        this.expectedLevel = client.level;
        this.expectedPlayer = client.player;
        copyState(original, this);
    }

    /** Install while idle. Refuses to wrap another mod or an already active dig. */
    public static BackgroundGameMode install(Minecraft client) throws ReflectiveOperationException {
        Objects.requireNonNull(client, "client");
        requireClientThread(client);
        if (!"26.3-rc-2".equals(client.getLaunchedVersion())) {
            throw new IllegalStateException("Background mining supports only Minecraft 26.3-rc-2");
        }
        if (client.player == null || client.level == null || !client.hasSingleplayerServer()) {
            throw new IllegalStateException("Open the intended singleplayer world before installing");
        }
        MultiPlayerGameMode original = client.gameMode;
        if (original == null || original.getClass() != MultiPlayerGameMode.class) {
            throw new IllegalStateException("Refusing to replace another game-mode wrapper");
        }
        if (original.isDestroying()) throw new IllegalStateException("Release the current dig before installing");
        ClientPacketListener connection = (ClientPacketListener) field("connection").get(original);
        BackgroundGameMode replacement = new BackgroundGameMode(client, original, connection);
        client.gameMode = replacement;
        return replacement;
    }

    /**
     * Own and progress a validated log target, at most once per player tick.
     * Repeated calls maintain a short lease; each target has a six-second limit.
     * A false result means no progress was made (including an already completed log).
     */
    public boolean mine(BlockPos pos, Direction face) {
        requireClientThread(client);
        Objects.requireNonNull(pos, "pos");
        Objects.requireNonNull(face, "face");
        expireOwnership();
        if (pos.equals(timedOutTarget)) {
            throw new IllegalStateException("Background mining target exceeded six seconds");
        }
        if (!usableContext() || getPlayerMode() != GameType.SURVIVAL || expectedPlayer.isUsingItem()) {
            releaseOwned();
            return false;
        }
        var miningState=expectedLevel.getBlockState(pos);
        boolean naturalLeaf=miningState.is(BlockTags.LEAVES) && miningState.hasProperty(BlockStateProperties.PERSISTENT)
            && !miningState.getValue(BlockStateProperties.PERSISTENT);
        if (!expectedLevel.isLoaded(pos) || (!miningState.is(BlockTags.LOGS) && !naturalLeaf)
            || expectedPlayer.getEyePosition().distanceTo(Vec3.atCenterOf(pos))
               > expectedPlayer.blockInteractionRange() - 0.1) {
            releaseOwned();
            return false;
        }
        long now = System.nanoTime();
        if (expectedPlayer.tickCount == lastMiningTick) return false;
        lastMiningTick = expectedPlayer.tickCount;

        boolean newTarget = !pos.equals(target);
        if (newTarget) {
            releaseOwned();
            target = pos.immutable();
            targetUntil = now + TARGET_LIMIT;
        }
        leaseUntil = now + OWNERSHIP_TTL;
        workerCall = true;
        try {
            // The ordinary game-mode methods own timing, prediction, tool wear,
            // carried-slot synchronization, and START/STOP mining packets.
            return newTarget ? super.startDestroyBlock(target, face)
                             : super.continueDestroyBlock(target, face);
        } catch (RuntimeException | Error failure) {
            releaseOwned();
            throw failure;
        } finally {
            workerCall = false;
        }
    }

    /** Must be used by the controller's release/stop path, not stopDestroyBlock(). */
    public void releaseOwned() {
        requireClientThread(client);
        target = null;
        timedOutTarget = null;
        leaseUntil = targetUntil = 0;
        boolean previousWorkerCall = workerCall;
        workerCall = true;
        try {
            if (client.level == expectedLevel && client.player == expectedPlayer) {
                super.stopDestroyBlock();
            }
        } finally {
            workerCall = previousWorkerCall;
        }
    }

    public boolean ownsTarget() {
        requireClientThread(client);
        expireOwnership();
        return target != null;
    }

    @Override public boolean startDestroyBlock(BlockPos pos, Direction direction) {
        if (!workerCall) {
            expireOwnership();
            if (target != null) return false;
        }
        return super.startDestroyBlock(pos, direction);
    }

    @Override public boolean continueDestroyBlock(BlockPos pos, Direction direction) {
        if (!workerCall) {
            expireOwnership();
            if (target != null) return false;
        }
        return super.continueDestroyBlock(pos, direction);
    }

    @Override public void stopDestroyBlock() {
        if (!workerCall) {
            expireOwnership();
            if (target != null) return;
        }
        super.stopDestroyBlock();
    }

    @Override public void tick() {
        expireOwnership();
        super.tick();
    }

    /** Restore the original instance with current mutable mode/slot state. */
    public void restore() throws ReflectiveOperationException {
        requireClientThread(client);
        if (restored) return;
        releaseOwned();
        // A reconnect may have installed its own new game mode. Never overwrite it.
        if (client.gameMode != this) {
            restored = true;
            return;
        }
        if (client.level != expectedLevel || client.player != expectedPlayer) {
            throw new IllegalStateException("World changed while background game mode remained installed");
        }
        copyState(this, original);
        client.gameMode = original;
        restored = true;
    }

    @Override public void close() throws ReflectiveOperationException { restore(); }

    private boolean usableContext() {
        return !restored && client.gameMode == this && client.level == expectedLevel
            && client.player == expectedPlayer && client.gui.screen() == null
            && !client.isPaused() && client.hasSingleplayerServer()
            && expectedPlayer.getHealth() > 12 && !expectedPlayer.isOnFire()
            && !expectedPlayer.isInWater() && !expectedPlayer.isInLava();
    }

    private void expireOwnership() {
        if (target == null || workerCall) return;
        long now = System.nanoTime();
        if (!usableContext() || now >= leaseUntil || now >= targetUntil) {
            BlockPos expired = now >= targetUntil ? target : null;
            releaseOwned();
            timedOutTarget = expired;
        }
    }

    private static void requireClientThread(Minecraft client) {
        if (!client.isSameThread()) throw new IllegalStateException("Call background game mode on the client thread");
    }

    private static Field field(String name) throws NoSuchFieldException {
        Field value = MultiPlayerGameMode.class.getDeclaredField(name);
        value.setAccessible(true);
        return value;
    }

    private static List<Field> stateFields() {
        List<Field> result = new ArrayList<>();
        for (Field field : MultiPlayerGameMode.class.getDeclaredFields()) {
            if (Modifier.isStatic(field.getModifiers())) continue;
            field.setAccessible(true);
            result.add(field);
        }
        return List.copyOf(result);
    }

    private static void copyState(MultiPlayerGameMode source, MultiPlayerGameMode destination)
        throws IllegalAccessException {
        // Validate every immutable reference before making any mutable copies.
        // Constructor bytecode confirms only minecraft and connection are final.
        for (Field field : STATE_FIELDS) {
            if (Modifier.isFinal(field.getModifiers()) && field.get(source) != field.get(destination)) {
                throw new IllegalStateException("Game-mode reference mismatch: " + field.getName());
            }
        }
        for (Field field : STATE_FIELDS) {
            if (!Modifier.isFinal(field.getModifiers())) field.set(destination, field.get(source));
        }
    }
}
