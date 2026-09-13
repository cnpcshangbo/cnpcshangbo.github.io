package woodagent;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Run with java woodagent.NavigationTest; no testing dependencies needed. */
public final class NavigationTest {
    private enum Block { AIR, SOLID, WATER, LAVA, CACTUS }

    private static final class Terrain implements Navigation.World {
        private final Map<Navigation.Pos, Block> blocks = new HashMap<>();
        private final int minX, maxX, minZ, maxZ;
        int predicateCalls;

        Terrain(int minX, int maxX, int minZ, int maxZ) {
            this.minX = minX;
            this.maxX = maxX;
            this.minZ = minZ;
            this.maxZ = maxZ;
        }

        Terrain put(int x, int y, int z, Block block) {
            blocks.put(new Navigation.Pos(x, y, z), block);
            return this;
        }

        Terrain floor(int y) {
            for (int x = minX; x <= maxX; x++) {
                for (int z = minZ; z <= maxZ; z++) put(x, y, z, Block.SOLID);
            }
            return this;
        }

        private Block block(int x, int y, int z) {
            if (x < minX || x > maxX || z < minZ || z > maxZ || y < -5 || y > 8) {
                return null; // Unknown/unloaded space must not be traversed.
            }
            return blocks.getOrDefault(new Navigation.Pos(x, y, z), Block.AIR);
        }

        public boolean isClear(int x, int y, int z) {
            predicateCalls++;
            return block(x, y, z) == Block.AIR;
        }

        public boolean isSupport(int x, int y, int z) {
            predicateCalls++;
            return block(x, y, z) == Block.SOLID;
        }
    }

    private static Navigation.Pos p(int x, int y, int z) {
        return new Navigation.Pos(x, y, z);
    }

    private static void require(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }

    private static List<Navigation.Pos> find(Terrain terrain, Navigation.Pos start, Navigation.Pos target) {
        return Navigation.find(terrain, start, target, 10_000);
    }

    private static void requireOriginalEdges(List<Navigation.Pos> original, List<Navigation.Pos> simplified) {
        for (int i = 1; i < simplified.size(); i++) {
            boolean seen = false;
            for (int j = 1; j < original.size(); j++) {
                if (original.get(j - 1).equals(simplified.get(i - 1))
                        && original.get(j).equals(simplified.get(i))) {
                    seen = true;
                    break;
                }
            }
            require(seen, "loop erasure must not invent a directed edge");
        }
    }

    public static void main(String[] args) {
        Terrain flat = new Terrain(0, 5, 0, 0).floor(0);
        List<Navigation.Pos> route = find(flat, p(0, 1, 0), p(5, 1, 0));
        require(route.size() == 5 && route.get(0).equals(p(1, 1, 0))
                && route.get(4).equals(p(5, 1, 0)), "flat route must exclude start and include target");
        require(find(flat, p(0, 1, 0), p(0, 1, 0)).isEmpty(), "already at goal");
        require(Navigation.find(flat, p(0, 1, 0), p(5, 1, 0), 1).isEmpty(), "node budget enforced");

        Terrain stairs = new Terrain(0, 3, 0, 0);
        for (int x = 0; x <= 3; x++) for (int y = 0; y <= x; y++) stairs.put(x, y, 0, Block.SOLID);
        require(find(stairs, p(0, 1, 0), p(3, 4, 0)).equals(List.of(p(1, 2, 0), p(2, 3, 0), p(3, 4, 0))),
                "ascending one-block stairs");
        require(find(stairs, p(3, 4, 0), p(0, 1, 0)).size() == 3, "descending stairs");
        stairs.put(0, 3, 0, Block.SOLID);
        require(find(stairs, p(0, 1, 0), p(3, 4, 0)).isEmpty(), "jump blocked by headroom over start");

        Terrain twoDrop = new Terrain(0, 1, 0, 0).put(0, 2, 0, Block.SOLID).put(1, 0, 0, Block.SOLID);
        require(find(twoDrop, p(0, 3, 0), p(1, 1, 0)).equals(List.of(p(1, 1, 0))), "two-block drop allowed");
        require(find(twoDrop, p(1, 1, 0), p(0, 3, 0)).isEmpty(), "two-block step up forbidden");
        Navigation.World reversible = new Navigation.World() {
            public boolean isClear(int x, int y, int z) { return twoDrop.isClear(x, y, z); }
            public boolean isSupport(int x, int y, int z) { return twoDrop.isSupport(x, y, z); }
            public int maxDrop() { return 1; }
        };
        require(Navigation.find(reversible, p(0, 3, 0), p(1, 1, 0), 100).isEmpty(),
                "maxDrop=1 rejects otherwise valid two-block drop");
        twoDrop.put(1, 1, 0, Block.SOLID);
        require(Navigation.find(reversible, p(0, 3, 0), p(1, 2, 0), 100).equals(List.of(p(1, 2, 0))),
                "maxDrop=1 preserves one-block drop");
        require(Navigation.find(reversible, p(1, 2, 0), p(0, 3, 0), 100).equals(List.of(p(0, 3, 0))),
                "one-block drop can be retraced");
        Terrain threeDrop = new Terrain(0, 1, 0, 0).put(0, 3, 0, Block.SOLID).put(1, 0, 0, Block.SOLID);
        require(find(threeDrop, p(0, 4, 0), p(1, 1, 0)).isEmpty(), "three-block drop forbidden");

        Terrain wall = new Terrain(0, 4, 0, 2).floor(0);
        wall.put(2, 1, 1, Block.SOLID).put(2, 2, 1, Block.SOLID);
        route = find(wall, p(0, 1, 1), p(4, 1, 1));
        require(route.size() == 6 && route.stream().anyMatch(pos -> pos.z() != 1), "wall requires a cardinal detour");
        wall.put(2, 1, 0, Block.SOLID).put(2, 2, 0, Block.SOLID)
                .put(2, 1, 2, Block.SOLID).put(2, 2, 2, Block.SOLID);
        require(find(wall, p(0, 1, 1), p(4, 1, 1)).isEmpty(), "sealed wall blocks route");

        Terrain pit = new Terrain(0, 2, 0, 0).put(0, 0, 0, Block.SOLID).put(2, 0, 0, Block.SOLID);
        require(find(pit, p(0, 1, 0), p(2, 1, 0)).isEmpty(), "unsupported gap is not walkable");
        for (Block hazard : List.of(Block.WATER, Block.LAVA, Block.CACTUS)) {
            pit.put(1, 0, 0, hazard);
            require(find(pit, p(0, 1, 0), p(2, 1, 0)).isEmpty(), hazard + " cannot support route");
            Terrain occupied = new Terrain(0, 2, 0, 0).floor(0).put(1, 1, 0, hazard);
            require(find(occupied, p(0, 1, 0), p(2, 1, 0)).isEmpty(), hazard + " cannot be entered");
        }

        Terrain roofedDrop = new Terrain(0, 1, 0, 0).put(0, 2, 0, Block.SOLID)
                .put(1, 0, 0, Block.SOLID).put(1, 4, 0, Block.SOLID);
        require(find(roofedDrop, p(0, 3, 0), p(1, 1, 0)).isEmpty(), "drop entry requires head clearance");

        Terrain tree = new Terrain(0, 5, 0, 0).floor(0).put(5, 1, 0, Block.SOLID).put(5, 2, 0, Block.SOLID);
        route = Navigation.findNear(tree, p(0, 1, 0), p(5, 1, 0), 1.0, 0, 100);
        require(route.size() == 4 && route.get(3).equals(p(4, 1, 0)), "near goal permits occupied tree target");
        require(Navigation.horizontalDistance(p(0, 9, 0), p(3, -9, 4)) == 5.0, "horizontal distance ignores height");
        require(!Navigation.isNear(p(4, 3, 0), p(5, 1, 0), 1.0, 1), "near goal respects vertical tolerance");
        require(find(flat, p(0, 2, 0), p(5, 1, 0)).isEmpty(), "unsupported starting position rejected");

        final int[] expansions = {0};
        Navigation.World enormous = new Navigation.World() {
            public boolean isClear(int x, int y, int z) { return y > 0; }
            public boolean isSupport(int x, int y, int z) { return y == 0; }
            public boolean canStand(int x, int y, int z) {
                if (y == 1) expansions[0]++;
                return Navigation.World.super.canStand(x, y, z);
            }
        };
        require(Navigation.find(enormous, p(0, 1, 0), p(100_000, 1, 0), Integer.MAX_VALUE).isEmpty(),
                "hard expansion cap terminates infinite terrain");
        require(expansions[0] <= 40_001, "at most four cardinal neighbors per 10,000 expansions");

        // Large-radius corner goals are unreachable. A narrow southward egress
        // exists beneath a roof/canopy, whose heightmap top is not walkable from here.
        Terrain egress = new Terrain(-10, 10, -10, 10).floor(0);
        for (int z = -10; z <= 10; z++) for (int y = 1; y <= 4; y++) {
            egress.put(-2, y, z, Block.SOLID).put(2, y, z, Block.SOLID);
        }
        for (int x = -1; x <= 1; x++) {
            for (int y = 1; y <= 4; y++) egress.put(x, y, -2, Block.SOLID);
            for (int z = -1; z <= 10; z++) egress.put(x, 3, z, Block.SOLID);
        }
        route = Navigation.findOutward(egress, p(0, 1, 0), 0, 0, 5, 24, 6_000);
        require(!route.isEmpty() && route.get(route.size() - 1).z() == 10,
                "outward flood finds available egress despite unreachable farther corners");
        require(route.stream().allMatch(pos -> Math.abs(pos.x()) <= 1 && pos.y() == 1),
                "outward route remains in reachable corridor beneath canopy");

        Terrain open = new Terrain(-10, 10, -10, 10).floor(0);
        route = Navigation.findOutward(open, p(0, 1, 0), 0, 0, 5, 8, 6_000);
        require(route.get(route.size() - 1).equals(p(0, 1, 8)), "outward score has an explicit south preference");
        require(route.stream().allMatch(pos -> Navigation.horizontalDistance(pos, p(0, 1, 0)) <= 8),
                "every outward waypoint stays within the local search radius");
        Terrain detour = new Terrain(-4, 4, -10, 8);
        for (int z = 0; z <= 8; z++) detour.put(0, 0, z, Block.SOLID);
        int[][] corners = {{0, 0}, {-3, 0}, {-3, -3}, {3, -3}, {3, -6}, {-3, -6}, {-3, -9}, {0, -9}};
        for (int i = 1; i < corners.length; i++) {
            int x = corners[i - 1][0], z = corners[i - 1][1];
            while (x != corners[i][0] || z != corners[i][1]) {
                x += Integer.compare(corners[i][0], x);
                z += Integer.compare(corners[i][1], z);
                detour.put(x, 0, z, Block.SOLID);
            }
        }
        route = Navigation.findOutward(detour, p(0, 1, 0), 0, 0, 5, 10, 1_000);
        require(route.get(route.size() - 1).equals(p(0, 1, 8)) && route.size() == 8,
                "a slightly farther destination behind a long detour loses to direct outward progress");
        route = Navigation.findOutward(flat, p(0, 1, 0), 0, 0, 2, 5, 4);
        require(route.equals(List.of(p(1, 1, 0), p(2, 1, 0), p(3, 1, 0))),
                "budget exhaustion returns the best reachable candidate already settled");
        require(Navigation.findOutward(flat, p(0, 1, 0), 0, 0, 6, 5, 100).isEmpty(),
                "outward search rejects impossible gain beyond its local radius");

        Navigation.World descendingMine = new Navigation.World() {
            public int maxDrop() { return 1; }
            public boolean isSupport(int x, int y, int z) { return z == 0 && x >= 0 && x <= 8 && y == -x; }
            public boolean isClear(int x, int y, int z) { return z == 0 && x >= 0 && x <= 8 && y > -x; }
        };
        require(Navigation.findOutward(descendingMine, p(0, 1, 0), 0, 0, 5, 8, 100).isEmpty(),
                "a deep mine cannot become the outward destination from the surface");
        final int[] valleyFloor = {0, -1, -2, -3, -4, -4, -3, -2, -1, 0, 0, 0, 0};
        Navigation.World valley = new Navigation.World() {
            public int maxDrop() { return 1; }
            public boolean isSupport(int x, int y, int z) {
                return z == 0 && x >= 0 && x < valleyFloor.length && y == valleyFloor[x];
            }
            public boolean isClear(int x, int y, int z) {
                return z == 0 && x >= 0 && x < valleyFloor.length && y > valleyFloor[x];
            }
        };
        route = Navigation.findOutward(valley, p(0, 1, 0), 0, 0, 9, 12, 100);
        require(!route.isEmpty() && route.get(route.size() - 1).equals(p(12, 1, 0))
                && route.stream().anyMatch(pos -> pos.y() < -2),
                "outward traversal may descend more than three blocks and reascend to its destination");

        // The adapter can represent open source-water surfaces as virtual support
        // while rejecting exits that would require jumping from deep water.
        Terrain shore = new Terrain(0, 3, 0, 0).floor(0)
                .put(1, 0, 0, Block.WATER).put(2, 0, 0, Block.WATER).put(3, 1, 0, Block.SOLID);
        Navigation.World surfaceWater = new Navigation.World() {
            public int maxDrop() { return 1; }
            public boolean isClear(int x, int y, int z) { return shore.isClear(x, y, z); }
            public boolean isSupport(int x, int y, int z) {
                return shore.isSupport(x, y, z)
                        || (shore.block(x, y, z) == Block.WATER && shore.isClear(x, y + 1, z));
            }
            public boolean canTransition(Navigation.Pos from, Navigation.Pos to) {
                return shore.block(from.x(), from.y() - 1, from.z()) != Block.WATER || to.y() <= from.y();
            }
        };
        require(Navigation.find(surfaceWater, p(0, 1, 0), p(2, 1, 0), 100)
                        .equals(List.of(p(1, 1, 0), p(2, 1, 0))),
                "virtual surface-water graph allows level entry and swimming");
        require(Navigation.find(surfaceWater, p(2, 1, 0), p(0, 1, 0), 100)
                        .equals(List.of(p(1, 1, 0), p(0, 1, 0))),
                "water adapter allows an exit onto a level shoreline");
        require(Navigation.find(surfaceWater, p(2, 1, 0), p(3, 2, 0), 100).isEmpty(),
                "transition veto prevents a one-block uphill water exit");
        require(Navigation.find(surfaceWater, p(3, 2, 0), p(2, 1, 0), 100).equals(List.of(p(2, 1, 0))),
                "one-block downward water entry remains allowed");
        require(Navigation.findOutward(surfaceWater, p(1, 1, 0), 0, 0, 2, 3, 100).isEmpty(),
                "outward search also honors the adapter's transition veto");
        Navigation.Pos a = p(0, 1, 0), b = p(1, 1, 0), c = p(2, 1, 0), d = p(2, 1, 1),
                e = p(3, 1, 1), f = p(1, 1, 1), g = p(1, 1, 2);
        List<Navigation.Pos> nested = List.of(a, b, c, d, e, d, c, b, f, g);
        List<Navigation.Pos> simplified = Navigation.eraseLoops(nested);
        require(simplified.equals(List.of(a, b, f, g)), "nested detours are erased chronologically");
        require(simplified.get(0).equals(nested.get(0))
                        && simplified.get(simplified.size() - 1).equals(nested.get(nested.size() - 1)),
                "loop erasure preserves starting and ending cells");
        requireOriginalEdges(nested, simplified);
        List<Navigation.Pos> duplicates = List.of(a, a, b, b, b, c, c);
        simplified = Navigation.eraseLoops(duplicates);
        require(simplified.equals(List.of(a, b, c)), "consecutive duplicate cells collapse");
        requireOriginalEdges(duplicates, simplified);
        List<Navigation.Pos> direct = List.of(a, b, c, d, e);
        require(Navigation.eraseLoops(direct).equals(direct), "loop-free path remains unchanged");
        require(Navigation.eraseLoops(List.of(a, b, c, b, a)).equals(List.of(a)),
                "a closed loop retains its shared starting and ending cell");
        require(Navigation.eraseLoops(List.of()).isEmpty(), "empty walk stays empty");
        boolean immutable = false;
        try { simplified.add(d); } catch (UnsupportedOperationException expected) { immutable = true; }
        require(immutable, "loop-erased path is immutable");
        System.out.println("Navigation tests passed (flat, stairs, drops, headroom, walls, hazards, near goals, outward routes, loops, budgets).");
    }
}
