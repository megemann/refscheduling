# Intramural Referee Scheduling Outline for Optimization

## Problem Description
At UMass, Intramurals is an ongoing activity, with many leagues constantly running throughout the year. These include smaller tournaments, like single-day cornhole, or larger leagues, like multi-week basketball. In some activities, like basketball, RecWell must hire referees to officiate games to foster a more professional environment. My job as a Program Assistant is to recruit, train, develop, and schedule these refs throughout the season for all the games we have participants for. However, facilitating the scheduling and operations of 150+ teams on 4 different days is an extremely time-consuming process, usually involving cross-referencing general availability with week-specific conflicts in a manual Excel spreadsheet. Additionally, later down the line it requires manual post-processing for payroll and attendance verification, which all respectively take time out of other people's day.

### Typical Job Workflow
1. Open leagues for participants; signees determine the number of games needed.
2. Get availability from interested referees during training, planning for general week-to-week scheduling.
3. Train referees and evaluate their skill level (usually returning referees are more suited to officiate harder games).
4. Week-to-week scheduling:
    - 4.1: Evaluate game cancellations and reschedulings (holidays, rain, etc.).
    - 4.2: Aggregate availability and week-to-week conflicts (exams, travel, etc.).
    - 4.3: Assign a relatively even amount of games to all officials based on availability and past reliability.
       -  More complicated information available in the '#Formulation' section
    - 4.4: Refactor weekly schedule to daily check-ins.
    - 4.5: Export daily check-ins to payroll calendar.
5. Conduct official and participants' playoff meeting to update availability along with tournament game structure.
6. Repeat 4-1 through 4-5 with extra consideration to effort and skill level, with double pay for semi-finals and finals given extra consideration for balance.

### Scale
My designation is basketball, which handles the following workload
- 40+ referees per season
- 70+ games per week during peak regular season
- Multiple skill levels (Top-Gun, Just Fun, Co-Rec)
- Time slots [6:30 pm, 7:30 pm, 8:30 pm, 9:30 pm]
- 4 Courts available per hour

### Current Challenges
- **Time-intensive**: Manual cross-referencing takes 4+ hours per week per sport
- **Error-prone**: Human scheduling mistakes lead to over/under-staffing
- **Inflexible**: Last-minute changes require extensive rework
- **Payroll complexity**: Manual post-processing for attendance verification which can lead to payroll issues
- **Referee satisfaction**: Uneven workload distribution and small shift length affects retention and morale
- **Scalability**: Current process doesn't scale well with league growth
- **Excel**: All scheduling requires manual input into standardized form templates, then transferred to daily templates

## Solution
My Goal is to create a **scheduling dashboard** that provides:
- Automated scheduling through optimization
- Customizable constraints based on week-to-week challenges
- Auto-Generated Excel filing for scheduling, availability, check-ins, and payroll.
- Simple visualizations of availabilty and game data to aid domain understanding
- Straight-forward directions to simplify the process for future employees
- Foster other integrations (Email, IT databases, Payroll)

### Planned Tech-Stack
- Streamlit: Dashboarding
- Pyomo: Framework definition
- Gurobi/GLPK: Linear solver
- Pandas: Tabular data processing
- xslxwriter: Excel Filings

### Implementation Roadmap
**Phase 1: Core Optimization Engine**
- Basic referee-game assignment optimization
- Simple availability constraints
- CSV/Excel I/O functionality

**Phase 2: Dashboard & User Interface**
- Streamlit dashboard for data input/visualization
- Template generation and file upload
- Schedule export functionality
- Base Generic Optimization framing and solving
  
## Domain Model

### Game Attributes
- Date
- Time
- Skill level (Top Gun, Just Fun, Co-Rec, Open, Womens, etc.)
- Teams involved
  - Skill level / Skill matchup of the teams
- Refs assigned to game
- number of refs required, number of refs wanted
- Location
- Playoff Round / Regular Season

### Ref Attributes
- Name
- Email
- T-Shirt size (for jerseys)
- Availability
- Participating Time (Have their own team)
- Phone #
- Skill / Experience Level
- Effort Level
- Year of Graduation
- Payroll Status

### Constraint Factors
- Games per Week balancing
- Availability
- Ensuring Game Coverage
- Skill Gap / Effort Gap reduction
- Reducing seperate shifts worked (favor large blocks of time)
- Double Pay Balancing (Playoffs)
- Pair lower-skill with higher-skill for training

## Algorithm Roadmap

### Phase 1
**Greedy Algorithm**
- Assign refs to games based on true availability only.
- Prioritize games with the fewest available refs.
- Schedule refs with the least hours assigned so far.
- Break ties by choosing refs with the least flexibility (fewest slots left).
- For games, break ties by picking times with the fewest available refs.
- No metadata or advanced constraints considered.
- Ensures balanced hours and prioritizes low-availability refs.
- No guarantee of optimality or termination.

### Phase 2
**Core Optimization**
- Model Games (W/ No Playoffs or Specific Skill Matchups)
- Model Refs (W/ Dummy Data for Payroll, and No Participation time or YOG)
- Testing and Weighting different Optimization Objectives:
  - Balancing Hours
  - Balancing Experience
  - Balancing Effort
  - Balancing Time Blocks (Favoring Large)
  - Balacing Lower-Higher skill pairs

## Formal Mathematical Model

### Phase 2: Constraints & Objective
**Hard Constraintss**
- No referee can be assigned to more than one game an hour
- No referee can work more than 8 hours in a night
- No referee can be scheduled more than 20 hours a week
- No referee can be scheduled during a time they have no availabilty
- Each scheduled game must have at least MIN_REFs assigned and no more than MAX_REFS assigned

**Soft Constraints**


**Optimization Criteria**

Weighted Combination of:
- Penalizing The difference of each referees hours away from the mean
- Awarding higher effort with more hours
- Awarding lesser number of continous time blocks
- Awarding Lower-Higher Skills pairs
- Penalizing lower mean skill score when compared to game score

### Mathmatical Equations
- Our input variable is binary, and has dimension $x_{i,j,k,l}$
  - 1 if Referee $i$ is working on day $j$ at hour $k$ on game $l$
  - 0 Otherwise
- Let $a_{i,j,k}$ denote a binary parameter, signifying if Referee $i$ is available on day $j$ at hour $k$
- Let $REx_{i}$ denote the experience level of Referee $i$
- Let $E_{i}$ denote the effort level of Referee $i$
- Let $GEx_{j,k,l}$ denote the difficulty level of the $l$th game on day $j$ at hour $k$.
- Let $G_{j,k,l}$ be a binary variable denoting if on day $j$ and at time $k$ that game $l$ is scheduled

**Hard Constraints:**  
> To differentiate between summation constraints and universal constraints, we use:
>- r $\in$ R to represent any referee r
> - d $\in$ D to represent any day d  
> - h $\in$ H to represent any hour h
> - g $\in$ G to represent any game g
> 
> Where summation constraints use $\sum$ over indices, and universal constraints use $\forall$ (for all)."

_No referee can be assigned to more than one game per hour:_

$$
\sum_{g \in G} x_{r,d,h,g} \leq 1 \qquad \forall r \in R,\ \forall d \in D,\ \forall h \in H
$$

_No referee can work more than 8 hours in a night:_
$$
\sum_{h \in H}\sum_{g \in G} x_{r,d,h,g} \leq 8 \qquad \forall r \in R,\ \forall d \in D
$$

_No referee can be scheduled more than 20 hours a week:_
$$
\sum_{d \in D}\sum_{h \in H}\sum_{g \in G} x_{r,d,h,g} \leq 20 \qquad \forall r \in R
$$

_No referee can be scheduled during a time they have no availabilty:_
$$ 
x_{r,d,h,g} \leq a_{r,d,h} \qquad \forall r \in R,\ \forall d \in D,\ \forall h \in H,\ \forall g \in G
$$

_Each game that is scheduled must have at least MIN_REF assigned and no more than MAX_REF assigned_:
$$
G_{d,h,g} \cdot \mathrm{MIN\_REF} \leq \sum_{r \in R}x_{r,d,h,g} \leq G_{d,h,g} \cdot \mathrm{MAX\_REF} \qquad \forall d \in D,\ \forall h \in H,\ \forall g \in G
$$

_Referees can only work games that are scheduled_:
$$
x_{r,d,h,g} \leq G_{d,h,g} \qquad \forall r \in R,\ \forall d \in D,\ \forall h \in H,\ \forall g \in G
$$

**User Constraints:** 

_All games assigned by user must be scheduled:_

For every user-assigned tuple $(r, d, h, g) \in A$:

$$
x_{r,d,h,g} = G_{d,h,g} \forall (r,d,h,g) \in A
$$

_Hours for a referee must be less than the user defined value:_

For every user-assigned bound $(r) \in \text{MAX\_HR}$:

$$
\sum_{d \in D} \sum_{h \in H} \sum_{g \in G} x_{r,d,h,g} \leq \text{MAX\_HR}_r \qquad \forall r \in R
$$

**Optimization Criteria:**

We start by defining useful metrics and functions

1. $N$ denotes the number of referees, 

2. $h_i = \sum_{j}\sum_{k}\sum_{l}x_{i,j,k,l}$, and $\bar{h} = \frac{1}{N}\sum_{i}h_i$ (hours for ref i, mean hours over all refs)

3. Define time blocks (The total number of shifts where there is no shift worked before it):
$$
blocks_r = \sum_{d \in D} \sum_{h \in H} start_{r,d,h}
$$

where $start_{r,d,h}$ is a binary variable indicating if referee $r$ starts a new time block at hour $h$ on day $d$, subject to:

$$
start_{r,d,h} \geq \sum_{g \in G} x_{r,d,h,g} - \sum_{g \in G} x_{r,d,h-1,g} \qquad \forall r \in R,\ \forall d \in D,\ \forall h \in H
$$

$$
start_{r,d,h} \leq \sum_{g \in G} x_{r,d,h,g} \qquad \forall r \in R,\ \forall d \in D,\ \forall h \in H
$$

$$
start_{r,d,h} \leq 1 - \sum_{g \in G} x_{r,d,h-1,g} \qquad \forall r \in R,\ \forall d \in D,\ \forall h \in H
$$

with $\sum_{g \in G} x_{r,d,h-1,g} = 0$ for the first hour of each day.

---

_Penalizing the mean absolute deviation of each referee's hours from the mean, only for referees not at their cap_

Let $C$ be the set of referees not at their cap:
$$
C = \{ i \in R \mid h_i < \text{MAX\_HR}_i \}
$$

Introduce auxiliary variables $d_i \geq 0$ for each $i \in C$ such that:
$$
d_i \geq h_i - \bar{h} \\
d_i \geq \bar{h} - h_i \\
\forall i \in C
$$

Then, the balancing penalty is:
$$
b(x) = \frac{1}{|C|} \sum_{i \in C} d_i
$$
_Awarding higher effort with more hours, only for referees not at their cap:_
$$
e(x) = \frac{1}{|C|}\sum_{i \in C}E_{i}h_i
$$

_Awarding lesser number of continuous time blocks:_
$$
tb(x) = \frac{1}{N}\sum_{r \in R} blocks_r = \frac{1}{N}\sum_{r \in R} \sum_{d \in D} \sum_{h \in H} start_{r,d,h}
$$

_Awarding Lower-Higher Skills pairs_
$$
p(x) = \frac{1}{L}\sum_{d \in D}\sum_{h \in H}\sum_{g \in G}\sum_{i<j} \Delta_{ij}\, y_{ij,d,h,g}
$$

- Where $L$ is the total number of games, $\Delta_{ij} = |REx_i - REx_j|$, and $y_{ij,d,h,g}$ is a binary variable indicating that referees $i$ and $j$ are both assigned to game $g$ at day $d$, hour $h$. This is subject to:

$$
y_{ij,d,h,g} \leq x_{i,d,h,g}, \quad y_{ij,d,h,g} \leq x_{j,d,h,g}, \quad y_{ij,d,h,g} \geq x_{i,d,h,g}+x_{j,d,h,g}-1 \qquad \forall i<j,\ \forall d,h,g
$$

_Penalizing lower mean skill score when compared to game score:_
$$
s(x) = -\frac{1}{L}\sum_{d \in D}\sum_{h \in H}\sum_{g \in G} u_{d,h,g}
$$

with 
$$
u_{d,h,g} \geq GEx_{d,h,g}\sum_{i \in R} x_{i,d,h,g} - \sum_{i \in R} REx_i \, x_{i,d,h,g}, \quad u_{d,h,g} \geq 0 \qquad \forall d \in D,\ \forall h \in H,\ \forall g \in G
$$

where `u_{d,h,g}` represents the **skill deficit penalty** - the amount by which the assigned referees' average experience falls short of the game's required difficulty level. When assigned referees have sufficient skill, `u_{d,h,g} = 0`. When they have insufficient skill, `u_{d,h,g} > 0` and contributes to the penalty.

**Final Objective Function**

$$
MAX \{obj(x) = w_1e(x) - w_2b(x) - w_3s(x) - w_4tb(x) + w_5p(x)\}
$$

where:
- `w_1` = weight for effort bonus (maximize high-effort referees)
- `w_2` = weight for hour balancing penalty (minimize hour imbalance) 
- `w_3` = weight for low skill penalty (minimize skill mismatches)
- `w_4` = weight for shift block penalty (minimize consecutive assignments)
- `w_5` = weight for skill combination bonus (maximize diverse skill pairs)

Note: some terms are divided by means for normalization, but are omitted to improve readability