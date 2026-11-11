''''
Geometric Algorithm Visualizer
Voronoi, Delaunay, Convex Hull

Modified so that it receives the senders simulated data & recomputes the structure.
(＿ ＿*) Z z z

    · threading & serial done
    · algorithm implementations done

ONLY CONT. LOGIC
'''

# libraries
import cv2 as cv
import numpy as np
import threading
import serial

# comunication configuration
WIDTH, HEIGHT = 600, 600
SERIAL_PORT = "/dev/pts/4"
BAUD_RATE = 9600

# thread configuration
shared_state = {
    "algorithm": "VOR",
    "points": [],
}
data_lock = threading.Lock()
running = True
LDR_THRESHOLD = 300 # considered on


# serial listener: drains the serial buffer and stores the last received frame
def serial_listener():
    global running, shared_state
    try:
        # init comm port object. port given → opens it ; etoc → returns serial object in closed state
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        ser.reset_input_buffer()
    except Exception as e:
        print(f"Error opening {SERIAL_PORT}: {e}")
        running = False
        return

    buffer = ""
    while running:
        try:
            # drain
            waiting = ser.in_waiting # returns #bits in the input buffer
            if waiting > 0:
                chunk = ser.read(waiting).decode("utf-8", errors="ignore")
                buffer += chunk

                # process msgs (\n ending)
                if "\n" in buffer:
                    lines = buffer.split("\n")
                    buffer = lines[-1]  # incomplete msg or empty txt
                    latest_line = lines[-2].strip()  # most recent full msg

                    # ALGORITHM;x1,y1,w1;x2,y2,w2;x3,y3,w3\n
                    if latest_line and ";" in latest_line:
                        parts = latest_line.split(";")

                        alg = parts[0]

                        parsed_points = []
                        for pair in parts[1:]:
                            coords = pair.split(",")
                            if len(coords) == 3:
                                parsed_points.append((int(coords[0]), int(coords[1]), int(coords[2])))
                            elif len(coords) == 2:
                                parsed_points.append(
                                    (int(coords[0]), int(coords[1]), 1023)
                                )

                        # act. thread state
                        with data_lock:
                            shared_state["algorithm"] = alg
                            shared_state["points"] = parsed_points
        except Exception:
            continue

    ser.close()


# algorithm implementation zZzz

def get_deterministic_color(point) -> tuple[int, int, int]:
    # spatial hash → each point has its unique seed based on its coordinates
    seed_val = int(abs(point[0]) * 73856093) ^ int(abs(point[1]) * 19349663)

    # random number generator → 2**31-1 mod (int32)
    rng = np.random.default_rng(seed=seed_val % (2**31 - 1))

    # 3 int in {50,219} → <50 dark & >220 bright
    return tuple(int(c) for c in rng.integers(50, 220, size=3))


def convex_hull(points, display):
    # convert list to numpy array, to match opencv point format (N, 1, 2) & int32
    vertex = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
    hull = cv.convexHull(vertex)
    cv.polylines(display, [hull], isClosed=True, color=(242, 172, 212), thickness=2)


def triangulation_coloring(points, display):
    coords = [(p[0], p[1]) for p in points]
    vertex = np.array(coords, dtype=np.int32).reshape((-1, 1, 2))
    hull = cv.convexHull(vertex)
    
    # extract vertex as [(x, y), ...]
    hull_pts = [tuple(p[0]) for p in hull]
    n = len(hull_pts)

    if n < 3: # shouldnt b happenin..
        return

    weight_map = {(p[0], p[1]): p[2] for p in points}
    
    # change 4 det. ?
    THREE_COLORS = [get_deterministic_color(hull_pts[i]) for i in range(3)]

    # fan triangulation starting at hull[0]
    root = hull_pts[0]
    for i in range(1, n - 1):
        pt_a = hull_pts[i]
        cv.line(display, root, pt_a, (160, 160, 180), 1, cv.LINE_AA)

    # ch contour
    cv.polylines(display, [hull], isClosed=True, color=(242, 172, 212), thickness=2)


    # 3color asignation
    colors_assigned = {0:0}
    for i in range(1, n):
        colors_assigned[i] = 1 if (i % 2 == 1) else 2

    # vertex
    for i, pt in enumerate(hull_pts):
        c_idx = colors_assigned[i]
        v_color = THREE_COLORS[c_idx]

        # weight → radius
        w = weight_map.get(pt, 100)
        radius = int(np.interp(w, [0, 1023], [5, 150]))

        # fill vertex
        cv.circle(display, pt, radius=radius, color=v_color, thickness=1, lineType=cv.LINE_AA)
        cv.circle(display, pt, radius=5, color=v_color, thickness=-1)

        # color tag
        cv.putText(display, str(c_idx), (pt[0] + 10, pt[1] - 5),
                   cv.FONT_HERSHEY_SIMPLEX, 0.45, v_color, 1, cv.LINE_AA)

        
def weighted_voronoi(pixel_coords, seeds, adc_lect):
    # lineal interpolation: light → weight
    weights = np.interp(adc_lect, [0, 1023], [0, 120]).astype(np.float32)

    # euclidian distance of every pixel to each one of the seeds (H, W, 4) 
    # (HEIGHT, WIDTH, 1, 2) - (1, 1, N, 2) = (HEIGHT, WIDTH, N, 2) → 2 = (x,y)
    dist = np.linalg.norm(pixel_coords - seeds, axis=-1) # axis -1 → pythagoras
   
    # additively weighted distance D = d(p, seed_i) - weight_i
    pond_dist = dist - weights
    winner_seed = np.argmin(pond_dist, axis=-1)
    return winner_seed


def weighted_delaunay(region_map):

    # horizontal neighbors
    diff_h = region_map[:, :-1] != region_map[:, 1:] # if they differ it means theres a edge there
    pairs_h = np.stack([region_map[:, :-1][diff_h], region_map[:, 1:][diff_h]], axis=-1) 

    # vertical neighbors
    diff_v = region_map[:-1, :] != region_map[1:, :]
    pairs_v = np.stack([region_map[:-1, :][diff_v], region_map[1:, :][diff_v]], axis=-1)

    all_pairs = np.vstack([pairs_h, pairs_v])
    if len(all_pairs) == 0:
        return set()

    # remove dupes
    ordered_pairs = np.sort(all_pairs, axis=1)
    unique_edges = {tuple(edge) for edge in np.unique(ordered_pairs, axis=0)}
    return unique_edges


# main logic
def main():
    global running

    # init thread
    t = threading.Thread(target=serial_listener, daemon=True)
    t.start()
    
    point_color = (140, 220, 180)
    cv.namedWindow("Serial Visualizer", cv.WINDOW_AUTOSIZE)

    while running:
        with data_lock:
            raw_pts = list(shared_state["points"])
            alg = shared_state["algorithm"]

        # create canvas to display the results
        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        alg_tag = "Waitin... (_ _*) Z z z"

        # active points filtering
        pts = [
                 (pt[0], pt[1]) for pt in raw_pts if pt[2] >= LDR_THRESHOLD
              ]
        
        if len(pts) >= 3:
            if alg == "CH":
                convex_hull(pts, canvas)
                alg_tag = "Convex Hull"

            elif alg == "3CH":
                raw_pts = [pt for pt in raw_pts if pt[2] >= LDR_THRESHOLD]
                triangulation_coloring(raw_pts, canvas)
                alg_tag = "Convex Hull & 3-Colored Fan Triangulation"

            else:
                # coordinates grid to calculate distance
                grid_x, grid_y = np.meshgrid(np.arange(WIDTH), np.arange(HEIGHT))
                pixel_coords = np.stack([grid_x, grid_y], axis=-1)[:, :, np.newaxis, :] # pixel matrix

                # adc lect. →  a point never truly dissapears so indexing is fine
                seeds = [(pt[0], pt[1]) for pt in raw_pts]
                seeds_arr = np.array(seeds, dtype=np.float32) # N seeds list → (N,2) matrix
                adc_lect = [pt[2] for pt in raw_pts]

                region_map = weighted_voronoi(pixel_coords, seeds_arr, adc_lect)

                if alg == "VOR":
                    # pixel color → winner seed
                    palette = np.array([get_deterministic_color(s) for s in seeds], dtype=np.uint8)
                    canvas = palette[region_map]
                    alg_tag = "Weigthed Voronoi Tesellation"

                elif alg == "DEL":
                    # laguerre dual
                    dual_edges = weighted_delaunay(region_map)
                    # for each pair (u, v) in edge it draws a segment connecting the 2 collindant seeds
                    for u, v in dual_edges:
                        p1 = tuple(seeds_arr[u].astype(int))
                        p2 = tuple(seeds_arr[v].astype(int))
                        cv.line(canvas, p1, p2, (130, 230, 210), 2, cv.LINE_AA)
                    alg_tag = "Weighted Delaunay Triangulation"

        if alg != "3CH":
            # draw the set of points on the canvas
            for pt in raw_pts:
                center = (int(pt[0]), int(pt[1]))
                weight = pt[2]
                is_active = weight >= LDR_THRESHOLD

                weighted_radius = int(np.interp(weight, [0, 1023], [5, 150]))
                
                if is_active:
                    cv.circle(canvas, center, radius=5, color=point_color, thickness=-1) # -1 fill
                    cv.circle(canvas, center, radius=weighted_radius, color=(200, 200, 200), thickness=1) #  1 outline

                else:
                    cv.circle(canvas, center, radius=5, color=(150, 150, 150), thickness=-1) # -1 fill
                    cv.circle(canvas, center, radius=6, color=(90, 90, 90), thickness=1) #  1 outline

        # 3CH has its own coloring method
        else:       
            for pt in raw_pts:
                if pt[2] < LDR_THRESHOLD:
                    center = (int(pt[0]), int(pt[1]))
                    cv.circle(canvas, center, radius=4, color=(90, 90, 90), thickness=-1)

        # windows display
        cv.putText(canvas, f"Algorithm: {alg_tag} | Active Points: {len(pts)}", (20, 35),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv.LINE_AA)

        cv.imshow("Serial Visualizer", canvas)

        # esc key
        if (cv.waitKey(15) & 0xFF) == 27:
            running = False
            break

    cv.destroyAllWindows()


if __name__ == "__main__":
    main()