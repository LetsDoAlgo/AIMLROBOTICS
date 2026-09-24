# **AIML ZG528 – Assignment 1: Probabilistic Motion & Sensor Models**
## **Part A – Question 2: Motion Model Implementation**

| | |
|---|---|
| **Domain** | Hospitality Bots (Restaurant Food Delivery) |
| **Date** | May 2026 |

**Team Members:**

| Name | ID | Contribution |
|------|-----|-------------|
| Ayushi Gupta | 2024AC05720 | 100% |

---

### **Problem Statement**

A restaurant has a small wheeled robot (differential-drive AMR) that delivers food plates from the kitchen counter to dining tables.

**Environment:**
- Rectangular restaurant floor (10m × 8m)
- Kitchen counter on the left, 4 dining tables
- Walls as obstacle boundaries

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import norm

%matplotlib inline
np.random.seed(42)
```

## **Step 1: Velocity-Based Motion Model**

**Inputs at each time step:**
- $v$ — translational velocity (forward speed)
- $\omega$ — rotational velocity (turn rate)

**Noise injection** (models wheel slippage, motor imprecision):

$$\hat{v} = v + \mathcal{N}(0,\; \alpha_1 v^2 + \alpha_2 \omega^2)$$
$$\hat{\omega} = \omega + \mathcal{N}(0,\; \alpha_3 v^2 + \alpha_4 \omega^2)$$
$$\hat{\gamma} = \mathcal{N}(0,\; \alpha_5 v^2 + \alpha_6 \omega^2)$$

**Position update (circular arc):**

$$x' = x - \frac{\hat{v}}{\hat{\omega}} \sin\theta + \frac{\hat{v}}{\hat{\omega}} \sin(\theta + \hat{\omega}\,\Delta t)$$
$$y' = y + \frac{\hat{v}}{\hat{\omega}} \cos\theta - \frac{\hat{v}}{\hat{\omega}} \cos(\theta + \hat{\omega}\,\Delta t)$$
$$\theta' = \theta + \hat{\omega}\,\Delta t + \hat{\gamma}\,\Delta t$$

**Noise parameters:**

| Parameter | Controls |
|-----------|----------|
| $\alpha_1, \alpha_2$ | Noise on forward speed |
| $\alpha_3, \alpha_4$ | Noise on turn rate |
| $\alpha_5, \alpha_6$ | Heading drift noise |

Higher values → more uncertainty in motion.

```python
# Restaurant layout - walls defined as line segments [(start_x, start_y), (end_x, end_y)]
restaurant_walls = [
    [(0, 0), (10, 0)],    # Bottom wall
    [(10, 0), (10, 8)],   # Right wall
    [(10, 8), (0, 8)],    # Top wall
    [(0, 8), (0, 0)],     # Left wall
    [(0, 5), (2.5, 5)],   # Kitchen counter
]

# Table positions (center x, center y)
tables = [
    (4.5, 2.0),  # Table 1
    (7.5, 2.0),  # Table 2
    (4.5, 6.0),  # Table 3
    (7.5, 6.0),  # Table 4
]

# Add table edges as walls (1m x 1m squares)
for tx, ty in tables:
    half = 0.5
    restaurant_walls.append([(tx-half, ty-half), (tx+half, ty-half)])
    restaurant_walls.append([(tx+half, ty-half), (tx+half, ty+half)])
    restaurant_walls.append([(tx+half, ty+half), (tx-half, ty+half)])
    restaurant_walls.append([(tx-half, ty+half), (tx-half, ty-half)])


def draw_restaurant(ax, title="Restaurant Layout"):
    """Draw the restaurant environment from top-down view."""
    for wall in restaurant_walls[:5]:
        xs = [wall[0][0], wall[1][0]]
        ys = [wall[0][1], wall[1][1]]
        ax.plot(xs, ys, 'k-', linewidth=2.5)
    
    for i, (tx, ty) in enumerate(tables):
        table_patch = mpatches.Rectangle((tx-0.5, ty-0.5), 1, 1, 
                                          color='saddlebrown', alpha=0.6)
        ax.add_patch(table_patch)
        ax.text(tx, ty, f'T{i+1}', ha='center', va='center', 
                fontsize=9, color='white', fontweight='bold')
    
    ax.text(1.0, 6.5, 'KITCHEN', fontsize=10, ha='center', color='darkgreen', fontweight='bold')
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.5, 9)
    ax.set_aspect('equal')
    ax.set_xlabel('X position (meters)')
    ax.set_ylabel('Y position (meters)')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.2)


# Visualize the restaurant
fig, ax = plt.subplots(figsize=(10, 8))
draw_restaurant(ax, "Restaurant Floor Plan (Bird's Eye View)")

planned_path = [(1.0, 3.0), (3.0, 3.0), (3.0, 6.0), (4.0, 6.0)]
path_x = [p[0] for p in planned_path]
path_y = [p[1] for p in planned_path]
ax.plot(path_x, path_y, 'g--o', linewidth=2, markersize=8, label='Planned path to Table 3')
ax.plot(1.0, 3.0, 'r^', markersize=15, label='Robot start')
ax.plot(4.0, 6.0, 'b*', markersize=15, label='Delivery point (Table 3)')
ax.legend(loc='upper right', fontsize=9)
plt.tight_layout()
plt.show()
```

```python
def velocity_motion_model(pose, command, noise_params, dt):
    """
    Probabilistic velocity motion model.
    
    Parameters:
        pose: [x, y, theta] - current robot pose
        command: [v, omega] - translational and rotational velocity
        noise_params: [a1, a2, a3, a4, a5, a6] - noise parameters
        dt: time step (seconds)
    
    Returns:
        new_pose: [x_new, y_new, theta_new]
    """
    x, y, theta = pose
    v, omega = command
    a1, a2, a3, a4, a5, a6 = noise_params
    
    # Sample noisy velocities
    v_actual = v + np.random.normal(0, np.sqrt(a1 * v**2 + a2 * omega**2))
    omega_actual = omega + np.random.normal(0, np.sqrt(a3 * v**2 + a4 * omega**2))
    drift = np.random.normal(0, np.sqrt(a5 * v**2 + a6 * omega**2))
    
    # Compute new position
    if abs(omega_actual) > 1e-4:
        radius = v_actual / omega_actual
        x_new = x - radius * np.sin(theta) + radius * np.sin(theta + omega_actual * dt)
        y_new = y + radius * np.cos(theta) - radius * np.cos(theta + omega_actual * dt)
        theta_new = theta + omega_actual * dt + drift * dt
    else:
        x_new = x + v_actual * np.cos(theta) * dt
        y_new = y + v_actual * np.sin(theta) * dt
        theta_new = theta + drift * dt
    
    theta_new = (theta_new + np.pi) % (2 * np.pi) - np.pi
    return np.array([x_new, y_new, theta_new])


def ideal_motion(pose, command, dt):
    """Noise-free motion model for comparison."""
    x, y, theta = pose
    v, omega = command
    
    if abs(omega) > 1e-4:
        radius = v / omega
        x_new = x - radius * np.sin(theta) + radius * np.sin(theta + omega * dt)
        y_new = y + radius * np.cos(theta) - radius * np.cos(theta + omega * dt)
        theta_new = theta + omega * dt
    else:
        x_new = x + v * np.cos(theta) * dt
        y_new = y + v * np.sin(theta) * dt
        theta_new = theta
    
    theta_new = (theta_new + np.pi) % (2 * np.pi) - np.pi
    return np.array([x_new, y_new, theta_new])


# Quick verification
test_result = ideal_motion([0, 0, 0], [1.0, 0], 1.0)
print(f"Ideal motion test: go forward 1 m/s for 1s → x={test_result[0]:.2f}, y={test_result[1]:.2f}")
```

## **Step 2: Monte Carlo Simulation of Delivery Route**

**Objective:** Simulate 100 deliveries (kitchen → Table 3) with noise to observe outcome spread.

**Simulation parameters:**
- Time step: 0.5s
- Noise profile: smooth tile floor
- Start pose: (1.0, 3.0), facing right

```python
dt = 0.5              # Time step (seconds)
num_simulations = 100

# Noise parameters [a1, a2, a3, a4, a5, a6] - typical smooth tile floor
noise_alpha = [0.02, 0.01, 0.01, 0.02, 0.005, 0.005]

# Starting pose: kitchen area, facing right
start = np.array([1.0, 3.0, 0.0])

# Route: (speed, turn_rate, number_of_steps)
route = [
    (0.5, 0.0, 8),         # Segment 1: Go straight (≈2m)
    (0.2, np.pi/4, 4),     # Segment 2: Turn left 90°
    (0.5, 0.0, 10),        # Segment 3: Go straight toward Table 3 (≈2.5m)
]

# Run simulations with noise
all_paths = []
for sim in range(num_simulations):
    path = [start.copy()]
    current_pose = start.copy()
    for speed, turn_rate, num_steps in route:
        for step in range(num_steps):
            current_pose = velocity_motion_model(current_pose, [speed, turn_rate], noise_alpha, dt)
            path.append(current_pose.copy())
    all_paths.append(np.array(path))

# Compute ideal path (no noise)
ideal_path = [start.copy()]
current_pose = start.copy()
for speed, turn_rate, num_steps in route:
    for step in range(num_steps):
        current_pose = ideal_motion(current_pose, [speed, turn_rate], dt)
        ideal_path.append(current_pose.copy())
ideal_path = np.array(ideal_path)

# Results
final_positions = np.array([path[-1, :2] for path in all_paths])
print(f"Simulation: {num_simulations} deliveries, {len(ideal_path)-1} steps each")
print(f"Ideal end position: ({ideal_path[-1,0]:.2f}, {ideal_path[-1,1]:.2f})")
print(f"Actual mean end: ({final_positions[:,0].mean():.2f}, {final_positions[:,1].mean():.2f})")
print(f"Spread (std): X ±{final_positions[:,0].std():.3f}m, Y ±{final_positions[:,1].std():.3f}m")
```

## **Step 3: Trajectory Uncertainty Visualization**

**What the plot shows:**
- Left: 100 noisy trajectories overlaid on the restaurant map
- Right: Final position scatter with confidence ellipses (1σ = 68%, 2σ = 95%)

**Key observation:** Spread increases over time → growing positional uncertainty.

```python
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Plot 1: All trajectories in restaurant
ax = axes[0]
draw_restaurant(ax, "100 Simulated Deliveries (Kitchen → Table 3)")
for path in all_paths:
    ax.plot(path[:, 0], path[:, 1], 'b-', alpha=0.1, linewidth=0.7)
ax.plot(ideal_path[:, 0], ideal_path[:, 1], 'r-', linewidth=3, label='Ideal path')
ax.plot(start[0], start[1], 'r^', markersize=14, label='Start')
ax.plot(ideal_path[-1,0], ideal_path[-1,1], 'r*', markersize=16, label='Goal')
ax.legend(loc='upper right', fontsize=9)

# Plot 2: Final position distribution with confidence ellipses
ax = axes[1]
ax.scatter(final_positions[:, 0], final_positions[:, 1], 
           c='blue', alpha=0.5, s=30, label='Final positions (100 runs)')
ax.plot(ideal_path[-1,0], ideal_path[-1,1], 'r*', markersize=20, label='Ideal goal')

# Confidence ellipses
mean_pos = final_positions.mean(axis=0)
cov_matrix = np.cov(final_positions.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
angle = np.degrees(np.arctan2(eigenvectors[1, 1], eigenvectors[0, 1]))

ellipse_1 = mpatches.Ellipse(mean_pos, 2*np.sqrt(eigenvalues[1]), 2*np.sqrt(eigenvalues[0]),
                              angle=angle, fill=False, color='red', linestyle='--', linewidth=2,
                              label='1σ (68%) region')
ax.add_patch(ellipse_1)

ellipse_2 = mpatches.Ellipse(mean_pos, 4*np.sqrt(eigenvalues[1]), 4*np.sqrt(eigenvalues[0]),
                              angle=angle, fill=False, color='orange', linestyle=':', linewidth=2,
                              label='2σ (95%) region')
ax.add_patch(ellipse_2)

ax.set_xlabel('X (meters)')
ax.set_ylabel('Y (meters)')
ax.set_title('Final Position Uncertainty', fontweight='bold')
ax.legend(fontsize=9)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## **Step 4: Beam-Based Sensor Model**

**Model:** LiDAR reading $z$ given true distance $z^*$ is a 4-component mixture:

$$p(z \mid z^*) = w_{hit} \cdot p_{hit}(z) + w_{short} \cdot p_{short}(z) + w_{max} \cdot p_{max}(z) + w_{rand} \cdot p_{rand}(z)$$

| Component | Distribution | Physical Meaning |
|-----------|-------------|-----------------|
| $p_{hit}$ | $\mathcal{N}(z^*, \sigma^2)$ | Normal reading with noise |
| $p_{short}$ | $\lambda e^{-\lambda z} / (1 - e^{-\lambda z^*})$ | Unexpected obstacle blocks beam |
| $p_{max}$ | Point mass at $z_{max}$ | Beam returns max range |
| $p_{rand}$ | Uniform$(0, z_{max})$ | Random sensor glitch |

**Parameters used:**

| Parameter | Value | Meaning |
|-----------|-------|---------|
| $w_{hit}$ | 0.70 | 70% normal readings |
| $w_{short}$ | 0.15 | 15% short readings |
| $w_{max}$ | 0.05 | 5% max range |
| $w_{rand}$ | 0.10 | 10% random |
| $\sigma$ | 0.15 m | Gaussian noise |
| $\lambda$ | 1.0 | Short-reading decay |
| $z_{max}$ | 8.0 m | Max sensor range |

```python
class BeamSensorModel:
    """Beam-based LiDAR sensor model with 4-component mixture."""
    
    def __init__(self):
        self.z_max = 8.0
        self.sigma_hit = 0.15
        self.lambda_short = 1.0
        self.w_hit = 0.70
        self.w_short = 0.15
        self.w_max = 0.05
        self.w_rand = 0.10
    
    def get_measurement(self, true_distance):
        """Generate a noisy sensor reading given the true distance."""
        reading_type = np.random.choice(
            ['hit', 'short', 'max', 'rand'],
            p=[self.w_hit, self.w_short, self.w_max, self.w_rand]
        )
        
        if reading_type == 'hit':
            z = np.clip(np.random.normal(true_distance, self.sigma_hit), 0, self.z_max)
        elif reading_type == 'short':
            z = np.random.uniform(0, true_distance)
        elif reading_type == 'max':
            z = self.z_max
        else:
            z = np.random.uniform(0, self.z_max)
        
        return z
    
    def probability(self, measurement, true_distance):
        """Compute p(z | z*) for a given measurement and true distance."""
        p = 0.0
        
        if 0 <= measurement <= self.z_max:
            p += self.w_hit * norm.pdf(measurement, true_distance, self.sigma_hit)
        
        if 0 <= measurement <= true_distance and true_distance > 0:
            p += self.w_short * (self.lambda_short * 
                  np.exp(-self.lambda_short * measurement) /
                  (1 - np.exp(-self.lambda_short * true_distance)))
        
        if abs(measurement - self.z_max) < 0.05:
            p += self.w_max * 1.0
        
        if 0 <= measurement < self.z_max:
            p += self.w_rand * (1.0 / self.z_max)
        
        return p


def ray_cast_distance(robot_pose, beam_angle, walls, max_range=8.0):
    """Compute true distance to nearest wall via ray-segment intersection."""
    x, y, theta = robot_pose
    angle = theta + beam_angle
    dx, dy = np.cos(angle), np.sin(angle)
    
    closest_distance = max_range
    for wall in walls:
        (x1, y1), (x2, y2) = wall
        denom = dx * (y1 - y2) - dy * (x1 - x2)
        if abs(denom) < 1e-10:
            continue
        t = ((x1 - x) * (y1 - y2) - (y1 - y) * (x1 - x2)) / denom
        u = -((dx) * (y1 - y) - (dy) * (x1 - x)) / denom
        if t > 0 and 0 <= u <= 1 and t < closest_distance:
            closest_distance = t
    
    return closest_distance


sensor = BeamSensorModel()
print(f"Sensor model: z_max={sensor.z_max}m, σ={sensor.sigma_hit}m")
print(f"Weights: hit={sensor.w_hit}, short={sensor.w_short}, max={sensor.w_max}, rand={sensor.w_rand}")
```

## **Step 5: Sensor Model Visualization**

**Plots:**
- Left: Probability distribution $p(z \mid z^*=3m)$ — shows what readings are likely
- Right: Histogram of 500 sampled readings — shows actual measurement spread

```python
true_dist = 3.0  # True distance to wall
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Probability distribution p(z | z*=3m)
ax = axes[0]
z_range = np.linspace(0, 8, 400)
probabilities = [sensor.probability(z, true_dist) for z in z_range]
ax.plot(z_range, probabilities, 'k-', linewidth=2, label='p(z|z*=3m)')
ax.axvline(x=true_dist, color='red', linestyle='--', linewidth=2, label=f'True distance = {true_dist}m')
ax.fill_between(z_range, probabilities, alpha=0.2, color='steelblue')
ax.set_xlabel('Sensor reading z (meters)')
ax.set_ylabel('Probability density')
ax.set_title('Beam Model PDF (z* = 3.0m)', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Plot 2: Histogram of sampled readings
ax = axes[1]
n_readings = 500
readings = [sensor.get_measurement(true_dist) for _ in range(n_readings)]
ax.hist(readings, bins=40, density=True, alpha=0.7, color='steelblue', edgecolor='black')
ax.axvline(x=true_dist, color='red', linestyle='--', linewidth=2.5, label=f'True = {true_dist}m')
ax.set_xlabel('Sensor reading (meters)')
ax.set_ylabel('Frequency (density)')
ax.set_title(f'Sampled Sensor Readings (n={n_readings})', fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"True distance: {true_dist:.1f}m | Mean reading: {np.mean(readings):.3f}m | Std: {np.std(readings):.3f}m")
```

## **Step 6: Combined Motion + Sensing Demo**

**Workflow at each time step:**
1. Robot moves → motion model adds positional noise
2. From new pose → sensor model adds measurement noise
3. Repeat for entire delivery route

**Visualization:** LiDAR beams (8 directions) shown at 3 key positions:
- After 5 straight steps
- After turning
- At final delivery position

```python
np.random.seed(99)

# Simulate one delivery with motion noise
delivery_path = [start.copy()]
current_pose = start.copy()
for speed, turn_rate, num_steps in route:
    for step in range(num_steps):
        current_pose = velocity_motion_model(current_pose, [speed, turn_rate], noise_alpha, dt)
        delivery_path.append(current_pose.copy())
delivery_path = np.array(delivery_path)

# Sense at 3 positions along the path
sense_indices = [5, 12, len(delivery_path)-1]
sense_labels = ['After 5 steps', 'After turning', 'Final position']

num_beams = 8
beam_angles = np.linspace(0, 2*np.pi, num_beams, endpoint=False)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for plot_idx, (step_idx, label) in enumerate(zip(sense_indices, sense_labels)):
    ax = axes[plot_idx]
    draw_restaurant(ax, f"Sensing: {label}")
    
    ax.plot(delivery_path[:step_idx+1, 0], delivery_path[:step_idx+1, 1], 
            'b-', linewidth=2, alpha=0.7)
    
    robot_pose = delivery_path[step_idx]
    rx, ry, rtheta = robot_pose
    
    true_dists = [ray_cast_distance(robot_pose, a, restaurant_walls) for a in beam_angles]
    noisy_dists = [sensor.get_measurement(d) for d in true_dists]
    
    for i, angle in enumerate(beam_angles):
        global_angle = rtheta + angle
        true_x = rx + true_dists[i] * np.cos(global_angle)
        true_y = ry + true_dists[i] * np.sin(global_angle)
        ax.plot([rx, true_x], [ry, true_y], 'g--', alpha=0.3, linewidth=1)
        
        noisy_x = rx + noisy_dists[i] * np.cos(global_angle)
        noisy_y = ry + noisy_dists[i] * np.sin(global_angle)
        ax.plot([rx, noisy_x], [ry, noisy_y], 'r-', alpha=0.5, linewidth=1.5)
        ax.plot(noisy_x, noisy_y, 'rx', markersize=6, markeredgewidth=2)
    
    ax.plot(rx, ry, 'ko', markersize=10)
    ax.arrow(rx, ry, 0.5*np.cos(rtheta), 0.5*np.sin(rtheta),
             head_width=0.15, head_length=0.1, fc='black', ec='black')
    
    ax.plot([], [], 'g--', label='True distances')
    ax.plot([], [], 'r-x', label='Noisy readings')
    ax.legend(fontsize=7, loc='upper right')

plt.suptitle('Motion Model → Sensor Model (sequential operation)', fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
```

## **Step 7: Effect of Floor Conditions on Motion Uncertainty**

**Comparison of 3 surface types:**

| Floor Type | Noise Level | α₁ value | Expected Behavior |
|-----------|-------------|----------|-------------------|
| Rubber mat (kitchen) | Low | 0.005 | Tight path clustering |
| Wooden floor (dining) | Medium | 0.02 | Moderate spread |
| Wet/spill area | High | 0.08 | Large deviation from ideal |

```python
floor_configs = {
    'Rubber Mat (Low Noise)': [0.005, 0.003, 0.003, 0.005, 0.002, 0.002],
    'Wooden Floor (Medium Noise)': [0.02, 0.01, 0.01, 0.02, 0.005, 0.005],
    'Wet/Spill Area (High Noise)': [0.08, 0.05, 0.05, 0.08, 0.02, 0.02],
}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, (title, alpha_noise) in enumerate(floor_configs.items()):
    ax = axes[idx]
    draw_restaurant(ax, title)
    
    for _ in range(50):
        path = [start.copy()]
        pose = start.copy()
        for speed, turn_rate, num_steps in route:
            for step in range(num_steps):
                pose = velocity_motion_model(pose, [speed, turn_rate], alpha_noise, dt)
                path.append(pose.copy())
        path = np.array(path)
        ax.plot(path[:, 0], path[:, 1], 'b-', alpha=0.2, linewidth=0.8)
    
    ax.plot(ideal_path[:, 0], ideal_path[:, 1], 'r-', linewidth=2.5, label='Ideal path')
    ax.plot(start[0], start[1], 'r^', markersize=12)
    ax.legend(fontsize=8, loc='upper right')

plt.suptitle('Motion Uncertainty vs. Floor Condition', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
```

## **Summary**

| Component | Implementation | Key Insight |
|-----------|---------------|-------------|
| Velocity motion model | `velocity_motion_model()` with α₁–α₆ | Faster motion → more positional uncertainty |
| Beam sensor model | `BeamSensorModel` (hit + short + max + rand) | Sensor readings are noisy mixtures |
| Monte Carlo simulation | 100 trajectory samples + confidence ellipses | Uncertainty grows over time |
| Floor condition analysis | 3 noise levels compared | Surface grip directly impacts reliability |

**Key Takeaways:**
- Motion model → **prediction step** (where the robot might be)
- Sensor model → **correction step** (what the robot observes)
- Together they form the foundation for Bayes filtering and particle-filter-based localization
- Essential for safe autonomous navigation in the restaurant environment
