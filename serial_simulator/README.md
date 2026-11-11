# Real-Time Geometric Algorithm Visualizer
꒰ᐢ. .ᐢ꒱
. ݁₊ ⊹ . ݁˖ . ݁

Serial communication simulation between two independent processes: an emitter that generates $N$ points with stochastic luminosity variations (simulating analog LDR sensor readings) and a visualizer that dynamically computes and renders geometric structures in real time.


## Operating Modes

### 1. `Blink`
Points toggle their state between *active* and *inactive* based on thresholded sensor readings.
* **Convex Hull (CH)**
* **Delaunay Triangulation**
* **Voronoi Tessellation** 

### 2. `Weighted`
Sensor readings are directly mapped to weights ($w_i$) associated with each point.
* **Triangulated and 3-Colored Convex Hull:** The convex hull is internally triangulated and colored using a graph 3-coloring algorithm.
* **Additively Weighted Voronoi Diagram:** Voronoi cells computed using the additive metric ($d_i(x) = \|x - p_i\| - w_i$), where the simulated light intensity sets each site's radial influence.
* **Regular Triangulation / Dual Weighted Delaunay:** Dual weighted triangulation corresponding to the additively weighted sites.


## Quickstart 

### Prerequisites

* **Operating System:** Linux  
* **System Utilities:** `socat`
* **Python 3.x Dependencies:**
  ```bash
  pip install numpy scipy matplotlib pyserial
  ```

---

### Execution Steps

#### 1. Create Virtual Serial Bridge
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

`socat` will print the assigned device descriptors, for example:
```text
2026/11/10 23:15:00 socat[1234] N PTY is /dev/pts/2
2026/11/10 23:15:00 socat[1234] N PTY is /dev/pts/3
```

*(Keep this terminal running in the background throughout the session).*

> **Note:** currently, configure the serial port path directly in the script (e.g., set to `/dev/pts/2` to the visualizer, and `/dev/pts/3` to the emmiter):

---

#### 2. Start the Visualizer (Receiver)
```bash
# blink mode visualizer
python visualizer_serial_blink.py

# weighted mode visualizer
python visualizer_serial_weighted.py
```

---

#### 3. Start the Simulation (Sender)

```bash
python sender.py 
```

## to-do ('''– ⌓ –)＝３

* **CLI Argument Parsing:** Add command-line flag support.
* **Unified Visualizer Script:** Merge `visualizer_serial_blink.py` and `visualizer_serial_weighted.py` into a single script with a `--mode` toggle.