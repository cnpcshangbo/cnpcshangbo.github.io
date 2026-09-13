package woodagent;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

/** Bounded cardinal walking routes for a two-block-tall Minecraft player. */
public final class Navigation {
    public static final int MAX_EXPANDED_NODES = 10_000;

    private Navigation() {}

    /** Coordinates are the block containing the player's feet. */
    public record Pos(int x, int y, int z) {}

    /**
     * The adapter must reject hazardous or unknown blocks in both predicates.
     * isClear means the full block is safe to occupy, and isSupport means its
     * upper face is safe to stand on. Water, lava, cactus, unloaded terrain,
     * partial-height blocks, and other unsupported movement types should be false.
     */
    public interface World {
        boolean isClear(int x, int y, int z);
        boolean isSupport(int x, int y, int z);

        /** Override with 1 for drops that can be retraced with a one-block jump. */
        default int maxDrop() { return 2; }

        /** Additional adapter-specific restrictions, such as leaving surface water. */
        default boolean canTransition(Pos from, Pos to) { return true; }

        default boolean canStand(int x, int y, int z) {
            return isSupport(x, y - 1, z)
                    && isClear(x, y, z)
                    && isClear(x, y + 1, z);
        }
    }

    private record Entry(Pos position, double cost, double estimate, long order) {}

    /**
     * Returns an immutable, start-exclusive path, or an empty list when already
     * at the goal, no route exists, or the expansion budget is exhausted.
     */
    public static List<Pos> find(World world, Pos start, Pos target, int maxNodes) {
        return findNear(world, start, target, 0.0, 0, maxNodes);
    }

    /**
     * Routes to a safe cell within horizontalRadius blocks of target and within
     * verticalTolerance of its feet height. The target itself may be occupied
     * (for example, by a tree trunk). Searches never expand over 10,000 nodes.
     */
    public static List<Pos> findNear(World world, Pos start, Pos target,
                                     double horizontalRadius, int verticalTolerance,
                                     int maxNodes) {
        if (world == null || start == null || target == null) {
            throw new NullPointerException("world, start and target are required");
        }
        if (!Double.isFinite(horizontalRadius) || horizontalRadius < 0
                || verticalTolerance < 0 || maxNodes < 0) {
            throw new IllegalArgumentException("radii and node budget must be nonnegative");
        }
        int budget = Math.min(maxNodes, MAX_EXPANDED_NODES);
        if (budget == 0 || !world.canStand(start.x(), start.y(), start.z())) {
            return List.of();
        }

        PriorityQueue<Entry> open = new PriorityQueue<>(Comparator
                .comparingDouble(Entry::estimate)
                .thenComparingDouble(Entry::cost)
                .thenComparingLong(Entry::order));
        Map<Pos, Double> best = new HashMap<>();
        Map<Pos, Pos> previous = new HashMap<>();
        long nextOrder = 0;
        best.put(start, 0.0);
        open.add(new Entry(start, 0.0,
                heuristic(start, target, horizontalRadius, verticalTolerance), nextOrder++));

        int expanded = 0;
        int[][] directions = {{1, 0}, {0, 1}, {-1, 0}, {0, -1}};
        while (!open.isEmpty() && expanded < budget) {
            Entry current = open.remove();
            if (current.cost() > best.getOrDefault(current.position(), Double.POSITIVE_INFINITY)) {
                continue; // Stale entry superseded by a cheaper route.
            }
            Pos position = current.position();
            expanded++;
            if (isNear(position, target, horizontalRadius, verticalTolerance)) {
                return reconstruct(previous, start, position);
            }
            for (int[] direction : directions) {
                Pos neighbor = adjacent(world, position, direction[0], direction[1]);
                if (neighbor == null || !world.canTransition(position, neighbor)) continue;
                int rise = neighbor.y() - position.y();
                double moveCost = rise > 0 ? 1.6 : 1.0 + 0.2 * -rise;
                double candidate = current.cost() + moveCost;
                if (candidate >= best.getOrDefault(neighbor, Double.POSITIVE_INFINITY)) continue;
                best.put(neighbor, candidate);
                previous.put(neighbor, position);
                open.add(new Entry(neighbor, candidate, candidate
                        + heuristic(neighbor, target, horizontalRadius, verticalTolerance), nextOrder++));
            }
        }
        return List.of();
    }

    /**
     * Explores the reachable walking graph once and returns its best outward
     * route. maxRadius is the horizontal radius around start, not around home.
     * A destination must increase distance from home by minGain and may be no
     * more than three blocks below start. Traversal may dip lower and reascend.
     *
     * Candidates are ranked by outward gain, a small southward preference, and
     * penalties for detours and travel cost. Only settled, reachable candidates
     * are considered. If the expansion budget expires, the best candidate seen
     * so far is returned; an empty list means no qualifying candidate was seen.
     * The adapter's maxDrop policy and all normal clearance checks still apply.
     */
    public static List<Pos> findOutward(World world, Pos start, double homeX, double homeZ,
                                        double minGain, double maxRadius, int maxNodes) {
        if (world == null || start == null) {
            throw new NullPointerException("world and start are required");
        }
        if (!Double.isFinite(homeX) || !Double.isFinite(homeZ)
                || !Double.isFinite(minGain) || minGain < 0
                || !Double.isFinite(maxRadius) || maxRadius < 0 || maxNodes < 0) {
            throw new IllegalArgumentException("coordinates must be finite; gain, radius and budget nonnegative");
        }
        int budget = Math.min(maxNodes, MAX_EXPANDED_NODES);
        if (budget == 0 || minGain > maxRadius
                || !world.canStand(start.x(), start.y(), start.z())) return List.of();

        PriorityQueue<Entry> open = new PriorityQueue<>(Comparator
                .comparingDouble(Entry::cost).thenComparingLong(Entry::order));
        Map<Pos, Double> best = new HashMap<>();
        Map<Pos, Pos> previous = new HashMap<>();
        long nextOrder = 0;
        best.put(start, 0.0);
        open.add(new Entry(start, 0.0, 0.0, nextOrder++));
        double startingDistance = Math.hypot(start.x() - homeX, start.z() - homeZ);
        Pos destination = null;
        double destinationScore = Double.NEGATIVE_INFINITY;
        double destinationCost = Double.POSITIVE_INFINITY;
        int expanded = 0;
        int[][] directions = {{1, 0}, {0, 1}, {-1, 0}, {0, -1}};

        while (!open.isEmpty() && expanded < budget) {
            Entry current = open.remove();
            if (current.cost() > best.getOrDefault(current.position(), Double.POSITIVE_INFINITY)) continue;
            expanded++;
            Pos position = current.position();
            double gain = Math.hypot(position.x() - homeX, position.z() - homeZ) - startingDistance;
            if (gain >= minGain && (long) position.y() >= (long) start.y() - 3) {
                double directDistance = horizontalDistance(start, position);
                double detour = Math.max(0.0, current.cost() - directDistance);
                double score = gain + 0.04 * ((double) position.z() - start.z())
                        - 0.20 * detour - 0.01 * current.cost();
                if (score > destinationScore + 1e-9
                        || (Math.abs(score - destinationScore) <= 1e-9 && current.cost() < destinationCost)) {
                    destination = position;
                    destinationScore = score;
                    destinationCost = current.cost();
                }
            }
            for (int[] direction : directions) {
                // Reject columns outside the local disk before asking the game
                // adapter for block states or collision shapes.
                double offsetX = (double) position.x() + direction[0] - start.x();
                double offsetZ = (double) position.z() + direction[1] - start.z();
                if (Math.hypot(offsetX, offsetZ) > maxRadius) continue;
                Pos neighbor = adjacent(world, position, direction[0], direction[1]);
                if (neighbor == null || !world.canTransition(position, neighbor)) continue;
                int rise = neighbor.y() - position.y();
                double candidate = current.cost() + (rise > 0 ? 1.6 : 1.0 + 0.2 * -rise);
                if (candidate >= best.getOrDefault(neighbor, Double.POSITIVE_INFINITY)) continue;
                best.put(neighbor, candidate);
                previous.put(neighbor, position);
                open.add(new Entry(neighbor, candidate, candidate, nextOrder++));
            }
        }
        return destination == null ? List.of() : reconstruct(previous, start, destination);
    }

    public static double horizontalDistance(Pos a, Pos b) {
        return Math.hypot((double) a.x() - b.x(), (double) a.z() - b.z());
    }

    /**
     * Removes chronological loops from a recorded walk. When a cell repeats,
     * erase everything after its previous occurrence before continuing. This
     * preserves the first and last cells, and every retained directed edge
     * occurred in the original walk; it never joins different cells across a
     * discarded detour. Runs in linear time and returns an immutable list.
     */
    public static List<Pos> eraseLoops(List<Pos> walk) {
        if (walk == null) throw new NullPointerException("walk is required");
        ArrayList<Pos> result = new ArrayList<>();
        Map<Pos, Integer> index = new HashMap<>();
        for (Pos position : walk) {
            if (position == null) throw new NullPointerException("walk cells must not be null");
            Integer previousIndex = index.get(position);
            if (previousIndex == null) {
                index.put(position, result.size());
                result.add(position);
            } else {
                while (result.size() > previousIndex + 1) {
                    index.remove(result.remove(result.size() - 1));
                }
            }
        }
        return List.copyOf(result);
    }

    public static boolean isNear(Pos position, Pos target,
                                 double horizontalRadius, int verticalTolerance) {
        return horizontalDistance(position, target) <= horizontalRadius
                && Math.abs((long) position.y() - target.y()) <= verticalTolerance;
    }

    private static double heuristic(Pos position, Pos target,
                                    double radius, int verticalTolerance) {
        return Math.max(0, horizontalDistance(position, target) - radius)
                + 0.2 * Math.max(0L, Math.abs((long) position.y() - target.y()) - verticalTolerance);
    }

    /** One walking/jumping/falling landing cell in a cardinal neighboring column. */
    private static Pos adjacent(World world, Pos start, int dx, int dz) {
        int x = start.x() + dx;
        int z = start.z() + dz;
        int y = start.y();
        if (world.canStand(x, y, z)) return new Pos(x, y, z);

        // Jumping a full block requires room over both the current and next cell.
        if (world.isClear(start.x(), y + 2, start.z()) && world.canStand(x, y + 1, z)) {
            return new Pos(x, y + 1, z);
        }

        // A drop must have a clear entry at the current height and a clear shaft.
        if (!world.isClear(x, y + 1, z) || !world.isClear(x, y, z)) return null;
        int maxDrop = Math.max(0, Math.min(2, world.maxDrop()));
        for (int drop = 1; drop <= maxDrop; drop++) {
            if (!world.isClear(x, y - drop, z)) return null;
            if (world.canStand(x, y - drop, z)) return new Pos(x, y - drop, z);
        }
        return null;
    }

    private static List<Pos> reconstruct(Map<Pos, Pos> previous, Pos start, Pos end) {
        ArrayList<Pos> result = new ArrayList<>();
        for (Pos at = end; !at.equals(start); at = previous.get(at)) {
            result.add(at);
        }
        Collections.reverse(result);
        return List.copyOf(result);
    }
}
