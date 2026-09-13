package woodagent;

import com.google.gson.*;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.RangedAttackMob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import static woodagent.Navigation.*;

/** Small deterministic client worker: all world reads and gameplay actions stay on the game thread. */
public final class Controller implements AutoCloseable {
    private final Minecraft mc = Minecraft.getInstance();
    private final Path dir;
    private final Gson json = new GsonBuilder().setPrettyPrinting().create();
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
        Thread t = new Thread(r,"local-wood-supervisor"); t.setDaemon(true); return t;
    });
    private final AtomicBoolean queued = new AtomicBoolean();
    private final ArrayDeque<Pos> route = new ArrayDeque<>();
    private final ArrayDeque<Pos> returnStops = new ArrayDeque<>();
    private final ArrayList<Pos> breadcrumbs = new ArrayList<>();
    private final Set<BlockPos> skippedTrees = new HashSet<>();
    private final ArrayDeque<Trees.Tree> recoveryTrees = new ArrayDeque<>();
    private volatile boolean closed;
    private String phase = "IDLE", reason = "Attached; awaiting a start command", commandId = "", afterRoute = "";
    private boolean active, previousPauseOnFocus, ownsFocusSetting;
    private int previousSlot, baselineLogs, targetLogs = 32, lastTick = -1, treesCut;
    private double homeX=-698, homeZ=195, radius=128, maxDistance=384;
    private long started, lastStatus, waypointStarted, harvestStarted, lootStarted, lastCommandPoll;
    private float previousHealth;
    private Pos start, lastWaypoint;
    private Trees.Tree tree;
    private net.minecraft.client.multiplayer.ClientLevel expectedLevel;
    private int logIndex;
    private BlockPos digging;
    private BackgroundGameMode background;
    private String lastScan = "";
    private record Plan(Pos goal,Trees.Tree tree,boolean near,String next,String message) {}
    private final ArrayDeque<Plan> plans=new ArrayDeque<>();
    private boolean returnOnPlanFailure;
    private final World world = new World() {
        public int maxDrop() { return 1; }
        public boolean canTransition(Pos from,Pos to) {return from.y()==to.y() || (!waterSupport(from)&&!waterSupport(to));}
        public boolean isClear(int x,int y,int z) {
            BlockPos p = new BlockPos(x,y,z);
            if (mc.level == null || !mc.level.hasChunkAt(p)) return false;
            var s=mc.level.getBlockState(p); String id=blockId(p);
            return s.getFluidState().isEmpty() && !hazard(id) && s.getCollisionShape(mc.level,p).isEmpty();
        }
        public boolean isSupport(int x,int y,int z) {
            BlockPos p = new BlockPos(x,y,z);
            if (mc.level == null || !mc.level.hasChunkAt(p)) return false;
            var s=mc.level.getBlockState(p);
            if(blockId(p).equals("minecraft:water") && s.getFluidState().is(FluidTags.WATER) && s.getFluidState().isSource()
                && mc.level.getBlockState(p.above()).isAir())return true;
            return s.getFluidState().isEmpty() && !hazard(blockId(p)) && !s.is(BlockTags.LEAVES)
                && s.isCollisionShapeFullBlock(mc.level,p);
        }
    };

    public Controller(Path directory) throws Exception {
        dir=directory; Files.createDirectories(dir.resolve("runtime"));
        Path command=dir.resolve("runtime/command.json");
        if(Files.exists(command)) commandId=JsonParser.parseString(Files.readString(command)).getAsJsonObject().get("id").getAsString();
        scheduler.scheduleWithFixedDelay(() -> {
            if(closed || !queued.compareAndSet(false,true)) return;
            mc.execute(() -> { try { tick(); } catch(Throwable e) { stop("ERROR",e.getClass().getSimpleName()+": "+e.getMessage(),true); }
                finally { queued.set(false); } });
        },0,50,TimeUnit.MILLISECONDS);
    }

    private void tick() throws Exception {
        long now=System.currentTimeMillis();
        if(now-lastCommandPoll>=100) { lastCommandPoll=now; commands(); }
        if(active && now-Files.getLastModifiedTime(dir.resolve("runtime/lease")).toMillis()>120_000) stop("STOPPED","Supervisor lease expired",true);
        if(active && (mc.player==null || mc.level==null || mc.level!=expectedLevel)) stop("STOPPED","World changed or disconnected",true);
        if(active && (mc.gui.screen()!=null || (mc.isPaused() && now-started>500))) stop("STOPPED","Game menu opened or game paused",false);
        if(active && mc.player!=null && mc.level!=null && mc.player.tickCount!=lastTick) {
            lastTick=mc.player.tickCount;
            if(mc.gui.screen()!=null || mc.isPaused()) stop("STOPPED","Game menu opened or game paused",false);
            else if(!mc.hasSingleplayerServer()) stop("STOPPED","Only the verified singleplayer world is supported",true);
            else if(mc.player.getHealth()<previousHealth || mc.player.getHealth()<=12) stop("STOPPED","Health changed; manual review needed",true);
            else if(mc.player.getFoodData().getFoodLevel()<=8 && !phase.equals("RETURN")) beginReturn("Food is low");
            else if(mc.player.isInLava() || mc.player.getAirSupply()<200) stop("STOPPED","Lava or insufficient air",true);
            else if(mc.level.getEntitiesOfClass(Monster.class,mc.player.getBoundingBox().inflate(24)).stream()
                .anyMatch(m->m.distanceTo(mc.player)<7 || (m instanceof RangedAttackMob && m.distanceTo(mc.player)<24 && m.hasLineOfSight(mc.player))))
                stop("STOPPED","Hostile mob or ranged attacker nearby",true);
            else if(now-started>20*60_000) stop("STOPPED","Twenty-minute run limit reached",true);
            else {
                previousHealth=mc.player.getHealth();
                Pos p=position();
                if(!phase.equals("RETURN") && (breadcrumbs.isEmpty() || !breadcrumbs.getLast().equals(p)) && (mc.player.onGround()||mc.player.isInWater()) && world.canStand(p.x(),p.y(),p.z())) breadcrumbs.add(p);
                if(phase.equals("NAVIGATE") || phase.equals("RETURN")) move();
                else if(phase.equals("PLAN_ESCAPE")) escape();
                else if(phase.equals("PLAN")) plan();
                else if(phase.equals("SEARCH")) search();
                else if(phase.equals("HARVEST")) harvest();
                else if(phase.equals("LOOT")) loot();
                if(active && mc.player.isInWater()){mc.options.keyShift.setDown(false);mc.options.keyJump.setDown(true);}
            }
        }
        if(now-lastStatus>=500) { lastStatus=now; status(); }
    }

    private void commands() throws Exception {
        Path file=dir.resolve("runtime/command.json"); if(!Files.exists(file)) return;
        JsonObject c; try { c=JsonParser.parseString(Files.readString(file)).getAsJsonObject(); } catch(Exception e) { return; }
        String id=c.get("id").getAsString(); if(id.equals(commandId)) return; commandId=id;
        String action=c.get("action").getAsString();
        if(action.equals("stop")) { stop("STOPPED","Stopped by supervisor",true); return; }
        if(action.equals("scan")) { if(active) return; scan(); return; }
        if(!action.equals("start") && !action.equals("resume")) { reason="Unknown command: "+action; return; }
        if(active) { reason="Already running"; return; }
        if(mc.player==null || mc.level==null || !mc.hasSingleplayerServer()) { reason="Open the intended singleplayer world first"; return; }
        if(!mc.getLaunchedVersion().equals("26.3-rc-2")) { reason="Unsupported game version: "+mc.getLaunchedVersion(); return; }
        homeX=number(c,"homeX",-698); homeZ=number(c,"homeZ",195);
        radius=number(c,"radius",128); targetLogs=(int)number(c,"logs",32); maxDistance=Math.max(radius+128,384);
        if(radius<128 || radius>512 || targetLogs<1 || targetLogs>64) { reason="Invalid run limits"; return; }
        if(mc.player.getHealth()<18 || mc.player.getFoodData().getFoodLevel()<12) { reason="Start requires healthy, fed player"; return; }
        baselineLogs=logs(); treesCut=0; start=position(); breadcrumbs.clear(); breadcrumbs.add(start); skippedTrees.clear();
        recoveryTrees.clear();
        if(action.equals("resume")) {
            Path saved=dir.resolve("runtime/mission.json");
            if(!Files.exists(saved)){reason="No saved mission to resume";return;}
            JsonObject mission=JsonParser.parseString(Files.readString(saved)).getAsJsonObject();
            homeX=mission.get("homeX").getAsDouble();homeZ=mission.get("homeZ").getAsDouble();radius=mission.get("radius").getAsDouble();
            targetLogs=mission.get("targetLogs").getAsInt();baselineLogs=mission.get("baselineLogs").getAsInt();start=json.fromJson(mission.get("start"),Pos.class);
            breadcrumbs.clear();for(var entry:mission.getAsJsonArray("breadcrumbs"))breadcrumbs.add(json.fromJson(entry,Pos.class));
            if(mission.has("recoveryTrees"))for(var entry:mission.getAsJsonArray("recoveryTrees"))recoveryTrees.add(json.fromJson(entry,Trees.Tree.class));
            // A stopped return should continue from here, not revisit the farthest tree.
            if(logs()-baselineLogs>=targetLogs && recoveryTrees.isEmpty()) {
                int at=breadcrumbs.lastIndexOf(position());
                if(at>=0)breadcrumbs.subList(at+1,breadcrumbs.size()).clear();
            }
        }
        maxDistance=Math.max(radius+128,384);
        started=System.currentTimeMillis(); expectedLevel=mc.level; previousHealth=mc.player.getHealth(); previousSlot=mc.player.getInventory().getSelectedSlot();
        previousPauseOnFocus=mc.options.pauseOnLostFocus; ownsFocusSetting=true; mc.options.pauseOnLostFocus=false;
        background=BackgroundGameMode.install(mc);
        Files.writeString(dir.resolve("runtime/lease"),Instant.now().toString());
        mc.gui.setScreen(null); active=true; phase=logs()-baselineLogs>=targetLogs && recoveryTrees.isEmpty()?"SEARCH":"PLAN_ESCAPE"; reason="Starting or resuming the local mission";
        lastTick=mc.player.tickCount; lastScan="";
    }
    private static double number(JsonObject c,String key,double fallback) { return c.has(key)?c.get(key).getAsDouble():fallback; }
    private Pos position() {
        int x=(int)Math.floor(mc.player.getX()), y=(int)Math.floor(mc.player.getY()+0.01), z=(int)Math.floor(mc.player.getZ());
        if(mc.player.isInWater()) {
            int surface=mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
            if(surface>=y && surface<=y+2 && waterSupport(new Pos(x,surface,z))) y=surface;
        }
        return new Pos(x,y,z);
    }
    private boolean waterSupport(Pos p){return mc.level.getBlockState(new BlockPos(p.x(),p.y()-1,p.z())).getFluidState().is(FluidTags.WATER);}
    private String blockId(BlockPos p) { return BuiltInRegistries.BLOCK.getKey(mc.level.getBlockState(p).getBlock()).toString(); }
    private static boolean hazard(String id) { return id.contains("lava")||id.contains("fire")||id.contains("cactus")||id.contains("magma")||id.contains("powder_snow")||id.contains("berry_bush")||id.contains("campfire"); }
    private int logs() { int n=0; for(int i=0;i<36;i++){ItemStack s=mc.player.getInventory().getItem(i); if(s.is(ItemTags.LOGS)) n+=s.getCount();} return n; }
    private boolean room() { int empty=0;for(int i=0;i<36;i++) if(mc.player.getInventory().getItem(i).isEmpty()) empty++;return empty>=2; }
    private double homeDistance(Pos p) { return Math.hypot(p.x()-homeX,p.z()-homeZ); }

    private List<Pos> surface(int cx,int cz,int r) {
        ArrayList<Pos> out=new ArrayList<>();
        for(int x=cx-r;x<=cx+r;x++) for(int z=cz-r;z<=cz+r;z++) {
            if(!mc.level.hasChunkAt(new BlockPos(x,64,z)))continue;
            int y=mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
            Pos p=new Pos(x,y,z);
            if(world.canStand(x,y,z) && !blockId(new BlockPos(x,y-1,z)).contains("log") && y>=50 && y<=120)out.add(p);
        }
        return out;
    }
    private void escape() {
        release(); Pos p=position();
        var candidates=surface(p.x(),p.z(),14);
        candidates.sort(Comparator.comparingDouble(a -> horizontalDistance(a,p)+Math.abs(a.y()-p.y())*.4));
        int tried=0;plans.clear();returnOnPlanFailure=false;
        for(Pos goal:candidates) {
            if(tried++>=30)break;
            if(isNear(p,goal,0,0)) { phase="SEARCH";reason="At the surface";return; }
            plans.add(new Plan(goal,null,false,"SEARCH","Walking out of the mine"));
        }
        phase="PLAN";
    }
    private void plan() {
        release();
        if(plans.isEmpty()){if(returnOnPlanFailure)outward();else stop("STOPPED","No safe walking route from the mine to the surface",true);return;}
        Plan p=plans.remove();Pos here=position();
        List<Pos> path=p.near()?findNear(world,here,p.goal(),2.5,0,4000):find(world,here,p.goal(),4000);
        boolean already=isNear(here,p.goal(),p.near()?2.5:0,0);
        if(!path.isEmpty() || already){tree=p.tree();logIndex=0;digging=null;plans.clear();if(already){phase=p.next();reason=p.message();}else setRoute(path,p.next(),p.message());}
        else if(p.tree()!=null)skippedTrees.add(p.tree().base());
    }
    private void search() {
        release();
        while(!recoveryTrees.isEmpty() && recoveryTrees.peek().logs().stream().allMatch(b->mc.level.getBlockState(b).isAir()))recoveryTrees.remove();
        if(!recoveryTrees.isEmpty()) {
            Trees.Tree pending=recoveryTrees.peek();plans.clear();returnOnPlanFailure=false;
            if(!Trees.restore(pending,mc.level,homeX,homeZ,radius) || !queueTree(pending)){stop("STOPPED","Cannot reach the remaining trunk at "+pending.base(),true);return;}
            phase="PLAN";return;
        }
        if(logs()-baselineLogs>=targetLogs) { beginReturn("Log target collected");return; }
        if(!room()) { beginReturn("Inventory nearly full");return; }
        Pos p=position();plans.clear();returnOnPlanFailure=true;
        if(homeDistance(p)>=radius+8) {
            var found=new ArrayList<>(Trees.candidates(mc.level,p.x(),p.y(),p.z(),24,homeX,homeZ,radius));
            found.sort(Comparator.comparingDouble(t -> t.base().distToCenterSqr(mc.player.position())));
            int attempts=0;
            for(Trees.Tree t:found) {
                if(skippedTrees.contains(t.base()) || attempts++>=16)continue;
                queueTree(t);
            }
        }
        phase="PLAN";
    }
    private boolean queueTree(Trees.Tree t) {
        int before=plans.size();
        for(int[] d:new int[][]{{1,0},{0,1},{-1,0},{0,-1}}) {
            Pos stance=new Pos(t.base().getX()+d[0],t.base().getY(),t.base().getZ()+d[1]);
            if(!world.canStand(stance.x(),stance.y(),stance.z()) || waterSupport(stance))continue;
            Vec3 eyes=new Vec3(stance.x()+.5,stance.y()+mc.player.getEyeHeight(),stance.z()+.5);
            boolean clear=true;
            for(int i=0;i<Math.min(2,t.logs().size());i++)if(!mc.level.getBlockState(t.logs().get(i)).isAir() && visiblePoint(eyes,t.logs().get(i))==null){clear=false;break;}
            if(clear)plans.add(new Plan(stance,t,false,"HARVEST","Approaching a clear side of a natural tree"));
        }
        if(plans.size()==before)plans.add(new Plan(new Pos(t.base().getX(),t.base().getY(),t.base().getZ()),t,true,"HARVEST","Approaching a tree to clear obstructing leaves"));
        return true;
    }
    private Vec3 visiblePoint(Vec3 eyes,BlockPos b) {
        for(double offset:new double[]{.5,.15,.85}) {
            Vec3 point=new Vec3(b.getX()+.5,b.getY()+offset,b.getZ()+.5);
            var ray=mc.level.clip(new ClipContext(eyes,point,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,mc.player));
            if(ray.getType()==HitResult.Type.BLOCK && ray.getBlockPos().equals(b))return point;
        }
        return null;
    }
    private void outward() {
        Pos p=position();
        if(homeDistance(p)>maxDistance-24){beginReturn("Travel limit reached without enough suitable trees");return;}
        var path=findOutward(world,p,homeX,homeZ,5,24,6000);
        if(path.isEmpty()){terrain(p);beginReturn("No further safe walking route away from home");return;}
        setRoute(path,"SEARCH","Following reachable ground away from home");
    }
    private void setRoute(List<Pos> path,String next,String message) {
        route.clear();route.addAll(path);afterRoute=next;phase="NAVIGATE";reason=message;waypointStarted=System.currentTimeMillis();lastWaypoint=null;
    }
    private void move() {
        if(route.isEmpty()) {
            release();
            if(!phase.equals("RETURN")){phase=afterRoute;return;}
            while(!returnStops.isEmpty() && returnStops.peek().equals(position()))returnStops.remove();
            if(returnStops.isEmpty()){stop(logs()-baselineLogs>=targetLogs?"COMPLETE":"RETURNED",reason+"; returned to starting point",true);return;}
            var leg=find(world,position(),returnStops.peek(),4000);
            if(leg.isEmpty()){stop("STOPPED","A recorded return segment is no longer walkable at "+returnStops.peek(),true);return;}
            returnStops.remove();route.addAll(leg);lastWaypoint=null;
        }
        Pos target=route.peek();
        if(!target.equals(lastWaypoint)) {lastWaypoint=target;waypointStarted=System.currentTimeMillis();}
        double dx=target.x()+.5-mc.player.getX(),dz=target.z()+.5-mc.player.getZ();
        if(System.currentTimeMillis()-waypointStarted>5000) {stop("STOPPED","Walking stalled at "+target,true);return;}
        if(Math.hypot(dx,dz)<.19) {
            releaseMovement();mc.options.keyJump.setDown(mc.player.isInWater());
            if((mc.player.onGround() && Math.abs(mc.player.getY()-target.y())<.28)
                || (waterSupport(target) && mc.player.isInWater() && Math.abs(mc.player.getY()-target.y())<1.4))route.remove();return;
        }
        if(!world.canStand(target.x(),target.y(),target.z())) {stop("STOPPED","Return or travel route changed at "+target,true);return;}
        if(Math.hypot(dx,dz)>3.0 || target.y()-mc.player.getY()>1.5) {stop("STOPPED","Unexpected displacement from the planned path",true);return;}
        mc.player.setYRot((float)Math.toDegrees(Math.atan2(-dx,dz)));mc.player.setXRot(0);
        boolean slippery=blockId(new BlockPos(position().x(),position().y()-1,position().z())).contains("ice")
            || blockId(new BlockPos(target.x(),target.y()-1,target.z())).contains("ice");
        mc.options.keyShift.setDown(slippery && !mc.player.isInWater() && !waterSupport(target));
        mc.options.keyUp.setDown(true);mc.options.keySprint.setDown(false);
        mc.options.keyJump.setDown(mc.player.isInWater() || waterSupport(target) || (target.y()>mc.player.getY()+.45 && mc.player.onGround()));
    }
    private boolean axe() {
        int best=-1;double score=-1;
        for(int i=0;i<9;i++) {var s=mc.player.getInventory().getItem(i);String id=BuiltInRegistries.ITEM.getKey(s.getItem()).toString();
            int reserve=tree!=null ? Math.max(2,tree.logs().size()-logIndex+1) : 2;
            if(!id.endsWith("_axe") || s.getMaxDamage()-s.getDamageValue()<reserve)continue;
            double value=(s.getMaxDamage()-s.getDamageValue())+(id.contains("stone")?30:0);if(value>score){score=value;best=i;}}
        if(best<0)return false;mc.player.getInventory().setSelectedSlot(best);return true;
    }
    private void harvest() {
        releaseMovement();
        if(!Trees.revalidate(mc.level,tree,homeX,homeZ,radius)) {skipTree("Tree validation changed");return;}
        while(logIndex<tree.logs().size() && mc.level.getBlockState(tree.logs().get(logIndex)).isAir())logIndex++;
        if(logIndex==tree.logs().size()) {release();treesCut++;phase="LOOT";lootStarted=System.currentTimeMillis();return;}
        if(logIndex>=2) {
            Pos base=new Pos(tree.base().getX(),tree.base().getY(),tree.base().getZ());
            if(!isNear(position(),base,0,0) && world.canStand(base.x(),base.y(),base.z())) {
                var path=find(world,position(),base,1000);
                if(!path.isEmpty()){release();setRoute(path,"HARVEST","Moving beneath the upper trunk");return;}
            }
        }
        BlockPos b=tree.logs().get(logIndex);
        if(!Trees.safeLog(mc.level,b,homeX,homeZ,radius)) {skipTree("Log is protected or no longer safe");return;}
        Vec3 end=Vec3.atCenterOf(b),eyes=mc.player.getEyePosition();
        if(eyes.distanceTo(end)>mc.player.blockInteractionRange()-.15) {skipTree("Upper trunk is out of reach");return;}
        BlockHitResult hit=null;
        for(double offset:new double[]{.5,.15,.85}) {
            Vec3 point=new Vec3(b.getX()+.5,b.getY()+offset,b.getZ()+.5);
            var ray=mc.level.clip(new ClipContext(eyes,point,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,mc.player));
            if(ray.getType()==HitResult.Type.BLOCK && ray.getBlockPos().equals(b)){hit=ray;end=point;break;}
        }
        boolean trimming=false;
        if(hit==null) {
            var obstruction=mc.level.clip(new ClipContext(eyes,Vec3.atCenterOf(b),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,mc.player));
            BlockPos leaf=obstruction.getBlockPos();
            if(obstruction.getType()==HitResult.Type.BLOCK && Trees.safeLeaf(mc.level,leaf,homeX,homeZ,radius)
                && Math.abs(leaf.getX()-tree.base().getX())<=3 && Math.abs(leaf.getZ()-tree.base().getZ())<=3
                && leaf.getY()>=tree.base().getY() && leaf.getY()<=tree.base().getY()+6) {
                b=leaf;hit=obstruction;end=obstruction.getLocation();trimming=true;
            } else {skipTree("Trunk is obstructed");return;}
        }
        if(trimming || !axe()) {
            int handSlot=-1;
            if(trimming || !recoveryTrees.isEmpty())for(int i=0;i<9;i++)if(!mc.player.getInventory().getItem(i).isDamageableItem()){handSlot=i;break;}
            if(handSlot<0){beginReturn("No usable axe remains");return;}
            mc.player.getInventory().setSelectedSlot(handSlot);
        }
        double dx=end.x-eyes.x,dy=end.y-eyes.y,dz=end.z-eyes.z;
        mc.player.setYRot((float)Math.toDegrees(Math.atan2(-dx,dz)));mc.player.setXRot((float)-Math.toDegrees(Math.atan2(dy,Math.hypot(dx,dz))));
        if(!b.equals(digging)) {mc.options.keyAttack.setDown(false);background.releaseOwned();digging=b;harvestStarted=System.currentTimeMillis();}
        else if(System.currentTimeMillis()-harvestStarted>5000){skipTree("Mining did not progress");return;}
        // Use normal survival mining progress without relying on window focus.
        mc.options.keyAttack.setDown(false);background.mine(b,hit.getDirection());
    }
    private void skipTree(String message) {
        release();
        if(tree!=null && logIndex>0 && logIndex<tree.logs().size()) {
            if(!recoveryTrees.contains(tree))recoveryTrees.addFirst(tree);
            stop("STOPPED",message+"; remaining trunk saved at "+tree.base(),true);return;
        }
        if(tree!=null)skippedTrees.add(tree.base());reason=message;phase="LOOT";lootStarted=System.currentTimeMillis();
    }
    private void loot() {
        if(tree==null){phase="SEARCH";return;}
        Pos base=new Pos(tree.base().getX(),tree.base().getY(),tree.base().getZ());
        if(world.canStand(base.x(),base.y(),base.z()) && !isNear(position(),base,0,0)) {
            var path=find(world,position(),base,3000);
            if(!path.isEmpty()){setRoute(path,"LOOT","Picking up dropped logs");return;}
        }
        if(System.currentTimeMillis()-lootStarted<1800)return;
        skippedTrees.add(tree.base());tree=null;phase="SEARCH";
    }
    private void beginReturn(String message) {
        if(phase.equals("RETURN"))return;release();reason=message;
        route.clear();returnStops.clear();
        // Recheck one nearby segment at a time so distant unloaded chunks can load as we return.
        ArrayList<Pos> reverse=new ArrayList<>(eraseLoops(breadcrumbs));Collections.reverse(reverse);
        returnStops.addAll(reverse);
        phase="RETURN";lastWaypoint=null;waypointStarted=System.currentTimeMillis();
    }
    private void releaseMovement() {mc.options.keyUp.setDown(false);mc.options.keyJump.setDown(false);mc.options.keySprint.setDown(false);mc.options.keyShift.setDown(false);}
    private void release() {releaseMovement();mc.options.keyAttack.setDown(false);if(background!=null)background.releaseOwned();else if(mc.gameMode!=null)mc.gameMode.stopDestroyBlock();digging=null;}
    private void stop(String state,String message,boolean pause) {
        release();active=false;phase=state;reason=message;route.clear();plans.clear();returnStops.clear();
        if(background!=null){try{background.restore();background=null;}catch(Exception e){phase="ERROR";reason+="; restore failed: "+e.getMessage();}}
        if(ownsFocusSetting){mc.options.pauseOnLostFocus=previousPauseOnFocus;ownsFocusSetting=false;if(mc.player!=null)mc.player.getInventory().setSelectedSlot(previousSlot);}
        if(pause && mc.player!=null && mc.gui.screen()==null) mc.pauseGame(false);
    }
    private void scan() {
        if(mc.player==null || mc.level==null){reason="No open world";return;}
        Pos p=position();terrain(p);var result=new LinkedHashMap<String,Object>();result.put("surface",surface(p.x(),p.z(),14));
        result.put("trees",Trees.candidates(mc.level,p.x(),p.y(),p.z(),24,homeX,homeZ,radius));
        lastScan=json.toJson(result);reason="Read-only scan finished";
        try{write("scan.json",lastScan);}catch(Exception e){reason=e.toString();}
    }
    private void terrain(Pos center) {
        var rows=new ArrayList<Object>();
        for(int x=center.x()-32;x<=center.x()+32;x++)for(int z=center.z()-32;z<=center.z()+32;z++) {
            if(!mc.level.hasChunkAt(new BlockPos(x,64,z)))continue;
            int y=mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
            rows.add(List.of(x,y,z,blockId(new BlockPos(x,y-1,z)),blockId(new BlockPos(x,y,z)),world.canStand(x,y,z)));
        }
        try{write("terrain.json",json.toJson(Map.of("position",center,"columns",rows)));}catch(Exception ignored){}
    }
    private void status() throws Exception {
        Map<String,Object> s=new LinkedHashMap<>();s.put("updatedAt",Instant.now().toString());s.put("phase",phase);s.put("reason",reason);s.put("active",active);s.put("version",mc.getLaunchedVersion());s.put("commandId",commandId);
        if(mc.player!=null){s.put("position",List.of(mc.player.getX(),mc.player.getY(),mc.player.getZ()));s.put("health",mc.player.getHealth());s.put("food",mc.player.getFoodData().getFoodLevel());s.put("inventoryLogs",logs());s.put("collectedLogs",started==0?0:logs()-baselineLogs);s.put("homeDistance",homeDistance(position()));}
        s.put("targetLogs",targetLogs);s.put("protectedRadius",radius);s.put("treesCut",treesCut);s.put("remainingWaypoints",route.size()+returnStops.size());s.put("nextWaypoint",route.peek());s.put("elapsedSeconds",started==0?0:(System.currentTimeMillis()-started)/1000);s.put("paused",mc.isPaused());
        write("status.json",json.toJson(s));
        if(started>0)write("mission.json",json.toJson(Map.of("homeX",homeX,"homeZ",homeZ,"radius",radius,"targetLogs",targetLogs,"baselineLogs",baselineLogs,"start",start,"breadcrumbs",breadcrumbs,"recoveryTrees",recoveryTrees)));
    }
    private void write(String name,String value) throws Exception {
        Path target=dir.resolve("runtime/"+name),temp=dir.resolve("runtime/"+name+".tmp");Files.writeString(temp,value);
        try{Files.move(temp,target,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}catch(AtomicMoveNotSupportedException e){Files.move(temp,target,StandardCopyOption.REPLACE_EXISTING);}
    }
    @Override public void close() throws Exception {closed=true;scheduler.shutdownNow();mc.submit(()->{stop("STOPPED","Controller unloaded",true);try{status();}catch(Exception ignored){}}).get(5,TimeUnit.SECONDS);}
}
