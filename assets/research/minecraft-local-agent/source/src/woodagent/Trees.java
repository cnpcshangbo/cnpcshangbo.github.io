package woodagent;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;

/** Conservative, read-only tree selection. Call on the Minecraft client thread. */
public final class Trees {
    private Trees() {}

    private static final int MAX_SCAN_RADIUS = 24;
    private static final int STRUCTURE_RADIUS = 6;
    private static final Set<String> SOILS = Set.of(
        "minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt",
        "minecraft:podzol", "minecraft:rooted_dirt", "minecraft:moss_block",
        "minecraft:mycelium");

    public record Tree(BlockPos base, List<BlockPos> logs) {
        public Tree {
            base = base.immutable();
            logs = logs.stream().map(BlockPos::immutable).toList();
        }
    }

    private record Evidence(String soil, String trunk, Map<BlockPos, String> canopy) {}
    // Unknown caller-constructed Trees fail revalidation rather than gaining trust.
    private static final Map<Tree, Evidence> EVIDENCE =
        Collections.synchronizedMap(new WeakHashMap<>());

    public static List<Tree> candidates(ClientLevel level, int centerX, int centerY,
                                        int centerZ, int radius, double homeX,
                                        double homeZ, double protectedRadius) {
        if (level == null || !validHome(homeX, homeZ, protectedRadius)) return List.of();
        int boundedRadius = Math.max(0, Math.min(MAX_SCAN_RADIUS, radius));
        List<Tree> result = new ArrayList<>();
        Set<BlockPos> inspectedBases = new HashSet<>();
        for (int dx = -boundedRadius; dx <= boundedRadius; dx++) {
            for (int dz = -boundedRadius; dz <= boundedRadius; dz++) {
                if (dx * dx + dz * dz > boundedRadius * boundedRadius) continue;
                int x = centerX + dx, z = centerZ + dz;
                BlockPos column = new BlockPos(x, centerY, z);
                if (!outsideHome(column, homeX, homeZ, protectedRadius)
                    || !level.hasChunkAt(column)) continue;

                int surface = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                inspect(level, new BlockPos(x, surface - 1, z), homeX, homeZ,
                    protectedRadius, inspectedBases, result);
                // Also finds trunks under obstructed heightmaps and on nearby slopes.
                for (int y = centerY + 12; y >= centerY - 12; y--) {
                    if (y == surface - 1) continue;
                    inspect(level, new BlockPos(x, y, z), homeX, homeZ,
                        protectedRadius, inspectedBases, result);
                }
            }
        }
        result.sort(Comparator.comparingDouble(tree -> distanceSquared(tree.base(), centerX, centerZ)));
        return List.copyOf(result);
    }

    private static void inspect(ClientLevel level, BlockPos probe, double homeX,
                                double homeZ, double radius, Set<BlockPos> inspected,
                                List<Tree> result) {
        if (!safeLog(level, probe, homeX, homeZ, radius)) return;
        BlockPos base = probe;
        int descended = 0;
        while (descended < 12 && isLog(level, base.below())) {
            base = base.below();
            descended++;
        }
        if (isLog(level, base.below()) || !inspected.add(base)) return;
        if (!level.isLoaded(base.below())) return;
        String soil = id(level.getBlockState(base.below()));
        if (!SOILS.contains(soil)) return;
        String trunk = id(level.getBlockState(base));
        List<BlockPos> logs = new ArrayList<>();
        for (int height = 0; height <= 6; height++) {
            BlockPos pos = base.above(height);
            if (!level.isLoaded(pos)) return;
            BlockState state = level.getBlockState(pos);
            if (!state.is(BlockTags.LOGS)) break;
            if (height == 6 || !safeLog(level, pos, homeX, homeZ, radius)
                || !id(state).equals(trunk) || adjacentLog(level, pos)) return;
            logs.add(pos);
        }
        if (logs.size() < 3 || logs.size() > 6 || structureNear(level, base)) return;
        Map<BlockPos, String> canopy = canopy(level, logs.getLast());
        if (canopy.size() < 8) return;
        Tree tree = new Tree(base, logs);
        EVIDENCE.put(tree, new Evidence(soil, trunk, Map.copyOf(canopy)));
        result.add(tree);
    }

    /** Home and natural-log checks only; callers must also revalidate the Tree. */
    public static boolean safeLog(ClientLevel level, BlockPos pos, double homeX,
                                  double homeZ, double protectedRadius) {
        if (level == null || pos == null || !validHome(homeX, homeZ, protectedRadius)
            || !outsideHome(pos, homeX, homeZ, protectedRadius) || !level.isLoaded(pos)) return false;
        BlockState state = level.getBlockState(pos);
        String name = id(state);
        return state.is(BlockTags.LOGS) && name.endsWith("_log")
            && !name.startsWith("minecraft:stripped_");
    }

    /** Caller must separately associate the leaf with the currently validated tree. */
    public static boolean safeLeaf(ClientLevel level, BlockPos pos, double homeX,
                                   double homeZ, double protectedRadius) {
        return level != null && pos != null && validHome(homeX, homeZ, protectedRadius)
            && outsideHome(pos, homeX, homeZ, protectedRadius) && level.isLoaded(pos)
            && naturalLeaf(level.getBlockState(pos));
    }

    /**
     * Re-establish evidence for an agent-observed tree saved across a worker reload.
     * The caller must supply its own saved observation, never an invented trunk.
     * Only a partially cut, otherwise intact original column is accepted.
     */
    public static boolean restore(Tree tree, ClientLevel level, double homeX,
                                  double homeZ, double protectedRadius) {
        if (tree == null || level == null || tree.base() == null || tree.logs() == null
            || !validHome(homeX, homeZ, protectedRadius)) return false;
        int count = tree.logs().size();
        if (count < 3 || count > 6 || !tree.base().equals(tree.logs().getFirst())) return false;
        if (!level.isLoaded(tree.base().below()) || isLog(level, tree.base().below())) return false;
        String soil = id(level.getBlockState(tree.base().below()));
        if (!SOILS.contains(soil)) return false;

        int airPrefix = 0, remaining = 0;
        String trunk = null;
        for (int index = 0; index < count; index++) {
            BlockPos pos = tree.logs().get(index);
            if (pos == null || !pos.equals(tree.base().above(index)) || !level.isLoaded(pos)
                || !outsideHome(pos, homeX, homeZ, protectedRadius)) return false;
            BlockState state = level.getBlockState(pos);
            if (state.isAir()) {
                if (remaining > 0) return false;
                airPrefix++;
            } else {
                if (!safeLog(level, pos, homeX, homeZ, protectedRadius)
                    || adjacentLog(level, pos)) return false;
                String currentId = id(state);
                if (trunk == null) trunk = currentId;
                else if (!trunk.equals(currentId)) return false;
                remaining++;
            }
        }
        if (airPrefix == 0 || remaining == 0 || adjacentLog(level, tree.base())) return false;
        BlockPos top = tree.logs().getLast();
        if (!level.isLoaded(top.above()) || isLog(level, top.above()) || structureNear(level, tree.base())) return false;
        Map<BlockPos, String> leaves = canopy(level, top);
        if (leaves.size() < 8) return false;
        EVIDENCE.put(tree, new Evidence(soil, trunk, Map.copyOf(leaves)));
        return true;
    }

    /**
     * Allows an already-harvested air prefix at the original base. Remaining logs
     * must form the unchanged upper part of the originally inspected trunk.
     * Original leaves may decay or be trimmed to air; surviving leaves must still
     * be the original natural leaf type. Other replacement blocks invalidate the tree.
     */
    public static boolean revalidate(Tree tree, ClientLevel level, double homeX,
                                     double homeZ, double protectedRadius) {
        if (tree == null || level == null || !validHome(homeX, homeZ, protectedRadius)) return false;
        Evidence evidence = EVIDENCE.get(tree);
        if (evidence == null || !level.isLoaded(tree.base().below())
            || !id(level.getBlockState(tree.base().below())).equals(evidence.soil())) return false;
        boolean reachedRemainingTrunk = false;
        for (BlockPos pos : tree.logs()) {
            if (!outsideHome(pos, homeX, homeZ, protectedRadius) || !level.isLoaded(pos)) return false;
            BlockState state = level.getBlockState(pos);
            if (state.isAir()) {
                if (reachedRemainingTrunk) return false;
            } else {
                if (!safeLog(level, pos, homeX, homeZ, protectedRadius)
                    || !id(state).equals(evidence.trunk()) || adjacentLog(level, pos)) return false;
                reachedRemainingTrunk = true;
            }
        }
        for (Map.Entry<BlockPos, String> leaf : evidence.canopy().entrySet()) {
            if (!level.isLoaded(leaf.getKey())) return false;
            BlockState state = level.getBlockState(leaf.getKey());
            if (state.isAir()) continue;
            if (!naturalLeaf(state) || !id(state).equals(leaf.getValue())) return false;
        }
        return !structureNear(level, tree.base());
    }

    public static boolean revalidate(ClientLevel level, Tree tree, double homeX,
                                     double homeZ, double protectedRadius) {
        return revalidate(tree, level, homeX, homeZ, protectedRadius);
    }

    /** Unknown chunks are treated as protected, never silently ignored. */
    public static boolean structureNear(ClientLevel level, BlockPos base) {
        return structureNear(level, base, STRUCTURE_RADIUS);
    }

    public static boolean structureNear(ClientLevel level, BlockPos base, int radius) {
        if (level == null || base == null) return true;
        int bounded = Math.max(STRUCTURE_RADIUS, Math.min(8, radius));
        for (int dx = -bounded; dx <= bounded; dx++) {
            for (int dz = -bounded; dz <= bounded; dz++) {
                for (int dy = -bounded; dy <= bounded; dy++) {
                    BlockPos pos = base.offset(dx, dy, dz);
                    if (!level.isLoaded(pos)) return true;
                    if (isStructure(id(level.getBlockState(pos)))) return true;
                }
            }
        }
        return false;
    }

    private static boolean isStructure(String id) {
        return id.endsWith("_planks") || id.endsWith("_door") || id.endsWith("_trapdoor")
            || id.contains("glass") || id.endsWith("chest") || id.equals("minecraft:barrel")
            || id.equals("minecraft:crafting_table") || id.endsWith("_bed")
            || id.endsWith("_fence") || id.endsWith("_fence_gate")
            || id.contains("stone_brick") || id.contains("stonebrick");
    }

    private static Map<BlockPos, String> canopy(ClientLevel level, BlockPos top) {
        Map<BlockPos, String> leaves = new LinkedHashMap<>();
        for (int dy = -2; dy <= 3; dy++) {
            for (int dx = -3; dx <= 3; dx++) {
                for (int dz = -3; dz <= 3; dz++) {
                    BlockPos pos = top.offset(dx, dy, dz);
                    if (!level.isLoaded(pos)) return Map.of();
                    BlockState state = level.getBlockState(pos);
                    if (naturalLeaf(state)) leaves.put(pos, id(state));
                }
            }
        }
        return leaves;
    }

    private static boolean adjacentLog(ClientLevel level, BlockPos pos) {
        // Reject 2x2 trunks and side branches, including diagonal log connections.
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                if (dx == 0 && dz == 0) continue;
                BlockPos neighbor = pos.offset(dx, 0, dz);
                if (!level.isLoaded(neighbor) || isLog(level, neighbor)) return true;
            }
        }
        return false;
    }

    private static boolean isLog(ClientLevel level, BlockPos pos) {
        return level.isLoaded(pos) && level.getBlockState(pos).is(BlockTags.LOGS);
    }

    private static boolean naturalLeaf(BlockState state) {
        return state.is(BlockTags.LEAVES)
            && state.hasProperty(BlockStateProperties.PERSISTENT)
            && !state.getValue(BlockStateProperties.PERSISTENT);
    }

    private static String id(BlockState state) {
        return BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString();
    }

    private static boolean validHome(double x, double z, double radius) {
        return Double.isFinite(x) && Double.isFinite(z) && Double.isFinite(radius) && radius >= 0;
    }

    private static boolean outsideHome(BlockPos pos, double x, double z, double radius) {
        // Measure the closest point of the whole block, not just its center.
        double dx = Math.max(0, Math.max(pos.getX() - x, x - (pos.getX() + 1.0)));
        double dz = Math.max(0, Math.max(pos.getZ() - z, z - (pos.getZ() + 1.0)));
        return dx * dx + dz * dz > radius * radius;
    }

    private static double distanceSquared(BlockPos pos, double x, double z) {
        double dx = pos.getX() + 0.5 - x, dz = pos.getZ() + 0.5 - z;
        return dx * dx + dz * dz;
    }
}
