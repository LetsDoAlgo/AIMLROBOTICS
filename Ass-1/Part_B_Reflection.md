# Part B – Individual Reflection (3 Marks)

| | |
|---|---|
| **Name** | Ayushi Gupta |
| **BITS ID** | 2024AC05720 |
| **Course** | AIML ZG528 – Assignment 1 |
| **Date** | June 2026 |

---

## Template for Form Submission

---

### 1. Workplace Connection (1 Mark)

- I currently work at ABB in the digital domain — building software solutions for industrial automation. While my day-to-day work involves data platforms and application development, ABB Robotics is where I aspire to contribute next.
- Two concepts from this assignment stood out as relevant to that aspirational direction:
  - **Probabilistic motion modeling** — robots in ABB's factories never move with perfect precision. Payload variations, mechanical wear, and environmental factors introduce uncertainty that software systems need to handle intelligently.
  - **Beam-based sensor models** — factory floors have dynamic obstacles (forklifts, workers, reflective metal surfaces) that sensors must account for, and understanding how to model this probabilistically is essential for anyone building robotics software.
- This assignment gave me a concrete technical foundation that bridges my current software skills with the robotics domain I want to move into.

---

### 2. Learning Reflection (1 Mark)

- The biggest takeaway was realizing how **motion uncertainty compounds over time**. Even small noise in velocity commands leads to significant positional drift. In ABB Robotics, this directly affects robotic arm repeatability — small joint-level errors accumulate through the kinematic chain and result in end-effector deviation during precision welding or assembly tasks.
- I found it eye-opening how the beam sensor model handles the "unexpected short reading" case. When a forklift or worker suddenly crosses a sensor's field, the exponential short-reading component captures this naturally — no special detection logic is needed. It just falls out of the math.
- Working with the velocity motion model taught me how much tuning the noise parameters (α values) matters. A robot carrying a heavy payload behaves very differently from one running unloaded — and as someone from the software side, I now understand why robotics teams spend so much effort on parameter calibration.

---

### 3. Skill Development (1 Mark)

- This assignment helped me bridge the gap between textbook probability theory (Gaussian distributions, mixture models) and actual working code. I can now implement these models in Python and produce visualizations that communicate results clearly.
- I developed a stronger sense of systems thinking — the motion model and sensor model are not independent; they must work together for reliable autonomy.
- As someone working in ABB's digital domain, I also gained an appreciation for how physical-world factors (payload, wear, dynamic obstacles) drive the software and algorithm choices in robotics.
- Going forward, I plan to leverage these skills to:
  - Build digital-twin simulations that incorporate probabilistic motion models for ABB's robotic arm cells
  - Contribute to software modules that handle sensor fusion and uncertainty estimation
  - Position myself for a transition into ABB Robotics, where these skills are directly needed

---

## Google Form Questions & Responses

---

**Q: Is there a scope of using Mobile Robots in your work environment?**

**A:**
- Not in my current digital/software role directly, but absolutely in the broader ABB context.
- ABB Robotics operates factory floors where material transport between robotic arm cells is still largely manual. There is clear scope for mobile robots to automate inter-station logistics — and as someone building digital solutions, I could contribute to the software and navigation stack for such deployments.

---

**Q: How does this assignment relate to your current or aspirational workplace? Which robotics concept(s) did you find directly applicable to your field?**

**A:**
- I currently work in ABB's digital domain (software and data solutions for industrial automation). My aspirational direction is ABB Robotics, where these concepts are directly applied every day.
- The **probabilistic motion model** is highly relevant — ABB's robotic arms (IRB series) face positional uncertainty from payload variations, joint wear, and thermal drift. Building software that accounts for this uncertainty is exactly where my skills could contribute.
- The **beam-based sensor model** applies to how safety sensors around robotic arm cells detect human workers and dynamic obstacles — understanding this from a software perspective helps me design better monitoring and decision-making systems.

---

**Q: What practical insights did you gain about robot motion or sensing from the implementation?**

**A:**
- I saw firsthand how motion uncertainty accumulates rapidly. Even small errors compound into significant drift — this is why ABB's robotic arms need regular recalibration, especially after payload changes or extended operation.
- The sensor model's four components (hit, short, max, random) map neatly to real factory scenarios:
  - Forklift suddenly crossing a sensor beam → short reading
  - Long open aisles → max-range return
  - Reflective metal surfaces on factory floors → random noise component
- Coming from a software background, this gave me a much better intuition for what the algorithms need to handle — it's not just clean data going into neat functions.

---

**Q: What was the most challenging or eye-opening part of the task?**

**A:**
- The most eye-opening moment was visualizing how drastically the noise parameters (α values) change the trajectory spread.
- When I cranked up the noise to simulate high-uncertainty conditions, the positional uncertainty grew so large that the robot would completely miss its target — this showed me, viscerally, why ABB Robotics invests so heavily in precision encoders and calibration routines.
- As someone from the digital side, it made me appreciate that robotics software isn't just about clean algorithms — it's about dealing with messy physical reality, and that's what makes it interesting to me.

---

**Q: How did this activity strengthen your technical or analytical thinking skills?**

**A:**
- It sharpened my ability to go from a mathematical model on paper to working code, and then back to practical interpretation of the results.
- I now instinctively think about robot performance in terms of distributions and confidence bounds, not just single deterministic numbers.
- This probabilistic mindset is valuable even in my current digital role, and even more so for ABB Robotics:
  - Designing software that characterizes arm repeatability under varying payloads
  - Building dashboards that show cycle time distributions, not just averages
  - Understanding why safety zones need probabilistic margins, not just fixed distances

---

**Q: How would you apply these skills in a future project or work situation?**

**A:**
- I would build digital-twin simulations that use probabilistic motion models to predict robotic arm behavior under different configurations — helping ABB Robotics teams test scenarios virtually before deploying on the factory floor.
- If I transition into a robotics software role, I could apply sensor model concepts to design navigation systems for mobile robots that handle reflective metal surfaces and dynamic human workers in ABB's factories.
- Even in my current digital role, I can apply these skills to build predictive maintenance systems that monitor when motion uncertainty crosses acceptable thresholds — flagging robots that need recalibration before they produce defective parts.

---

**Q: Which specific mobile robot sensing component (e.g., LiDAR, Camera, GPS etc.,) is most critical for tasks in your domain, based on what you learned?**

**A:**
- For mobile robots in an industrial setting like ABB's factories, **LiDAR** would be the most critical sensing component.
- Factory floors are structured environments with metallic surfaces, forklifts, and human workers — LiDAR handles all of these reliably.
- Unlike cameras, LiDAR works regardless of lighting conditions. Unlike GPS, it works indoors.
- After this assignment, I can clearly see how the beam-based sensor model maps to real industrial LiDAR behavior — reflective surfaces causing unexpected short readings, and long open corridors triggering max-range returns.

---

**Q: Based on the assignment, how much do you agree that integrating AI/ML is essential for the successful deployment of mobile robots in complex real-world scenarios?**

**A:**
- **5 (Strongly Agree)**
- After implementing these models, it is clear that probabilistic reasoning and ML-based perception are not optional — they are necessary for handling uncertainty, dynamic obstacles, and variability in real factory environments.
- Pure deterministic programming simply cannot cope with the complexity of shared human-robot workspaces.

---

**Q: How would you rate the effectiveness of the AI/ML approach learned in the assignment for solving a practical problem in your field?**

**A:**
- **4 out of 5**
- The probabilistic approach is highly effective for modeling motion and sensor uncertainty in industrial robotics settings.
- I rated it 4 rather than 5 because real ABB Robotics deployments also require integration with PLC systems, safety-rated controllers (like SafeMove), and industrial communication protocols — aspects that go beyond what this assignment covered, but are essential for anyone wanting to work in that space.

---

**Q: Please provide an example of a specific task in your domain where a mobile robot could significantly improve efficiency.**

**A:**
- A clear use case in ABB's robotics factories is **automated material handling between robotic arm welding cells**.
- Today, operators manually load metal parts onto carts and push them between IRB arm stations — it is slow and ties up skilled workers.
- An AMR with LiDAR-based navigation could:
  - Pick up finished parts from one robotic arm cell autonomously
  - Navigate across the factory floor, avoiding forklifts and workers in real time
  - Deliver parts to the next cell for assembly
- Estimated impact: ~60% reduction in inter-station transfer time, freeing operators for higher-value work like quality inspection and robot programming.
- From my digital perspective, I could contribute by building the fleet management software and route optimization algorithms for such a deployment.

---

*Note: Submit these responses through the official BITS email form linked in the assignment PDF.*
